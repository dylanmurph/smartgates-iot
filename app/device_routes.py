from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Device, EventLog
from app.forms import AddDeviceForm, EditDeviceForm

bp = Blueprint('devices', __name__)

@bp.route('/devices')
@login_required
def list_devices():
    all_devices = current_user.get_viewable_devices()
    device = all_devices[0] if all_devices else None
    add_form = AddDeviceForm()
    edit_form = EditDeviceForm()
    return render_template('devices.html', title='My Devices', device=device, add_form=add_form, edit_form=edit_form)

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

@bp.route('/devices/<int:device_id>/edit', methods=['POST'])
@login_required
def edit_device(device_id):
    device = Device.query.get_or_404(device_id)
    
    if device.owner != current_user:
        flash('You do not have permission to edit this device.', 'danger')
        return redirect(url_for('devices.list_devices'))

    form = EditDeviceForm()
    if form.validate_on_submit():
        device.name = form.device_name.data
        db.session.commit()
        flash('Device renamed successfully.', 'success')
    else:
        flash('Error: Invalid name provided.', 'danger')
        
    return redirect(url_for('devices.list_devices'))

@bp.route('/devices/<int:device_id>/delete', methods=['POST'])
@login_required
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    
    # Security: Ensure only the owner can delete
    if device.owner != current_user:
        flash('You do not have permission to delete this device.', 'danger')
        return redirect(url_for('devices.list_devices'))

    try:
        # 1. Manually delete logs (Because your model relationship doesn't have cascade="all,delete")
        EventLog.query.filter_by(device_id=device.id).delete()
        
        # 2. Delete the device
        # Note: AccessLinks and Invitations WILL delete automatically because 
        # you defined cascade="all, delete-orphan" in models.py for them.
        db.session.delete(device)
        db.session.commit()
        
        flash('Device and all associated logs deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting device: {str(e)}', 'danger')

    return redirect(url_for('devices.list_devices'))