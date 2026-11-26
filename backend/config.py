"""全局配置文件"""
import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # MySQL 数据库连接配置（如有改动请同步修改 sql/campus_market.sql 部署说明）
    SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://root:4530@localhost:3306/campus_market?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # JWT 认证配置
    JWT_SECRET_KEY = 'campus-market-jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # 图片上传配置
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 最大 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
