#!/usr/bin/env python
# coding=utf-8
import os
from app import create_app, db  # 导入工厂函数和数据库实例
from app.models import User, Role  # 导入User,Role模型
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


# 如果定义了环境变量，则从中读取配置名，否则使用默认配置
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


# 定义一个回调函数
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)  # 生成一个字典
manager.add_command("shell", Shell(make_context=make_shell_context))  # 为shell添加一个上下文
manager.add_command('db', MigrateCommand)  # 添加数据库迁移命令，附加到manager上


# 启用单元测试的命令
@manager.command  # 装饰器自定义命令
def test():  # 装饰函数名就是命令名
    """Run the unit tests."""  # 文档字符会显示在帮助信息中
    import unittest  # 调用unittest包提供测试运行函数
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
