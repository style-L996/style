"""用户认证与个人资料接口"""
from flask import Blueprint, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from extensions import db
from models import User
from routes.common import ok, error

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _identity_user():
    return User.query.get(int(get_jwt_identity()))


@auth_bp.post('/register')
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    nickname = (data.get('nickname') or '').strip()

    if not username or not password:
        return error('账号和密码不能为空')
    if len(username) > 50 or len(password) < 6:
        return error('账号过长或密码少于6位')

    if User.query.filter_by(username=username).first():
        return error('该账号已被注册')

    user = User(username=username, nickname=nickname or username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return ok(user.to_dict(), '注册成功')


@auth_bp.post('/login')
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return error('账号或密码错误')
    if user.status == 0:
        return error('该账号已被禁用，请联系管理员')

    token = create_access_token(identity=str(user.id))
    return ok({'token': token, 'user': user.to_dict()}, '登录成功')


@auth_bp.get('/me')
@jwt_required()
def me():
    return ok(_identity_user().to_dict())


@auth_bp.put('/me')
@jwt_required()
def update_me():
    user = _identity_user()
    data = request.get_json(silent=True) or {}
    for field in ('nickname', 'avatar', 'phone', 'qq'):
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()
    return ok(user.to_dict(), '资料修改成功')


@auth_bp.put('/password')
@jwt_required()
def change_password():
    user = _identity_user()
    data = request.get_json(silent=True) or {}
    old_password = data.get('old_password') or ''
    new_password = data.get('new_password') or ''

    if not user.check_password(old_password):
        return error('原密码错误')
    if len(new_password) < 6:
        return error('新密码不能少于6位')
    user.set_password(new_password)
    db.session.commit()
    return ok(msg='密码修改成功')
