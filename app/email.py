# coding=utf-8
from threading import Thread  # 异步发送Email
from flask import current_app, render_template  # 程序上下文，渲染模板
from flask_mail import Message  # 从mail扩展中导入Message
from . import mail  # 在当前目录下导入mail对象


# 异步发送邮件
def send_async_email(app, msg):  # 确保不同线程send时，程序上下文都激活
    with app.app_context():  # 人工创建程序上下文
        mail.send(msg)


# 定义发邮件函数
def send_email(to, subject, template, **kwargs):  # 收件人，主题，渲染正文的模板，关键字参数列表
    app = current_app.get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])  # 主题，寄件人，收件人列表
    msg.body = render_template(template + '.txt', **kwargs)  # 渲染
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])  # 异步
    thr.start()
    return thr
