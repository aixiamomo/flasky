# coding=utf-8
import os
from app import create_app, db  # 导入工厂函数和数据库实例
from app.models import User, Role  # 导入User,Role模型
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


app = create_app(os.getemv)
