from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models import EventLog, Device

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html', title="Home")

@bp.route('/dashboard')
@login_required
def dashboard():
    # 1. Get all devices user can see (Owned + Guest)
    all_devices = current_user.get_viewable_devices()
    
    # 2. Pick the first one as the "Active" device for the navbar/dashboard
    device = all_devices[0] if all_devices else None

    # 3. Optional: Get logs only if we have devices
    recent_logs = []
    if device:
        recent_logs = device.logs.order_by(EventLog.timestamp.desc()).limit(10).all()

    return render_template('dashboard.html', 
                           device=device,        # Defines the active device
                           devices=all_devices,  # List for dropdowns (future use)
                           logs=recent_logs, 
                           title="Dashboard")

@bp.route('/profile')
@login_required
def profile():
    # We pass a device just so the navbar Logs link knows where to point (if any exist)
    all_devices = current_user.get_viewable_devices()
    device = all_devices[0] if all_devices else None
    return render_template('profile.html', title='User Profile', device=device)

@bp.route('/logs/<int:device_id>')
@login_required
def view_logs(device_id):
    device = Device.query.get_or_404(device_id)
    
    if device not in current_user.get_viewable_devices():
        flash("You do not have access to this device's logs.")
        return redirect(url_for('main.dashboard'))

    logs = device.logs.order_by(EventLog.timestamp.desc()).limit(20).all()
    return render_template('logs.html', device=device, logs=logs)