<template>
  <div class="front-layout">
    <header class="header">
      <div class="page-container header-inner">
        <router-link to="/" class="logo">
          <span class="logo-icon">♻</span>
          <span class="logo-text">校园闲置</span>
        </router-link>

        <nav class="nav">
          <router-link to="/" class="nav-item" :class="{ active: route.path === '/' }">
            首页
          </router-link>
          <router-link
            to="/publish"
            class="nav-item"
            :class="{ active: route.path.startsWith('/publish') }"
          >
            发布闲置
          </router-link>
          <router-link
            to="/profile"
            class="nav-item"
            :class="{ active: route.path.startsWith('/profile') }"
          >
            个人中心
          </router-link>
        </nav>

        <div class="header-right">
          <el-input
            v-model="keyword"
            class="search"
            placeholder="搜索你想要的闲置"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" />
            </template>
          </el-input>

          <template v-if="store.isLogin">
            <el-dropdown trigger="click">
              <span class="user-entry">
                <el-avatar :size="30" :src="avatarUrl">{{ nicknameFirst }}</el-avatar>
                <span class="user-name">{{ store.user?.nickname }}</span>
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="router.push('/profile')">个人中心</el-dropdown-item>
                  <el-dropdown-item v-if="store.isAdmin" @click="router.push('/admin')">
                    后台管理
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button v-if="store.isAdmin" type="primary" plain @click="router.push('/admin')">
              后台管理
            </el-button>
          </template>
          <template v-else>
            <el-button type="primary" @click="router.push('/login')">登录 / 注册</el-button>
          </template>
        </div>
      </div>
    </header>

    <main class="main">
      <router-view />
    </main>

    <footer class="footer">
      <div class="page-container">
        校园闲置交易系统 · 让闲置流转起来 © 2026
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const keyword = ref('')

const avatarUrl = computed(() => store.user?.avatar || '')
const nicknameFirst = computed(() => (store.user?.nickname || 'U').slice(0, 1))

function handleSearch() {
  router.push({ path: '/', query: { keyword: keyword.value || undefined } })
}

function handleLogout() {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' })
    .then(() => {
      store.logout()
      ElMessage.success('已退出登录')
      router.push('/')
    })
    .catch(() => {})
}
</script>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: #fff;
  box-shadow: 0 2px 10px rgba(28, 39, 60, 0.07);
}

.header-inner {
  display: flex;
  align-items: center;
  height: 64px;
  gap: 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 22px;
  font-weight: 700;
  color: var(--brand);
}

.logo-icon {
  font-size: 24px;
}

.nav {
  display: flex;
  gap: 8px;
  flex: 1;
}

.nav-item {
  padding: 8px 14px;
  border-radius: 18px;
  color: var(--text-sub);
  font-size: 15px;
  transition: all 0.2s;
}

.nav-item:hover {
  color: var(--brand);
}

.nav-item.active {
  color: var(--brand);
  background: var(--brand-light);
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search {
  width: 260px;
}

.user-entry {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: var(--text-main);
}

.user-name {
  max-width: 90px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.main {
  min-height: calc(100vh - 64px - 70px);
  padding: 24px 0;
}

.footer {
  padding: 26px 0;
  text-align: center;
  color: var(--text-sub);
  font-size: 13px;
}
</style>
