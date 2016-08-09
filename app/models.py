# coding=utf-8
import hashlib
from datetime import datetime

from . import db  # 在当前目录下导入db
from . import login_manager

from werkzeug.security import generate_password_hash, check_password_hash  # 加入密码散列
from flask_login import UserMixin, AnonymousUserMixin  # 支持用户登陆,检查用户权限
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request


class Permission(object):  # 程序权限常量：关注、评论、写文章、修改评论、管理网站
    Follow = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Post(db.Model):
    """博客文章模型"""
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)  # 权限
    users = db.relationship('User', backref='role', lazy='dynamic')  # P49 构造关系，返回User模型中，与角色关联的用户组成的列表

    def __repr__(self):
        """返回一个可读性的字符串表示模型，测试时候使用"""
        return '<Role {}'.format(self.name)

    @staticmethod
    def insert_roles():  # 静态方法，用来在数据库中创建角色实例
        roles = {
            'User': (Permission.Follow |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.Follow |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }  # 角色字典，|按位或，将权限位值组合起来
        for r in roles:
            role = Role.query.filter_by(name=r).first()  # 数据库查找有无角色字典里的用户行
            if role is None:
                role = Role(name=r)  # 新建一行
            role.permissions = roles[r][0]  # 权限位值
            role.default = roles[r][1]  # 默认角色，这里为User
            db.session.add(role)  # 添加到数据库会话
        db.session.commit()  # 提交


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        """初始化默认的用户角色"""
        super(User, self).__init__(**kwargs)  # 调用父类的构造函数
        if self.role is None:  # 判定用户有没定义角色
            if self.email == current_app.config['FLASKY_ADMIN']:  # 根据邮箱值定义用户
                self.role == Role.query.filter_by(permissions=0xff).first()  # 定义管理员
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()  # 定义默认用户

        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    def __repr__(self):
        return '<User {}'.format(self.name)

    @property  # 只写属性.
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

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def confirm(self, token):  # 检验token
        """确认用户token"""
        s = Serializer(current_app.config['SECRET_KEY'])  # 生成token
        try:
            data = s.loads(token)  # 解码token，
        except:  # 捕获抛出的所有异常
            return False
        if data.get('confirm') != self.id:  # 检验token中的ID与current_user保存的已登录用户匹配
            return False
        self.confirmed = True  # 检验通过，设为True,self表示一行
        db.session.add(self)  # 添加到数据库会话
        return True

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()  # 修改邮箱，重新计算头像散列值
        db.session.add(self)
        return True

    def can(self, permissions):  # 如果角色包含传入参数/（请求）的所有权限位，返回True
        """检查用户是否有指定的权限"""
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        """每次访问网页后，刷新这个值：最后登陆时间"""
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


class AnonymousUser(AnonymousUserMixin):
    """定义匿名用户类,未登陆用户的current_user"""
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser  # 把匿名类注册给登陆管理器


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
