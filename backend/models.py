"""数据模型定义：用户、分类、商品、留言、收藏"""
import json
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


def to_ts(dt):
    """统一的时间格式化"""
    return dt.strftime('%Y-%m-%d %H:%M:%S') if dt else None


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='登录账号')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    nickname = db.Column(db.String(50), comment='昵称')
    avatar = db.Column(db.String(255), comment='头像URL')
    phone = db.Column(db.String(20), comment='联系电话')
    qq = db.Column(db.String(30), comment='QQ/微信')
    role = db.Column(db.SmallInteger, nullable=False, default=0, comment='0学生 1管理员')
    status = db.Column(db.SmallInteger, nullable=False, default=1, comment='1正常 0禁用')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='注册时间')

    products = db.relationship('Product', backref='seller', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname or self.username,
            'avatar': self.avatar,
            'phone': self.phone,
            'qq': self.qq,
            'role': self.role,
            'status': self.status,
            'create_time': to_ts(self.create_time),
        }


class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False, comment='分类名称')
    sort = db.Column(db.Integer, nullable=False, default=0, comment='排序号')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'sort': self.sort}


class Product(db.Model):
    __tablename__ = 'product'

    STATUS_ON_SALE = 1
    STATUS_SOLD = 2
    STATUS_OFF_SALE = 0

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False, comment='发布者')
    category_id = db.Column(db.BigInteger, db.ForeignKey('category.id'), nullable=False, comment='分类')
    title = db.Column(db.String(100), nullable=False, comment='标题')
    description = db.Column(db.Text, comment='描述')
    price = db.Column(db.Numeric(10, 2), nullable=False, comment='出售价')
    original_price = db.Column(db.Numeric(10, 2), comment='原价')
    images = db.Column(db.String(1000), comment='图片JSON数组')
    status = db.Column(db.SmallInteger, nullable=False, default=1, comment='1在售 2已售 0下架')
    views = db.Column(db.Integer, nullable=False, default=0, comment='浏览量')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='发布时间')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    category = db.relationship('Category')
    messages = db.relationship('Message', backref='product', lazy='dynamic')

    STATUS_TEXT = {1: '在售', 2: '已售', 0: '已下架'}

    @property
    def image_list(self):
        if not self.images:
            return []
        try:
            return json.loads(self.images)
        except (ValueError, TypeError):
            return []

    def to_dict(self, with_seller=True):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'title': self.title,
            'description': self.description,
            'price': float(self.price),
            'original_price': float(self.original_price) if self.original_price else None,
            'images': self.image_list,
            'status': self.status,
            'status_text': self.STATUS_TEXT.get(self.status, '未知'),
            'views': self.views,
            'create_time': to_ts(self.create_time),
            'category_name': self.category.name if self.category else None,
            'message_count': self.messages.count(),
        }
        if with_seller and self.seller:
            data['seller'] = {
                'id': self.seller.id,
                'nickname': self.seller.nickname or self.seller.username,
                'avatar': self.seller.avatar,
                'phone': self.seller.phone,
                'qq': self.seller.qq,
            }
        return data


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    product_id = db.Column(db.BigInteger, db.ForeignKey('product.id'), nullable=False, comment='商品')
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False, comment='留言人')
    content = db.Column(db.String(500), nullable=False, comment='留言内容')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='留言时间')

    user = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'content': self.content,
            'create_time': to_ts(self.create_time),
            'user': {
                'id': self.user.id,
                'nickname': self.user.nickname or self.user.username,
                'avatar': self.user.avatar,
            } if self.user else None,
        }


class Favorite(db.Model):
    __tablename__ = 'favorite'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False, comment='用户')
    product_id = db.Column(db.BigInteger, db.ForeignKey('product.id'), nullable=False, comment='商品')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='收藏时间')

    product = db.relationship('Product')

    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='uk_user_product'),)
