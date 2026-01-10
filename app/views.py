from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User, Device, Invitation, UserDeviceAccess, EventLog
from app.forms import LoginForm, RegistrationForm
from urllib.parse import urlsplit


bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html', title="Home")

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.dashboard'))
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get devices the user owns OR has guest access to
    owned = current_user.owned_devices.all()
    guest_links = current_user.get_accessible_devices()
    all_devices = list(set(owned + guest_links)) # Combine and remove duplicates
    
    # Get the 10 most recent logs for all of the user's devices
    device_ids = [d.id for d in all_devices]
    recent_logs = EventLog.query.filter(EventLog.device_id.in_(device_ids))\
        .order_by(EventLog.timestamp.desc()).limit(10).all()

    return render_template('dashboard.html', 
                           devices=all_devices, 
                           logs=recent_logs, 
                           title="Dashboard")

@bp.route('/devices')
@login_required
def manage_devices():
    # No extra query needed: Jinja uses current_user.owned_devices
    return render_template('devices.html', title='My Devices')

@bp.route('/invites')
@login_required
def invites():
    # Pass the Invitation model class so Jinja can query it
    return render_template('invites.html', title='Invitations', Invitation=Invitation)

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='User Profile')