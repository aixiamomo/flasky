# coding=utf-8
from . import db  # 在当前目录下导入db


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')  # 构造关系，返回User模型中，与角色关联的用户组成的列表

    def __repr__(self):
        return '<Role {}'.format(self.name)  # 返回一个可读性的字符串表示模型，测试时候使用


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=Truem, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User {}'.format(self.name)