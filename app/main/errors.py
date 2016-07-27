# coding=utf-8
from flask import render_template
from . import main  # 从当前目录下的__init__.py中导入main, 即导入蓝本实例


@main.app_errorhandler(404)  # 蓝本中使用app_errorhandler代替errorhandler，注册全局的错误处理程序
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500