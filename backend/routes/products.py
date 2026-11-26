"""商品相关接口：列表检索、详情、发布、修改、上下架"""
import json

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions import db
from models import Product, User, Favorite
from routes.common import ok, error

product_bp = Blueprint('products', __name__, url_prefix='/api/products')


@product_bp.get('')
def list_products():
    """商品列表：支持关键词、分类、状态筛选与分页"""
    keyword = (request.args.get('keyword') or '').strip()
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status', type=int)
    user_id = request.args.get('user_id', type=int)
    sort = request.args.get('sort', 'new')
    page = max(request.args.get('page', 1, type=int), 1)
    page_size = min(max(request.args.get('page_size', 12, type=int), 1), 50)

    query = Product.query
    # 前台默认只展示在售商品，传 status 参数可精确筛选
    if status is None:
        query = query.filter(Product.status == Product.STATUS_ON_SALE)
    else:
        query = query.filter(Product.status == status)
    if keyword:
        query = query.filter(Product.title.like(f'%{keyword}%'))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if user_id:
        query = query.filter(Product.user_id == user_id)

    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'hot':
        query = query.order_by(Product.views.desc())
    else:
        query = query.order_by(Product.create_time.desc())

    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    items = [p.to_dict(with_seller=False) for p in pagination.items]
    return ok({
        'list': items,
        'total': pagination.total,
        'page': page,
        'page_size': page_size,
    })


@product_bp.get('/<int:pid>')
def product_detail(pid):
    """商品详情，浏览量自增"""
    product = Product.query.get(pid)
    if not product:
        return error('商品不存在')
    product.views += 1
    db.session.commit()

    data = product.to_dict()
    # 若已登录，返回当前用户是否收藏了该商品
    from flask_jwt_extended import verify_jwt_in_request
    try:
        verify_jwt_in_request(optional=True)
        uid = get_jwt_identity()
        data['is_favorite'] = bool(
            uid and Favorite.query.filter_by(user_id=int(uid), product_id=pid).first()
        )
    except Exception:
        data['is_favorite'] = False
    return ok(data)


@product_bp.post('')
@jwt_required()
def create_product():
    """发布商品"""
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    title = (data.get('title') or '').strip()
    price = data.get('price')
    category_id = data.get('category_id')
    images = data.get('images') or []

    if not title:
        return error('商品标题不能为空')
    if price is None or not isinstance(price, (int, float)) or price <= 0:
        return error('请填写正确的价格')
    if not category_id:
        return error('请选择商品分类')

    product = Product(
        user_id=user_id,
        category_id=category_id,
        title=title,
        description=(data.get('description') or '').strip(),
        price=price,
        original_price=data.get('original_price'),
        images=json.dumps(images) if images else None,
    )
    db.session.add(product)
    db.session.commit()
    return ok(product.to_dict(), '发布成功')


@product_bp.put('/<int:pid>')
@jwt_required()
def update_product(pid):
    """修改自己的商品"""
    user_id = int(get_jwt_identity())
    product = Product.query.get(pid)
    if not product:
        return error('商品不存在')
    if product.user_id != user_id:
        return error('只能修改自己发布的商品')

    data = request.get_json(silent=True) or {}
    if 'title' in data and (data.get('title') or '').strip():
        product.title = data['title'].strip()
    for field in ('description', 'original_price', 'category_id'):
        if field in data:
            setattr(product, field, data[field])
    if 'price' in data and isinstance(data['price'], (int, float)) and data['price'] > 0:
        product.price = data['price']
    if 'images' in data:
        product.images = json.dumps(data['images']) if data['images'] else None
    db.session.commit()
    return ok(product.to_dict(), '修改成功')


@product_bp.delete('/<int:pid>')
@jwt_required()
def delete_product(pid):
    """删除商品：发布者本人或管理员"""
    user = User.query.get(int(get_jwt_identity()))
    product = Product.query.get(pid)
    if not product:
        return error('商品不存在')
    if product.user_id != user.id and user.role != 1:
        return error('无权限删除该商品')
    db.session.delete(product)
    db.session.commit()
    return ok(msg='删除成功')


@product_bp.put('/<int:pid>/status')
@jwt_required()
def change_status(pid):
    """修改商品状态：上架/下架/标记已售"""
    user_id = int(get_jwt_identity())
    product = Product.query.get(pid)
    if not product:
        return error('商品不存在')
    if product.user_id != user_id:
        return error('只能操作自己发布的商品')

    data = request.get_json(silent=True) or {}
    status = data.get('status')
    if status not in (Product.STATUS_ON_SALE, Product.STATUS_SOLD, Product.STATUS_OFF_SALE):
        return error('状态值不合法')
    product.status = status
    db.session.commit()
    return ok(product.to_dict(), '状态修改成功')
