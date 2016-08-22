#!/usr/bin/env python
# coding=utf-8
import os

from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db  # 导入工厂函数和数据库实例
from app.models import User, Role, Permission, Post, Follow  # 导入User,Role模型


COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

# 如果定义了环境变量，则从中读取配置名，否则使用默认配置
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


# 定义一个回调函数
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role,
                Permission=Permission, Post=Post, Follow=Follow)  # 生成一个字典
manager.add_command("shell", Shell(make_context=make_shell_context))  # 为shell添加一个上下文
manager.add_command('db', MigrateCommand)  # 添加数据库迁移命令，附加到manager上
manager.add_command('runserver', Server('127.0.0.1', port='2000'))


# 启用单元测试的命令
@manager.command  # 装饰器自定义命令
def test():  # 装饰函数名就是命令名
    """Run the unit tests."""  # 文档字符会显示在帮助信息中
    import unittest  # 调用unittest包提供测试运行函数
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """部署到生产环境"""
    from flask_migrate import upgrade
    from app.models import Role, User

    # 把数据库迁移到最新修订版本
    upgrade()

    # 创建用户角色
    Role.insert_roles()

    # 让所有的用户都关注自己
    User.add_self_follows()


if __name__ == '__main__':
    manager.run()
