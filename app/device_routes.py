from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Device, User, UserDeviceAccess
from app.forms import AddDeviceForm, EditDeviceForm, AddGuestForm

bp = Blueprint("devices", __name__)

@bp.route("/devices")
@login_required
def list_devices():
    owned_devices = current_user.owned_devices.all()
    
    all_accessible = current_user.get_accessible_devices()
    shared_devices = [d for d in all_accessible if d.owner_id != current_user.id]

    device = owned_devices[0] if owned_devices else (shared_devices[0] if shared_devices else None)
    
    add_form = AddDeviceForm()
    edit_form = EditDeviceForm()
    guest_form = AddGuestForm()

    return render_template(
        "devices.html",
        title="My Devices",
        device=device,
        owned_devices=owned_devices,   
        shared_devices=shared_devices, 
        add_form=add_form,
        edit_form=edit_form,
        guest_form=guest_form,
    )

@bp.route('/devices/add', methods=['POST'])
@login_required
def add_device():
    form = AddDeviceForm()
    if form.validate_on_submit():
        dev = Device(name=form.device_name.data, owner=current_user)
        db.session.add(dev)
        db.session.commit()
        flash(f'Device "{dev.name}" added successfully!', 'success')
    else:
        flash('Error adding device.', 'danger')
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
    return redirect(url_for('devices.list_devices'))

@bp.route('/devices/<int:device_id>/delete', methods=['POST'])
@login_required
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    if device.owner != current_user:
        flash('You do not have permission to delete this device.', 'danger')
        return redirect(url_for('devices.list_devices'))

    db.session.delete(device)
    db.session.commit()
    flash('Device deleted.', 'success')
    return redirect(url_for('devices.list_devices'))

@bp.route("/devices/<int:device_id>/add-guest", methods=["POST"])
@login_required
def add_guest(device_id):
    device = Device.query.get_or_404(device_id)
    form = AddGuestForm()

    if device.owner != current_user:
        flash("Only the device owner can add guests.", "danger")
        return redirect(url_for("devices.list_devices"))

    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        target_user = User.query.filter_by(email=email).first()

        if target_user:
            existing = UserDeviceAccess.query.filter_by(user_id=target_user.id, device_id=device.id).first()
            is_owner = target_user == current_user

            if not existing and not is_owner:
                new_access = UserDeviceAccess(user=target_user, device=device)
                db.session.add(new_access)
                db.session.commit()
                print(f"Access granted to {email}")
            else:
                print(f"User {email} already has access or is owner.")
        else:
            print(f"User {email} NOT FOUND in database.")

        flash(f'If an account exists for "{email}", access has been granted.', "info")

    else:
        flash("Invalid email address format.", "danger")

    return redirect(url_for("devices.list_devices"))

@bp.route('/devices/<int:device_id>/leave', methods=['POST'])
@login_required
def leave_device(device_id):
    device = Device.query.get_or_404(device_id)

    if device.owner == current_user:
        return redirect(url_for('devices.list_devices'))

    access_link = UserDeviceAccess.query.filter_by(user_id=current_user.id, device_id=device.id).first()
    
    if access_link:
        db.session.delete(access_link)
        db.session.commit()
        flash(f'You have removed "{device.name}" from your account.', 'success')
    else:
        flash('You do not have access to this device.', 'info')

    return redirect(url_for('devices.list_devices'))