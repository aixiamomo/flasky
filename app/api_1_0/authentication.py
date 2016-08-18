# coding=utf-8
from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()  # 使用HTTPAuth认证


@api.route('/token')
def get_token():
    """
    服务器生成令牌，发送给客户端。
    """
    if g.current_user.is_anonymous() or g.token_used:  # 当用户是匿名用户，或者token被使用过之后
        return unauthorized('Invalid credentials')  # 返回401
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})  # 生成json格式的令牌


@auth.verify_password
def verify_password(email_or_token, password):
    """
    在API蓝本中使用的用户认证方法，可以认证包含密码，或者令牌的请求。
    客户端发送密码或令牌给服务器进行验证
    """
    if email_or_token == '':
        g.current_user = AnonymousUser()  # 匿名对象的实例
        return True
    if password == '':
        g.current_user = User.verfy_auth_token(email_or_token)
        g.token_used = True  # 添加一个变量标记token有没使用，给视图函数区分用
        return g.current_user is not None  # 认证成功返回True
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user  # 把用户保存在全局对象g里，这样视图函数才能访问
    g.token_used = False
    return user.verify_password(password)  # 密令正确，验证回调函数返回True,密令错误，服务器会返回401状态码


@auth.error_handler
def auth_error():
    """401错误处理程序"""
    return unauthorized('Invalid credentials')  # 自定义这个错误响应，使与API里的其他错误响应一致


@api.before_request  # 每次api请求前都会执行
@auth.login_required  # 验证是否登陆
def before_request():
    # if not g.current_user.is_anonymous and \
    #         not g.current_user.confirmed:  # 已经通过认证，但是没有确认账户的用户
    #     return forbidden('Unconfirmed account')
    pass

