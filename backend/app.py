"""应用入口：校园闲置交易系统后端服务"""
import os

from flask import Flask, send_from_directory
from flask_cors import CORS

from config import Config
from extensions import db, jwt
from routes.auth import auth_bp
from routes.products import product_bp
from routes.messages import message_bp
from routes.favorites import favorite_bp
from routes.categories import category_bp
from routes.upload import upload_bp
from routes.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 跨域支持（前后端分离开发模式）
    CORS(app, supports_credentials=True)

    db.init_app(app)
    jwt.init_app(app)

    # 注册各业务蓝图
    for bp in (auth_bp, product_bp, message_bp, favorite_bp, category_bp, upload_bp, admin_bp):
        app.register_blueprint(bp)

    # 上传图片的静态访问
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.get('/')
    def index():
        return {'name': '校园闲置交易系统 API', 'version': '1.0', 'status': 'ok'}

    # JWT 过期/无效统一响应
    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        from flask import jsonify
        return jsonify({'code': 401, 'msg': '登录已过期，请重新登录'}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        from flask import jsonify
        return jsonify({'code': 401, 'msg': '无效的登录凭证'}), 401

    @jwt.unauthorized_loader
    def missing_token(reason):
        from flask import jsonify
        return jsonify({'code': 401, 'msg': '请先登录'}), 401

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
