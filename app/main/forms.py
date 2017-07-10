from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from flask_pagedown.fields import PageDownField
from wtforms.validators import Required, Length, Email, Regexp
from ..models import User, Role


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    name = StringField('真实姓名', validators=[Length(0,64)])
    location = StringField('所在地', validators=[Length(0,64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

class EditProfileAdminForm(FlaskForm):
    email = StringField('电子邮件', validators=[Required(), Length(1,64), Email()])
    username = StringField('用户名', validators=[Required(), Length(1,64), \
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名只能由字母，数字，点和下划线组成,且以字母开头.')])
    confirmed = BooleanField('账户激活状态')
    role = SelectField('用户类别', coerce=int)
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('所在地', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('该电子邮件已经注册过。')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用。')

class PostForm(FlaskForm):
    title = TextAreaField('文章标题', validators=[Required()])
    body = PageDownField("文章内容", validators=[Required()])
    submit = SubmitField("提交")
