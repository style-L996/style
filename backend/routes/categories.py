"""商品分类接口"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from extensions import db
from models import Category, Product
from routes.common import ok, error, admin_required

category_bp = Blueprint('categories', __name__, url_prefix='/api/categories')


@category_bp.get('')
def list_categories():
    """全部分类（带在售商品数量）"""
    categories = Category.query.order_by(Category.sort.asc(), Category.id.asc()).all()
    items = []
    for c in categories:
        d = c.to_dict()
        d['product_count'] = Product.query.filter_by(category_id=c.id, status=1).count()
        items.append(d)
    return ok(items)


@category_bp.post('')
@admin_required
def create_category():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return error('分类名称不能为空')
    if Category.query.filter_by(name=name).first():
        return error('分类已存在')
    c = Category(name=name, sort=data.get('sort', 0))
    db.session.add(c)
    db.session.commit()
    return ok(c.to_dict(), '添加成功')


@category_bp.put('/<int:cid>')
@admin_required
def update_category(cid):
    c = Category.query.get(cid)
    if not c:
        return error('分类不存在')
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if name and name != c.name:
        if Category.query.filter(Category.name == name, Category.id != cid).first():
            return error('分类名已存在')
        c.name = name
    if 'sort' in data:
        c.sort = data['sort']
    db.session.commit()
    return ok(c.to_dict(), '修改成功')


@category_bp.delete('/<int:cid>')
@admin_required
def delete_category(cid):
    c = Category.query.get(cid)
    if not c:
        return error('分类不存在')
    if Product.query.filter_by(category_id=cid).first():
        return error('该分类下还有商品，无法删除')
    db.session.delete(c)
    db.session.commit()
    return ok(msg='删除成功')
