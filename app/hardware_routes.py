from flask import Blueprint, jsonify
from app.hardware_service import trigger_gate

bp = Blueprint('hardware', __name__)

@bp.route('/open-gate', methods=['POST'])
def open_gate():
    success, message = trigger_gate()

    if success:
        return jsonify({"status": "success", "message": message}), 200
    else:
        return jsonify({"status": "error", "message": message}), 500