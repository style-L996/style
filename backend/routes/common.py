"""通用工具：统一响应格式与管理员权限装饰器"""
from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from models import User


def ok(data=None, msg='操作成功'):
    return jsonify({'code': 0, 'msg': msg, 'data': data})


def error(msg='操作失败', code=1, http_status=200):
    return jsonify({'code': code, 'msg': msg}), http_status


def admin_required(fn):
    """JWT 认证 + 管理员权限校验"""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = User.query.get(int(get_jwt_identity()))
        if not user or user.role != 1:
            return error('无权限访问，需要管理员身份', code=403)
        return fn(*args, **kwargs)

    return wrapper
