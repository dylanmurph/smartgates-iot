from flask import Blueprint, render_template, redirect, url_for, flash, request
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
    devices = current_user.get_viewable_devices()
    
    if not devices:
        return render_template('dashboard.html', 
                               title='Dashboard', 
                               devices=[], 
                               device=None, 
                               is_owner=False)

    device_id = request.args.get('device_id', type=int)
    if device_id:
        device = next((d for d in devices if d.id == device_id), devices[0])
    else:
        device = devices[0]

    is_owner = (device.owner == current_user)

    return render_template('dashboard.html', 
                           title="Dashboard",
                           device=device,
                           devices=devices,
                           is_owner=is_owner) 

@bp.route('/profile')
@login_required
def profile():
    all_devices = current_user.get_viewable_devices()
    device = all_devices[0] if all_devices else None
    return render_template('profile.html', title='User Profile', device=device)

@bp.route('/logs/<int:device_id>')
@login_required
def view_logs(device_id):
    device = Device.query.get_or_404(device_id)

    is_owner = (device.owner == current_user)

    if is_owner:
        logs = device.logs.order_by(EventLog.timestamp.desc()).all()
    else:
        logs = []

    return render_template('logs.html', 
                           device=device, 
                           logs=logs, 
                           is_owner=is_owner)