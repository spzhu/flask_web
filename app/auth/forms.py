from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login')

class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    username = StringField('Username', validators=[Required(), Length(1,64), \
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名只能由字母，数字，点和下划线组成,且以字母开头.')])
    password = PasswordField('Password', validators=[Required(), EqualTo('password2', \
            message='两次输入密码不匹配。')])
    password2 = PasswordField('Confirm Password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('电子邮件地址已存在。')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

class PasswordChangeForm(Form):
    old_password = PasswordField("旧密码", validators=[Required()])
    new_password = PasswordField("新密码", validators=[Required()])
    new_password2 = PasswordField("重新输入新密码", validators=[Required(), \
            EqualTo('new_password', message="两次输入的密码不匹配。")])
    submit = SubmitField("提交")

class ResetEmailRequestForm(Form):
    email = StringField("原电子邮件", validators=[Required(), Length(1,64), Email()])
    new_email = StringField("新电子邮件", validators=[Required(), Length(1,64), Email()])
    password = PasswordField("密码", validators=[Required()])
    submit = SubmitField("修改电子邮件")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('未知的电子邮件地址')


class ResetPasswordRequestForm(Form):
    email = StringField("电子邮件", validators=[Required(), Length(1,64), Email()])
    submit = SubmitField("重置密码")

class ResetPasswordForm(Form):
    email = StringField("注册邮箱", validators=[Required(), Length(1,64), Email()])
    new_password = PasswordField("新密码", validators=[Required()])
    new_password2 = PasswordField("再次输入新密码", validators=[Required(), \
            EqualTo('new_password', message="两次输入密码不一致。")])
    submit = SubmitField("重置密码")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first is None:
            raise ValidationError('未知的电子邮件地址')
