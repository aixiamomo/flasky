# coding=utf-8
import unittest  # 单元测试
from flask import current_app  # 程序上下文：当前激活程序的实例
from app import create_app, db # 工厂函数，数据库模型实例


class BasicsTestCase(unittest.TestCase):  # 基础 测试 实例
    """
    setUp(),tearDown()方法每次测试前后都会调用
    test_开头的函数作为测试执行
    """
    def setUp(self):  # 创建一个测试环境
        self.app = create_app('testing')  # 构造测试实例
        self.app_context = self.app.app_context()  # 激活程序上下文
        self.app_context.push()  # 入栈
        db.create_all()  # 根据模型类创建数据库

    def tearDown(self):  # 拆毁
        db.session.remove()  # 移除数据库会话
        db.drop_all()  # 删除数据库
        self.app_context.pop()  # 出栈

    def test_app_exists(self):
        self.assertFalse(current_app is None)  # assertFalse()核实状态

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
