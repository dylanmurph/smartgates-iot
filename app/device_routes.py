from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Device

bp = Blueprint('devices', __name__)

@bp.route('/devices')
@login_required
def list_devices():
    return render_template('devices.html', title='My Devices')


@bp.route('/devices/add', methods=['GET', 'POST'])
@login_required
def add_device():
    pass

@bp.route('/devices/<int:device_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_device(device_id):
    pass

@bp.route('/devices/<int:device_id>/delete', methods=['POST'])
@login_required
def delete_device(device_id):
    pass