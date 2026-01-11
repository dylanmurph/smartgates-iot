from flask import Blueprint, render_template, redirect, url_for
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
    owned = current_user.owned_devices.all()
    guest_links = current_user.get_accessible_devices()
    all_devices = list(set(owned + guest_links))
    
    device_ids = [d.id for d in all_devices]
    if device_ids:
        recent_logs = EventLog.query.filter(EventLog.device_id.in_(device_ids))\
            .order_by(EventLog.timestamp.desc()).limit(10).all()
    else:
        recent_logs = []

    return render_template('dashboard.html', 
                           devices=all_devices, 
                           logs=recent_logs, 
                           title="Dashboard")

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='User Profile')

@bp.route('/logs/<int:device_id>')
def view_logs(device_id):
    device = Device.query.get_or_404(device_id)
    logs = device.logs.order_by(EventLog.timestamp.desc()).limit(20).all()
    return render_template('logs.html', device=device, logs=logs)