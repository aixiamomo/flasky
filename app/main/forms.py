# coding=utf-8
from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp


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
    email = StringField('Email', validators=[Email(), DataRequired(), Length(1,64)])
    username = StringField('Username', validators=[
        DataRequired(), Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                             'Usernames must have only letters, '
                                             'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)  # 下拉列表
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')
