from flask import render_template, redirect, request, url_for, flash
from ..email import send_email
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User
from .forms import LoginForm, RegistrationForm, PasswordChangeForm, ResetPasswordForm, \
        ResetPasswordRequestForm, ResetEmailRequestForm
from . import auth
from .. import db

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
           and request.endpoint[:5] != 'auth.' \
           and request.endpoint != 'static':
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

@auth.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            flash("密码修改成功。")
            return redirect(url_for('main.index'))
        else:
            flash("密码错误。")
    return render_template('auth/change_password.html', form = form)

@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_password_token()
            send_email(user.email, "重置密码", 'auth/email/reset_password', \
                      user=user, token=token, next=request.args.get('next'))
        flash("重置密码确认邮件已发送到您的邮箱，请确认。")
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.new_password.data):
            flash("密码已重置。")
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset_email', methods=['GET', 'POST'])
def reset_email_request():
    form = ResetEmailRequestForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.new_email.data
            token = current_user.generate_reset_emial_token(new_email)
            send_email(new_email, "更换电子邮件地址", "auth/email/reset_email", \
                      user=current_user, token=token)
            flash("请前往新电子邮箱确认邮件，完成后续工作。")
            return redirect(url_for('main.index'))
        else:
            flash("用户密码错误。")
    return render_template('auth/reset_email.html', form=form)

@auth.route('/reset_email/<token>')
@login_required
def reset_email(token):
    if current_user.reset_email(token):
        flash("电子邮件更换成功。")
    else:
        flash("电子邮件更换出错，请再次尝试。")
    return redirect(url_for('main.index'))
    


