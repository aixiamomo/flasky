# coding=utf-8
from flask import jsonify
from . import api
from app.exceptions import ValidationError


def forbidden(message):
    """403status_code状态码的处理程序"""
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    """只要抛出了指定的异常，就会调用被修饰的函数"""
    return bad_request(e.args[0])


"""生成各种状态码的辅助函数，供视图函数调用"""