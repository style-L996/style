"""收藏接口"""
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions import db
from models import Favorite, Product
from routes.common import ok, error

favorite_bp = Blueprint('favorites', __name__, url_prefix='/api/favorites')


@favorite_bp.get('')
@jwt_required()
def my_favorites():
    """我的收藏列表"""
    user_id = int(get_jwt_identity())
    page = max(request.args.get('page', 1, type=int), 1)
    page_size = min(max(request.args.get('page_size', 12, type=int), 1), 50)
    pagination = (
        Favorite.query.filter_by(user_id=user_id)
        .order_by(Favorite.create_time.desc())
        .paginate(page=page, per_page=page_size, error_out=False)
    )
    items = []
    for fav in pagination.items:
        if fav.product:
            items.append(fav.product.to_dict(with_seller=False))
    return ok({'list': items, 'total': pagination.total})


@favorite_bp.post('/<int:pid>')
@jwt_required()
def add_favorite(pid):
    """收藏商品"""
    user_id = int(get_jwt_identity())
    if not Product.query.get(pid):
        return error('商品不存在')
    if Favorite.query.filter_by(user_id=user_id, product_id=pid).first():
        return ok(msg='已收藏过该商品')
    fav = Favorite(user_id=user_id, product_id=pid)
    db.session.add(fav)
    db.session.commit()
    return ok(msg='收藏成功')


@favorite_bp.delete('/<int:pid>')
@jwt_required()
def remove_favorite(pid):
    """取消收藏"""
    user_id = int(get_jwt_identity())
    fav = Favorite.query.filter_by(user_id=user_id, product_id=pid).first()
    if not fav:
        return error('尚未收藏该商品')
    db.session.delete(fav)
    db.session.commit()
    return ok(msg='已取消收藏')
