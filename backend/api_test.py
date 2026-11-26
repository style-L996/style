"""API 回归测试脚本：收藏、资料修改（UTF-8 安全）"""
import json
import urllib.request

BASE = 'http://localhost:5000'


def call(method, path, token=None, body=None):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', 'Bearer ' + token)
    data = json.dumps(body).encode('utf-8') if body else None
    try:
        with urllib.request.urlopen(req, data) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode('utf-8'))


# 1. 登录
r = call('POST', '/api/auth/login', body={'username': 'zhangsan', 'password': '123456'})
assert r['code'] == 0, r
token = r['data']['token']
print('登录 OK')

# 2. 修复昵称（之前被测试脚本编码污染）
r = call('PUT', '/api/auth/me', token, {'nickname': '张三'})
print('改昵称:', r['data']['nickname'])

# 3. 收藏 iPad (id=1)
r = call('POST', '/api/favorites/1', token)
print('收藏 iPad:', r['msg'])
r = call('GET', '/api/favorites', token)
titles = [p['title'] for p in r['data']['list']]
print('我的收藏:', titles)

# 4. 详情页 is_favorite 标记
r = call('GET', '/api/products/1', token)
print('iPad is_favorite:', r['data'].get('is_favorite'))

# 5. 取消收藏 → 再收藏（恢复状态）
r = call('DELETE', '/api/favorites/1', token)
print('取消收藏:', r['msg'])
r = call('GET', '/api/products/1', token)
print('取消后 is_favorite:', r['data'].get('is_favorite'))
call('POST', '/api/favorites/1', token)

# 6. 修改密码流程：错误原密码应失败
r = call('PUT', '/api/auth/password', token, {'old_password': 'wrong', 'new_password': '123456'})
print('错误原密码:', r['msg'])

# 7. 管理员登录 + 统计
r = call('POST', '/api/auth/login', body={'username': 'admin', 'password': '123456'})
admin_token = r['data']['token']
print('管理员登录 OK, role =', r['data']['user']['role'])
r = call('GET', '/api/admin/stats', admin_token)
print('统计: 用户', r['data']['user_count'], '| 商品', r['data']['product_count'],
      '| 在售', r['data']['on_sale_count'], '| 留言', r['data']['message_count'])

# 8. 学生访问管理接口应被拒绝
r = call('GET', '/api/admin/stats', token)
print('学生访问管理接口:', r['msg'])

# 9. 未登录发布商品应 401
r = call('POST', '/api/products', body={'title': 'x', 'price': 1, 'category_id': 1})
print('未登录发布:', r['msg'])

# 10. 管理员下架/恢复商品 6（羽绒服）
r = call('PUT', '/api/admin/products/6/status', admin_token, {'status': 0})
print('管理员下架羽绒服:', r['msg'], '状态:', r['data']['status_text'])
r = call('GET', '/api/products?page_size=50')
titles = [p['title'] for p in r['data']['list']]
print('前台在售列表含羽绒服:', '冬季羽绒服 M码 95新' in titles)
r = call('PUT', '/api/admin/products/6/status', admin_token, {'status': 1})
print('恢复上架:', r['msg'])

print('\n=== 全部回归测试完成 ===')
