from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import Invitation, UserDeviceAccess

bp = Blueprint('invites', __name__)

@bp.route('/invites')
@login_required
def manage_invites():
    all_devices = current_user.get_viewable_devices()
    device = all_devices[0] if all_devices else None
    return render_template('invites.html', title='Invitations', Invitation=Invitation, device=device)

@bp.route('/devices/<int:device_id>/invite', methods=['GET', 'POST'])
@login_required
def send_invite(device_id):
    pass

@bp.route('/invites/<int:invite_id>/accept', methods=['POST'])
@login_required
def accept_invite(invite_id):
    pass

@bp.route('/invites/<int:invite_id>/revoke', methods=['POST'])
@login_required
def revoke_access(invite_id):
    pass