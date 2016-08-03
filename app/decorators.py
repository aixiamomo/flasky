# coding=utf-8
"""检查用户权限的自定义装饰器"""

from functools import wraps

from flask import abort
from flask_login import current_user


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                

