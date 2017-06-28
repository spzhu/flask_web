from flask import render_template, redirect, request, url_for, flash
from ..email import send_email
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User
from .forms import LoginForm, RegistrationForm
from . import auth
from .. import db

@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed \
       and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, "账户确认邮件", 'auth/email/confirm', user=current_user, token=token)
    flash("确认邮件已发送到邮箱，请确认。")
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您的账号已激活。')
    else:
        flash("确认链接非法或已过有效期。")
    return redirect(url_for('main.index'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, "账户确认邮件", 'auth/email/confirm', user=user, token=token)
        flash("注册成功！请前往注册邮箱激活账号。")
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)
