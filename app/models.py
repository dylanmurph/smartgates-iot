from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login

import string
import secrets

def get_utc_now():
    return datetime.now(timezone.utc)

def generate_device_id():
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(4))

# --- USER DEVICES (Association Table) ---
class UserDeviceAccess(db.Model):
    __tablename__ = 'user_device_access'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), primary_key=True)
    assigned_at = db.Column(db.DateTime, default=get_utc_now)
    
    user = db.relationship("User", back_populates="access_links")
    device = db.relationship("Device", back_populates="access_links")

# --- USERS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=get_utc_now)
    
    
    owned_devices = db.relationship('Device', back_populates='owner', lazy='dynamic')
    access_links = db.relationship('UserDeviceAccess', back_populates='user', lazy='dynamic')
    sent_invites = db.relationship('Invitation', back_populates='inviter', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_accessible_devices(self):
        return [link.device for link in self.access_links]

    def get_viewable_devices(self):
        """Returns ALL devices this user can see (Owned + Guest Access)."""
        owned = self.owned_devices.all()
        guests = [link.device for link in self.access_links]
        return list(set(owned + guests))

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# --- DEVICES ---
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    unique_id = db.Column(db.String(64), unique=True, default=generate_device_id)
    is_online = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_gate_open = db.Column(db.Boolean, default=False)
    is_tamper_active = db.Column(db.Boolean, default=False)
    
    owner = db.relationship('User', back_populates='owned_devices')
    access_links = db.relationship('UserDeviceAccess', back_populates='device', cascade="all, delete-orphan")
    logs = db.relationship('EventLog', back_populates='device', lazy='dynamic')
    invites = db.relationship('Invitation', back_populates='device', cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        super(Device, self).__init__(**kwargs)

        if self.owner:
            self.add_owner_to_access(self.owner)
        elif self.owner_id:
            owner_user = User.query.get(self.owner_id)
            if owner_user:
                self.add_owner_to_access(owner_user)

    def add_owner_to_access(self, user_obj):
        from app.models import UserDeviceAccess
        new_access = UserDeviceAccess(user=user_obj, device=self)
        db.session.add(new_access)

    def __repr__(self):
        return f'<Device {self.name}>'

# --- LOGS ---
class EventLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50))
    description = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=get_utc_now)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    
    device = db.relationship('Device', back_populates='logs')

    def __repr__(self):
        return f'<Log {self.event_type}>'
    
# --- INVITATIONS ---
class Invitation(db.Model):
    __tablename__ = 'invitation'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    inviter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    invitee_email = db.Column(db.String(120))
    token = db.Column(db.String(64), unique=True)
    status = db.Column(db.String(20), default='pending') 
    created_at = db.Column(db.DateTime, default=get_utc_now)

    device = db.relationship('Device', back_populates='invites')
    inviter = db.relationship('User', back_populates='sent_invites')

    def __repr__(self):
        return f'<Invitation {self.invitee_email} for {self.device_id}>'