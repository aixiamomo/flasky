# coding=utf-8
from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()  # 使用HTTPAuth认证


@auth.verify_password
def verify_password(email, password):
    """在API蓝本中使用的用户认证方法"""
    if email == '':
        g.current_user = AnonymousUser()  # 匿名对象的实例
        return True
    user = User.query.filter_by(email=email).first()
    if not user:
        return False
    g.current_user = user  # 把用户保存在全局对象g里
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    """401错误处理程序"""
    return unauthorized('Invalid credentials')  # 传递给message


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous:
        return forbidden('Unconfirmed account')
