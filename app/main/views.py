from flask import render_template, session, redirect, url_for, current_app, abort
from .. import db
from ..models import User, Permission
from ..decorators import admin_required, permission_required
from flask_login import login_required
from ..email import send_email
from . import main
from .forms import NameForm


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', name=session.get('name'), \
                           known=session.get('known', False))

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)

@main.route('/admin')
@login_required
@admin_required
def for_admin_only():
    return render_template('admin.html')

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return render_template('moderator.html')

