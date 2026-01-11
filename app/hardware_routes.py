from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.hardware_service import trigger_gate
from app.models import Device, EventLog

bp = Blueprint('hardware', __name__)

@bp.route('/open-gate/<int:device_id>', methods=['POST'])
@login_required
def open_gate(device_id):
    device = Device.query.get_or_404(device_id)

    try:
        new_log = EventLog(
            event_type="MANUAL_OPEN",
            description=f"Gate opening - Triggered by {current_user.username}",
            device_id=device.id
        )
        db.session.add(new_log)
        db.session.commit()
    except Exception as e:
        print(f"Logging failed: {e}")

    success, message = trigger_gate(device_id)

    if success:
        return jsonify({"status": "success", "message": message}), 200
    else:
        return jsonify({"status": "error", "message": message}), 500
    
@bp.route('/status/gate/<int:device_id>')
def gate_status(device_id):
    device = Device.query.get_or_404(device_id)
    return render_template('partials/_gate_status.html', device=device)

@bp.route('/status/tamper/<int:device_id>')
def tamper_status(device_id):
    device = Device.query.get_or_404(device_id)
    return render_template('partials/_tamper_status.html', device=device)

@bp.route('/status/logs/<int:device_id>')
@login_required
def log_updates(device_id):
    device = Device.query.get_or_404(device_id)

    if device.owner != current_user:
        return "Access Denied", 403

    logs = device.logs.order_by(EventLog.timestamp.desc()).all()
    return render_template('partials/_log_rows.html', logs=logs)