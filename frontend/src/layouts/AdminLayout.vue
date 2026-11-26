<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-icon">♻</span>
        <span>校园闲置后台</span>
      </div>
      <el-menu :default-active="route.path" router class="menu">
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>数据看板</span>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/admins">
          <el-icon><UserFilled /></el-icon>
          <span>管理员登记</span>
        </el-menu-item>
        <el-menu-item index="/admin/products">
          <el-icon><Goods /></el-icon>
          <span>商品管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/categories">
          <el-icon><Menu /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/messages">
          <el-icon><ChatDotRound /></el-icon>
          <span>留言管理</span>
        </el-menu-item>
      </el-menu>
    </aside>

    <div class="content">
      <header class="admin-header">
        <div class="admin-title">{{ pageTitle }}</div>
        <div class="admin-actions">
          <el-button text :icon="Back" @click="router.push('/')">返回前台</el-button>
          <el-divider direction="vertical" />
          <span class="admin-user">{{ store.user?.nickname }}</span>
          <el-button text type="primary" @click="handleLogout">退出</el-button>
        </div>
      </header>
      <main class="admin-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Back } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()

const titles = {
  '/admin/dashboard': '数据看板',
  '/admin/users': '用户管理',
  '/admin/admins': '管理员登记',
  '/admin/products': '商品管理',
  '/admin/categories': '分类管理',
  '/admin/messages': '留言管理'
}

const pageTitle = computed(() => titles[route.path] || '后台管理')

function handleLogout() {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' })
    .then(() => {
      store.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    })
    .catch(() => {})
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg);
}

.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: #fff;
  box-shadow: 2px 0 10px rgba(28, 39, 60, 0.06);
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 64px;
  padding: 0 20px;
  font-size: 16px;
  font-weight: 700;
  color: var(--brand);
  border-bottom: 1px solid var(--border);
}

.brand-icon {
  font-size: 22px;
}

.menu {
  border-right: none;
}

.menu :deep(.el-menu-item.is-active) {
  color: var(--brand);
  background: var(--brand-light);
  border-left: 3px solid var(--brand);
}

.content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 24px;
  background: #fff;
  box-shadow: 0 2px 10px rgba(28, 39, 60, 0.06);
}

.admin-title {
  font-size: 18px;
  font-weight: 600;
}

.admin-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.admin-user {
  color: var(--text-sub);
}

.admin-main {
  flex: 1;
  padding: 24px;
}
</style>
