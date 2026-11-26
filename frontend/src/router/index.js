import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

import FrontLayout from '../layouts/FrontLayout.vue'
import AdminLayout from '../layouts/AdminLayout.vue'

import Home from '../views/Home.vue'
import Detail from '../views/Detail.vue'
import Publish from '../views/Publish.vue'
import Login from '../views/Login.vue'
import Profile from '../views/Profile.vue'

import Dashboard from '../views/admin/Dashboard.vue'
import Users from '../views/admin/Users.vue'
import AdminForm from '../views/admin/AdminForm.vue'
import Products from '../views/admin/Products.vue'
import Categories from '../views/admin/Categories.vue'
import Messages from '../views/admin/Messages.vue'

const routes = [
  { path: '/login', name: 'Login', component: Login },
  {
    path: '/',
    component: FrontLayout,
    children: [
      { path: '', name: 'Home', component: Home },
      { path: 'product/:id', name: 'Detail', component: Detail },
      { path: 'publish', name: 'Publish', component: Publish, meta: { requireAuth: true } },
      {
        path: 'publish/:id',
        name: 'PublishEdit',
        component: Publish,
        meta: { requireAuth: true }
      },
      { path: 'profile', name: 'Profile', component: Profile, meta: { requireAuth: true } }
    ]
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requireAdmin: true },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'AdminDashboard', component: Dashboard },
      { path: 'users', name: 'AdminUsers', component: Users },
      { path: 'admins', name: 'AdminForm', component: AdminForm },
      { path: 'products', name: 'AdminProducts', component: Products },
      { path: 'categories', name: 'AdminCategories', component: Categories },
      { path: 'messages', name: 'AdminMessages', component: Messages }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 登录 / 管理员权限守卫
router.beforeEach(to => {
  const store = useUserStore()
  const needAuth = to.matched.some(r => r.meta.requireAuth)
  const needAdmin = to.matched.some(r => r.meta.requireAdmin)

  if (needAuth && !store.isLogin) {
    ElMessage.warning('请先登录')
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (needAdmin && !store.isAdmin) {
    ElMessage.warning('无权限访问，请使用管理员账号登录')
    return store.isLogin ? { path: '/' } : { path: '/login' }
  }
  return true
})

export default router
