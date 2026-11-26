# 基于 Web 技术的校园闲置交易系统设计与实现

> 湖南软件职业技术大学 毕业设计
> 姓名：毛文杰　学号：202401140105　班级：Web2401

## 一、项目简介

本系统是一个面向校园场景的闲置物品交易平台，采用**前后端分离架构**开发。学生用户可以发布、浏览、检索闲置商品，通过留言与卖家沟通并收藏感兴趣的商品；管理员通过后台对用户、商品、分类和留言进行统一管理。

## 二、技术栈

| 层次 | 技术 |
| ---- | ---- |
| 前端 | Vue 3 + Vite + Vue Router + Pinia + Element Plus + Axios + ECharts |
| 后端 | Python Flask + Flask-SQLAlchemy + Flask-JWT-Extended + Flask-Cors |
| 数据库 | MySQL 8.0（5 张数据表，含外键约束） |
| 认证 | JWT（JSON Web Token）令牌认证 |
| 架构 | 前后端分离，RESTful API，Vite 代理联调 |

## 三、目录结构

```
campus-market/
├── backend/                     # Flask 后端
│   ├── app.py                   # 应用入口（蓝图注册、JWT处理、静态资源）
│   ├── config.py                # 配置（数据库连接、JWT密钥、上传限制）
│   ├── extensions.py            # Flask 扩展实例
│   ├── models.py                # 数据模型（User/Category/Product/Message/Favorite）
│   ├── requirements.txt         # Python 依赖
│   ├── gen_demo_images.py       # 演示图片生成脚本（可选运行）
│   ├── api_test.py              # 接口回归测试脚本（可选运行）
│   ├── routes/                  # 接口蓝图
│   │   ├── auth.py              # 注册/登录/个人资料/修改密码
│   │   ├── products.py          # 商品列表检索/详情/发布/修改/上下架
│   │   ├── messages.py          # 商品留言
│   │   ├── favorites.py         # 收藏
│   │   ├── categories.py        # 分类
│   │   ├── upload.py            # 图片上传
│   │   ├── admin.py             # 管理端（统计/用户/商品/留言管理）
│   │   └── common.py            # 统一响应与管理员权限装饰器
│   └── uploads/                 # 上传图片存储目录
├── frontend/                    # Vue3 前端
│   ├── vite.config.js           # Vite 配置（/api、/uploads 代理到后端）
│   └── src/
│       ├── api/                 # Axios 封装与全部接口
│       ├── router/              # 路由与登录/权限守卫
│       ├── stores/              # Pinia 用户状态（localStorage 持久化）
│       ├── layouts/             # 前台布局 / 后台布局
│       ├── views/               # 页面（首页/详情/发布/个人中心/登录注册）
│       │   └── admin/           # 后台页面（看板/用户/商品/分类/留言管理）
│       └── styles/global.css    # 全局主题样式
└── sql/campus_market.sql        # 数据库脚本（建库建表+演示数据）
```

## 四、快速启动

### 1. 导入数据库

本机需安装 MySQL 8.0，然后执行：

```bash
mysql -u root -p < sql/campus_market.sql
```

脚本会自动创建 `campus_market` 数据库、5 张表以及演示数据。

> 数据库连接配置在 `backend/config.py`，如账号密码不同请修改其中的 `SQLALCHEMY_DATABASE_URI`。

### 2. 启动后端（端口 5000）

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 3. 启动前端（端口 5173）

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 http://localhost:5173 即可使用系统。

## 五、测试账号

| 角色 | 账号 | 密码 | 说明 |
| ---- | ---- | ---- | ---- |
| 管理员 | admin | 123456 | 可进入"后台管理" |
| 学生 | zhangsan / lisi / wangwu | 123456 | 普通用户 |

## 六、功能清单

### 学生端

- 注册、登录（JWT），登录状态 7 天有效
- 商品浏览：分类筛选、关键词搜索、按最新/浏览量/价格排序、分页
- 商品详情：图片轮播、浏览量统计、卖家信息、联系卖家
- 发布闲置：多图上传（最多 4 张）、分类选择、价格与原价、描述
- 商品管理（我的发布）：编辑、上架/下架、标记已售、删除
- 留言：商品下留言、删除自己的留言、查看我发表的留言
- 收藏：收藏/取消收藏、我的收藏列表
- 个人中心：我的发布、我的收藏、我的留言、编辑资料（含头像上传）、修改密码

### 管理员后台

- 数据看板：用户/商品/在售/留言统计卡片、近 7 天发布趋势折线图、分类分布饼图（ECharts）
- 用户管理：搜索、禁用/启用、删除（管理员账号受保护）
- 商品管理：全状态商品列表、搜索筛选、下架/上架、删除
- 分类管理：新增/编辑/删除（有商品时禁止删除）、重名校验
- 留言管理：查看全部留言、删除违规留言

## 七、数据库设计（5 张表）

| 表名 | 说明 | 关键字段 |
| ---- | ---- | ---- |
| user | 用户表 | username(唯一)、password_hash、role(0学生/1管理员)、status(1正常/0禁用) |
| category | 商品分类 | name(唯一)、sort |
| product | 商品表 | user_id→user、category_id→category、price、images(JSON数组)、status(1在售/2已售/0下架)、views |
| message | 商品留言 | product_id→product、user_id→user、content |
| favorite | 收藏表 | user_id+product_id 联合唯一 |

ER 关系：用户 1—N 商品 / 用户 1—N 留言 / 用户 N—N 商品（通过 favorite）/ 分类 1—N 商品。

## 八、主要 API 一览（前缀 /api）

| 模块 | 接口 | 说明 |
| ---- | ---- | ---- |
| 认证 | POST /auth/register、/auth/login | 注册、登录 |
| 认证 | GET/PUT /auth/me、PUT /auth/password | 资料、改密 |
| 商品 | GET /products?keyword&category_id&sort&page | 列表检索 |
| 商品 | GET/PUT/DELETE /products/:id、PUT /products/:id/status | 详情/编辑/删除/状态 |
| 留言 | GET/POST /products/:id/messages、DELETE /messages/:id | 留言 |
| 收藏 | GET/POST/DELETE /favorites/:productId | 收藏 |
| 分类 | GET /categories、POST/PUT/DELETE | 分类（写操作需管理员） |
| 上传 | POST /upload | 图片上传 |
| 管理 | GET /admin/stats 及 /admin/users、/admin/products 等 | 管理端接口 |

统一响应格式：`{"code": 0, "msg": "操作成功", "data": {...}}`，非 0 表示业务失败，401 表示未登录/过期。

## 九、系统测试

- 浏览器功能测试：首页浏览/分类/排序/搜索、登录、详情、收藏、留言、发布、个人中心各标签页、后台各管理页面均已通过
- 接口回归测试：运行 `python backend/api_test.py` 可一键验证核心接口（含权限隔离、异常场景）
