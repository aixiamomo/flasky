# coding=utf-8
import os
from flask import Flask, render_template, session, redirect, url_for
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form  # 导入表单类
from wtforms import StringField, SubmitField  # 导入字段类
from wtforms.validators import Required  # 导入验证函数
from flask_sqlalchemy import SQLAlchemy  # 导入数据库抽象层代码包 SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))  # 返回目录的绝对路径

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'  # 设置密匙，防止CSRF攻击
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')  # 返回组合后的数据库URL
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # 数据库请求结束后自动提交变动

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)


# 定义Role模型
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)  # 类的属性 = 列
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')  # 返回User模型中，与角色关联的用户组成的列表

    def __repr__(self):
        return '<Role %r>' % self.name  # 返回一个可读性的字符串表示模型，调试测试使用


# 定义User模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


# 定义表单类
class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    # 第二个参数是验证函数，是个列表。Required()确保字段中有数据
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():  # 如果数据能被所有验证函数接受，validate_on_submit()返回True
        user = User.query.filter_by(username=form.name.data).first()  # 查询数据库中有无表单输入的名字
        if user is None:  # 数据库中没有
            user = User(username=form.name.data)  # 一个对象就是一行
            db.session.add(user)
            session['known'] = False
        else:  # 数据库有记录
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))  # Post重定向Get
    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False))


if __name__ == '__main__':
    manager.run()
