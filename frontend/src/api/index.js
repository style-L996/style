/**
 * axios 统一封装 + 全部接口定义
 * 响应结构：{ code, msg, data }，code=0 表示成功
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'
import { useUserStore } from '../stores/user'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000
})

request.interceptors.request.use(config => {
  const store = useUserStore()
  if (store.token) {
    config.headers.Authorization = `Bearer ${store.token}`
  }
  return config
})

request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 0) {
      ElMessage.error(res.msg || '操作失败')
      return Promise.reject(new Error(res.msg || '操作失败'))
    }
    return res.data
  },
  error => {
    const status = error.response && error.response.status
    if (status === 401) {
      const store = useUserStore()
      store.logout()
      ElMessage.error('登录已失效，请重新登录')
      router.push('/login')
    } else {
      const msg =
        (error.response && error.response.data && error.response.data.msg) ||
        '网络异常，请稍后重试'
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  }
)

export default request

// ---------------- 认证 ----------------
export const authApi = {
  register: data => request.post('/auth/register', data),
  login: data => request.post('/auth/login', data),
  me: () => request.get('/auth/me'),
  updateProfile: data => request.put('/auth/me', data),
  changePassword: data => request.put('/auth/password', data)
}

// ---------------- 商品 ----------------
export const productApi = {
  list: params => request.get('/products', { params }),
  detail: id => request.get(`/products/${id}`),
  create: data => request.post('/products', data),
  update: (id, data) => request.put(`/products/${id}`, data),
  remove: id => request.delete(`/products/${id}`),
  changeStatus: (id, status) => request.put(`/products/${id}/status`, { status })
}

// ---------------- 留言 ----------------
export const messageApi = {
  list: (pid, params) => request.get(`/products/${pid}/messages`, { params }),
  create: (pid, data) => request.post(`/products/${pid}/messages`, data),
  myList: params => request.get('/my/messages', { params }),
  remove: id => request.delete(`/messages/${id}`)
}

// ---------------- 收藏 ----------------
export const favoriteApi = {
  list: params => request.get('/favorites', { params }),
  add: pid => request.post(`/favorites/${pid}`),
  remove: pid => request.delete(`/favorites/${pid}`)
}

// ---------------- 分类 ----------------
export const categoryApi = {
  list: () => request.get('/categories'),
  create: data => request.post('/categories', data),
  update: (id, data) => request.put(`/categories/${id}`, data),
  remove: id => request.delete(`/categories/${id}`)
}

// ---------------- 上传 ----------------
export const uploadApi = {
  upload: file => {
    const form = new FormData()
    form.append('file', file)
    return request.post('/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// ---------------- 管理端 ----------------
export const adminApi = {
  stats: () => request.get('/admin/stats'),
  users: params => request.get('/admin/users', { params }),
  createAdmin: data => request.post('/admin/users', data),
  toggleUserStatus: id => request.put(`/admin/users/${id}/status`),
  removeUser: id => request.delete(`/admin/users/${id}`),
  products: params => request.get('/admin/products', { params }),
  changeProductStatus: (id, status) =>
    request.put(`/admin/products/${id}/status`, { status }),
  removeProduct: id => request.delete(`/admin/products/${id}`),
  messages: params => request.get('/admin/messages', { params }),
  removeMessage: id => request.delete(`/admin/messages/${id}`)
}
