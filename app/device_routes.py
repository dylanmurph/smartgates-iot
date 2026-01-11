from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Device
from app.forms import AddDeviceForm

bp = Blueprint('devices', __name__)

@bp.route('/devices')
@login_required
def list_devices():
    all_devices = current_user.get_viewable_devices()
    device = all_devices[0] if all_devices else None
    form = AddDeviceForm() 
    return render_template('devices.html', title='My Devices', device=device, form=form)

@bp.route('/devices/add', methods=['POST'])
@login_required
def add_device():
    form = AddDeviceForm()
    
    if form.validate_on_submit():
        new_device = Device(
            name=form.device_name.data,
            owner=current_user
        )

        db.session.add(new_device)
        db.session.commit()
        
        flash(f'Device Added! ID: {new_device.unique_id}', 'success')
    else:
        flash('Error: Device name is required.', 'danger')
        
    return redirect(url_for('devices.list_devices'))

@bp.route('/devices/<int:device_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_device(device_id):
    pass

@bp.route('/devices/<int:device_id>/delete', methods=['POST'])
@login_required
def delete_device(device_id):
    pass