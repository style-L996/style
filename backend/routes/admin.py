"""管理员后台接口：统计、用户管理、商品管理、留言管理"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from extensions import db
from models import User, Product, Message, Category
from routes.common import ok, error, admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ---------------- 统计 ----------------
@admin_bp.get('/stats')
@admin_required
def stats():
    """后台首页统计数据"""
    user_count = User.query.filter_by(role=0).count()
    product_count = Product.query.count()
    on_sale_count = Product.query.filter_by(status=1).count()
    sold_count = Product.query.filter_by(status=2).count()
    message_count = Message.query.count()

    # 各分类在售商品数量（用于图表）
    category_stat = [
        {'name': c.name, 'value': Product.query.filter_by(category_id=c.id, status=1).count()}
        for c in Category.query.order_by(Category.sort.asc()).all()
    ]
    # 最近7天新增商品趋势
    from sqlalchemy import func
    from datetime import datetime, timedelta
    today = datetime.now().date()
    trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day + timedelta(days=1), datetime.min.time())
        count = Product.query.filter(
            Product.create_time >= day_start, Product.create_time < day_end
        ).count()
        trend.append({'date': day.strftime('%m-%d'), 'count': count})

    return ok({
        'user_count': user_count,
        'product_count': product_count,
        'on_sale_count': on_sale_count,
        'sold_count': sold_count,
        'message_count': message_count,
        'category_stat': category_stat,
        'trend': trend,
    })


# ---------------- 用户管理 ----------------
@admin_bp.get('/users')
@admin_required
def list_users():
    keyword = (request.args.get('keyword') or '').strip()
    page = max(request.args.get('page', 1, type=int), 1)
    page_size = min(max(request.args.get('page_size', 10, type=int), 1), 50)

    query = User.query
    if keyword:
        query = query.filter(
            db.or_(User.username.like(f'%{keyword}%'), User.nickname.like(f'%{keyword}%'))
        )
    pagination = query.order_by(User.create_time.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )
    items = []
    for u in pagination.items:
        d = u.to_dict()
        d['product_count'] = Product.query.filter_by(user_id=u.id).count()
        items.append(d)
    return ok({'list': items, 'total': pagination.total})


@admin_bp.put('/users/<int:uid>/status')
@admin_required
def toggle_user_status(uid):
    """启用/禁用用户"""
    user = User.query.get(uid)
    if not user:
        return error('用户不存在')
    if user.role == 1:
        return error('不能禁用管理员账号')
    user.status = 0 if user.status == 1 else 1
    db.session.commit()
    return ok(user.to_dict(), '操作成功')


@admin_bp.delete('/users/<int:uid>')
@admin_required
def delete_user(uid):
    user = User.query.get(uid)
    if not user:
        return error('用户不存在')
    if user.role == 1:
        return error('不能删除管理员账号')
    db.session.delete(user)
    db.session.commit()
    return ok(msg='删除成功')


@admin_bp.post('/users')
@admin_required
def create_admin():
    """管理员登记：新增管理员账号"""
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    nickname = (data.get('nickname') or '').strip()
    phone = (data.get('phone') or '').strip()
    qq = (data.get('qq') or '').strip()

    if not username or not password:
        return error('账号和密码不能为空')
    if len(username) < 3 or len(username) > 50:
        return error('账号长度需为 3-50 位')
    if len(password) < 6:
        return error('密码不能少于6位')
    if User.query.filter_by(username=username).first():
        return error('该账号已存在')

    admin = User(
        username=username,
        nickname=nickname or username,
        phone=phone or None,
        qq=qq or None,
        role=1,
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    return ok(admin.to_dict(), '管理员登记成功')



# ---------------- 商品管理 ----------------
@admin_bp.get('/products')
@admin_required
def list_products():
    """全部商品（含下架/已售）"""
    keyword = (request.args.get('keyword') or '').strip()
    status = request.args.get('status', type=int)
    page = max(request.args.get('page', 1, type=int), 1)
    page_size = min(max(request.args.get('page_size', 10, type=int), 1), 50)

    query = Product.query
    if keyword:
        query = query.filter(Product.title.like(f'%{keyword}%'))
    if status is not None:
        query = query.filter(Product.status == status)
    pagination = query.order_by(Product.create_time.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )
    return ok({'list': [p.to_dict() for p in pagination.items], 'total': pagination.total})


@admin_bp.put('/products/<int:pid>/status')
@admin_required
def change_product_status(pid):
    """管理员下架/恢复商品"""
    product = Product.query.get(pid)
    if not product:
        return error('商品不存在')
    data = request.get_json(silent=True) or {}
    status = data.get('status')
    if status not in (Product.STATUS_ON_SALE, Product.STATUS_OFF_SALE, Product.STATUS_SOLD):
        return error('状态值不合法')
    product.status = status
    db.session.commit()
    return ok(product.to_dict(), '操作成功')


@admin_bp.delete('/products/<int:pid>')
@admin_required
def delete_product(pid):
    product = Product.query.get(pid)
    if not product:
        return error('商品不存在')
    db.session.delete(product)
    db.session.commit()
    return ok(msg='删除成功')


# ---------------- 留言管理 ----------------
@admin_bp.get('/messages')
@admin_required
def list_messages():
    page = max(request.args.get('page', 1, type=int), 1)
    page_size = min(max(request.args.get('page_size', 10, type=int), 1), 50)
    pagination = Message.query.order_by(Message.create_time.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )
    items = []
    for m in pagination.items:
        d = m.to_dict()
        d['product_title'] = m.product.title if m.product else None
        items.append(d)
    return ok({'list': items, 'total': pagination.total})


@admin_bp.delete('/messages/<int:mid>')
@admin_required
def delete_message(mid):
    msg = Message.query.get(mid)
    if not msg:
        return error('留言不存在')
    db.session.delete(msg)
    db.session.commit()
    return ok(msg='删除成功')
