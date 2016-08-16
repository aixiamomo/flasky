# coding=utf-8
from flask import render_template, request, jsonify
from . import main  # 从当前目录下的__init__.py中导入main, 即导入蓝本实例


@main.app_errorhandler(403)
def forbidden(e):
    """使用HTTP内容协商处理错误"""
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:  # 请求首部绝对客户端期望接受的响应格式：json/accept
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('403.html'), 403


@main.app_errorhandler(404)  # 蓝本中使用app_errorhandler代替errorhandler，注册全局的错误处理程序
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_json:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('500.html'), 500
