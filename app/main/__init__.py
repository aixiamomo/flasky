# coding=utf-8
# 创建蓝本
from flask import Blueprint

main = Blueprint('main', __name__)  # 实例化,参数：蓝本名，蓝本所在的包或者模块

from . import views, errors  # 从当前目录下的包中导入views,errors模块，并与蓝本关联起来
