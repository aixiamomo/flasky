# coding=utf-8
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user  # 实现登录路由
from flask_login import logout_user, login_required  # 实现登出路由
from flask_login import current_user  # 当前用户

from . import auth  # 从这一层的__init__.py 导入蓝本实例
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm
from ..email import send_email


# 用钩子过滤未确认的用户
@auth.before_app_request
def before_request():  # P94，拦截请求
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':  # 用户已登录/用户未确认/请求端点不在蓝本里
        return redirect(url_for('auth.unconfirmed'))  # 显示一个确认账户相关信息的界面


# 显示给未确认用户的页面
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


# 登录
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


# 登出
@auth.route('/logout')
@login_required
def logout():
    logout_user()  # 删除并重设用户会话
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


# 注册
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()  # p92
        token = user.generate_confirmation_token()  # 生成Token
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


# 确认用户
@auth.route('/confirm/<token>')
@login_required  # 保护路由，用户点击URL需要先登录，然后执行这个视图函数 P93
def confirm(token):
    if current_user.confirmed:  # 当前登录用户是否确认过
        return redirect(url_for('main.index'))
    if current_user.confirm(token):  # 验证通过
        flash('You have confirmed your account. Thanks')
    else:  # token过期，验证失败
        flash('The confirmation link is invalid or has expired')
    return redirect(url_for('main.index'))


# 重新发送账户确认邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

