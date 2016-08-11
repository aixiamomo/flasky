# coding=utf-8
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown

from config import config


# 尚未初始化程序实例app=Flask(__name__),所以创建扩展对象的时候没有传入参数
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.session_protection = 'strong'  # 不同属性表示不同安全等级。
login_manager.login_view = 'auth.login'  # login_view属性设置登录页面的端点


# 工厂函数
def create_app(config_name):  # 参数为config.py里字典的key
    # 创建程序实例并配置config
    app = Flask(__name__)  # 初始化程序实例
    app.config.from_object(config[config_name])  # from_object是flask实例的内置方法，导入配置对象，配置对象从字典查询

    # 初始化扩展
    bootstrap.init_app(app)  # 在之前创建的扩展对象上调用init_app()完成初始化
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # 附加路由和自定义的错误页面
    from .main import main as main_blueprint  # 从当前目录下的main目录下的__init__导入蓝本实例并重命名
    app.register_blueprint(main_blueprint)  # 注册（激活）蓝图

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')  # 使用参数，注册后蓝本中定义的所有路由都会加上指定的前缀

    return app  # 工厂函数返回创建的程序实例
