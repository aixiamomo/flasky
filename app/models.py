# coding=utf-8
from . import db  # 在当前目录下导入db
from . import login_manager

from werkzeug.security import generate_password_hash, check_password_hash  # 加入密码散列
from flask_login import UserMixin  # 支持用户登陆
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')  # 构造关系，返回User模型中，与角色关联的用户组成的列表

    def __repr__(self):
        return '<Role {}'.format(self.name)  # 返回一个可读性的字符串表示模型，测试时候使用


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)

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

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)  # 生成token,有效期一个小时
        return s.dumps({'confirm': self.id})  # 为指定的数据生成加密签名，令牌字符串

    def confirm(self, token):  # 检验token
        s = Serializer(current_app.config['SECRET_KEY'])  # 生成token
        try:
            data = s.loads(token)  # 解码token，
        except:  # 捕获抛出的所有异常
            return False
        if data.get('confirm') != self.id:  # 检验令牌中的ID与current_user保存的已登录用户匹配
            return False
        self.confirmed = True  # 检验通过，设为True
        db.session.add(self)  # 添加到数据库会话
        return True


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
