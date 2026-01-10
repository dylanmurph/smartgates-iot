from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

def get_utc_now():
    return datetime.now(timezone.utc)

# --- USER DEVICES ---
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

    access_links = db.relationship('UserDeviceAccess', back_populates='user', cascade="all, delete-orphan")
    owned_devices = db.relationship('Device', back_populates='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def get_accessible_devices(self):
        return [link.device for link in self.access_links]

    def __repr__(self):
        return f'<User {self.username}>'

# --- DEVICES ---
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    unique_id = db.Column(db.String(64), unique=True)
    is_online = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    owner = db.relationship('User', back_populates='owned_devices')
    access_links = db.relationship('UserDeviceAccess', back_populates='device', cascade="all, delete-orphan")
    logs = db.relationship('EventLog', back_populates='device', lazy='dynamic')

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
    
from app import login
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))