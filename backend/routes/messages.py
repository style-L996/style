"""商品留言接口"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions import db
from models import Message, Product, User
from routes.common import ok, error

message_bp = Blueprint('messages', __name__, url_prefix='/api')


@message_bp.get('/products/<int:pid>/messages')
def list_messages(pid):
    """某商品的留言列表"""
    if not Product.query.get(pid):
        return error('商品不存在')
    page = max(request.args.get('page', 1, type=int), 1)
    page_size = min(max(request.args.get('page_size', 20, type=int), 1), 50)
    pagination = (
        Message.query.filter_by(product_id=pid)
        .order_by(Message.create_time.desc())
        .paginate(page=page, per_page=page_size, error_out=False)
    )
    return ok({
        'list': [m.to_dict() for m in pagination.items],
        'total': pagination.total,
        'page': page,
        'page_size': page_size,
    })


@message_bp.post('/products/<int:pid>/messages')
@jwt_required()
def create_message(pid):
    """发表留言"""
    user_id = int(get_jwt_identity())
    product = Product.query.get(pid)
    if not product:
        return error('商品不存在')

    data = request.get_json(silent=True) or {}
    content = (data.get('content') or '').strip()
    if not content:
        return error('留言内容不能为空')
    if len(content) > 500:
        return error('留言内容不能超过500字')

    msg = Message(product_id=pid, user_id=user_id, content=content)
    db.session.add(msg)
    db.session.commit()
    return ok(msg.to_dict(), '留言成功')


@message_bp.get('/my/messages')
@jwt_required()
def my_messages():
    """我发表的留言（个人中心）"""
    user_id = int(get_jwt_identity())
    page = max(request.args.get('page', 1, type=int), 1)
    page_size = min(max(request.args.get('page_size', 10, type=int), 1), 50)
    pagination = (
        Message.query.filter_by(user_id=user_id)
        .order_by(Message.create_time.desc())
        .paginate(page=page, per_page=page_size, error_out=False)
    )
    items = []
    for m in pagination.items:
        d = m.to_dict()
        d['product_title'] = m.product.title if m.product else None
        items.append(d)
    return ok({'list': items, 'total': pagination.total})


@message_bp.delete('/messages/<int:mid>')
@jwt_required()
def delete_message(mid):
    """删除留言：本人或管理员"""
    user = User.query.get(int(get_jwt_identity()))
    msg = Message.query.get(mid)
    if not msg:
        return error('留言不存在')
    if msg.user_id != user.id and user.role != 1:
        return error('无权限删除该留言')
    db.session.delete(msg)
    db.session.commit()
    return ok(msg='删除成功')
