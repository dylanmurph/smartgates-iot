from flask import Blueprint, jsonify
from app.hardware_service import trigger_gate
from datetime import datetime
from app.models import Device, EventLog
from flask import render_template

bp = Blueprint('hardware', __name__)

@bp.route('/open-gate/<int:device_id>', methods=['POST'])
def open_gate(device_id):
    success, message = trigger_gate(device_id)

    if success:
        return jsonify({"status": "success", "message": message}), 200
    else:
        return jsonify({"status": "error", "message": message}), 500
    
@bp.route('/status/gate/<int:device_id>')
def gate_status(device_id):
    device = Device.query.get_or_4_04(device_id)
    return render_template('partials/_gate_status.html', device=device, now=datetime.now())

@bp.route('/status/tamper/<int:device_id>')
def tamper_status(device_id):
    device = Device.query.get_or_4_04(device_id)
    return render_template('partials/_tamper_status.html', device=device)

@bp.route('/status/logs/<int:device_id>')
def log_updates(device_id):
    device = Device.query.get_or_404(device_id)
    # Get the latest 10 logs
    logs = device.logs.order_by(EventLog.timestamp.desc()).limit(10).all()
    return render_template('partials/_log_rows.html', logs=logs)