"""图片上传接口"""
import os
import uuid

from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required

from routes.common import ok, error

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')


def allowed_file(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in current_app.config['ALLOWED_EXTENSIONS']


@upload_bp.post('')
@jwt_required()
def upload_image():
    file = request.files.get('file')
    if not file or not file.filename:
        return error('请选择要上传的图片')
    if not allowed_file(file.filename):
        return error('仅支持 png/jpg/jpeg/gif/webp 格式图片')

    ext = file.filename.rsplit('.', 1)[-1].lower()
    filename = f'{uuid.uuid4().hex}.{ext}'
    save_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(save_dir, exist_ok=True)
    file.save(os.path.join(save_dir, filename))
    return ok({'url': f'/uploads/{filename}'}, '上传成功')
