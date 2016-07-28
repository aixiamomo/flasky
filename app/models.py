# coding=utf-8
from . import db  # 在当前目录下导入db
from werkzeug.security import generate_password_hash, check_password_hash  # 加入密码散列


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
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}'.format(self.name)

    @property  # 只写属性
    def password(self):  # 读取password会报错
        raise AttributeError('password is not a readable attribute')

    @password.setter  # 设定值
    def password(self, password):
        self.password_hash = generate_password_hash(password)  # 调用生成hash赋值给password_hash字段

    def verify_password(self, password):  # 与存储在User模型中的密码散列值对比
        return check_password_hash(self.password_hash, password)