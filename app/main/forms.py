# coding=utf-8
from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, TextAreaField, \
    BooleanField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp

from ..models import Role, User


class NameForm(Form):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    """用户级别的资料编辑表单"""
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    """管理员级别的资料编辑表单"""
    email = StringField('Email', validators=[Email(), DataRequired(), Length(1, 64)])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must have only letters, '
                                              'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)  # 下拉列表

    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]  # 根据指定条件对原查询结果进行排序，返回一个新查询
        self.user = user  # 被编辑的用户

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(Form):
    """博客文章表单"""
    body = PageDownField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')
