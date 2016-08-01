# coding=utf-8
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user  # 实现登录路由
from flask_login import logout_user, login_required  # 实现登出路由

from . import auth  # 从这一层的__init__.py 导入蓝本实例
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # 验证表单数据
        user = User.query.filter_by(email=form.email.data).first()  # 查询数据库
        if user is not None and user.verify_password(form.password.data):  # 尝试登录：检验对象和密码
            login_user(user, form.remember_me.data)  # 标记为已登录
            return redirect(request.args.get('next') or url_for('main.index'))  # 重定向至主页
        flash('Invalid username or password')  # 验证失败
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()  # 删除并重设用户会话
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        flash('You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

