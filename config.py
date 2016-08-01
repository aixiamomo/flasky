# coding=utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))  # 返回当前程序目录的绝对路径


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'  # 密钥
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 每次请求结束提交数据改动
    FLASKY_MAIL_SUBJECT_PREFIX = '[FLASKY]'  # 主题前缀
    FLASKY_MAIL_SENDER = 'Flasky Admin qq920534583@gmail.com'  # 发件人
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')  # 收件管理员
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
            pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USER_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')  # 将多个路径组合后返回


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}