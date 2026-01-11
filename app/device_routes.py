from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Device, User, UserDeviceAccess
from app.forms import AddDeviceForm, EditDeviceForm, AddGuestForm

bp = Blueprint("devices", __name__)


@bp.route("/devices")
@login_required
def list_devices():
    all_devices = current_user.get_viewable_devices()
    device = all_devices[0] if all_devices else None
    add_form = AddDeviceForm()
    edit_form = EditDeviceForm()
    guest_form = AddGuestForm()

    return render_template(
        "devices.html",
        title="My Devices",
        device=device,
        devices=all_devices,
        add_form=add_form,
        edit_form=edit_form,
        guest_form=guest_form,
    )


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
