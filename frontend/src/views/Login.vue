<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-head">
        <router-link to="/" class="logo">
          <span class="logo-icon">♻</span>
          <span>校园闲置</span>
        </router-link>
        <h2>{{ activeTab === 'login' ? '欢迎回来' : '创建账号' }}</h2>
        <p>让闲置流转起来，让好物遇见新主人</p>
      </div>

      <el-tabs v-model="activeTab" stretch class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form ref="loginRef" :model="loginForm" :rules="loginRules" label-position="top" @submit.prevent>
            <el-form-item label="账号" prop="username">
              <el-input v-model="loginForm.username" placeholder="请输入账号" :prefix-icon="User" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                show-password
                placeholder="请输入密码"
                :prefix-icon="Lock"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="handleLogin">
              登录
            </el-button>
            <div class="tip-row">
              演示账号：admin / 123456 ，zhangsan / 123456
            </div>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerRef"
            :model="registerForm"
            :rules="registerRules"
            label-position="top"
            @submit.prevent
          >
            <el-form-item label="账号" prop="username">
              <el-input v-model="registerForm.username" placeholder="6-50 位字符" :prefix-icon="User" />
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="registerForm.nickname" placeholder="不填则默认使用账号" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                show-password
                placeholder="至少 6 位"
                :prefix-icon="Lock"
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm">
              <el-input
                v-model="registerForm.confirm"
                type="password"
                show-password
                placeholder="请再次输入密码"
                :prefix-icon="Lock"
              />
            </el-form-item>
            <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="handleRegister">
              注册并登录
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <div class="back-home">
        <el-button text :icon="Back" @click="router.push('/')">返回首页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Back } from '@element-plus/icons-vue'
import { authApi } from '../api'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const loginRef = ref()
const registerRef = ref()

const loginForm = reactive({ username: '', password: '' })
const registerForm = reactive({ username: '', nickname: '', password: '', confirm: '' })

const loginRules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const registerRules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

function goAfterLogin(user) {
  if (route.query.redirect) {
    router.push(route.query.redirect)
  } else if (user.role === 1) {
    router.push('/admin')
  } else {
    router.push('/')
  }
}

async function handleLogin() {
  await loginRef.value.validate()
  loading.value = true
  try {
    const data = await authApi.login({ ...loginForm })
    store.setAuth(data.token, data.user)
    ElMessage.success('登录成功')
    goAfterLogin(data.user)
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  await registerRef.value.validate()
  loading.value = true
  try {
    await authApi.register({
      username: registerForm.username,
      password: registerForm.password,
      nickname: registerForm.nickname
    })
    const data = await authApi.login({
      username: registerForm.username,
      password: registerForm.password
    })
    store.setAuth(data.token, data.user)
    ElMessage.success('注册成功，已自动登录')
    goAfterLogin(data.user)
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(125deg, #ff7a45 0%, #ff9a76 45%, #ffd0b8 100%);
  padding: 30px;
}

.login-card {
  width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 30px 34px 22px;
  box-shadow: 0 18px 46px rgba(120, 60, 30, 0.22);
}

.login-head {
  text-align: center;
}

.logo {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 700;
  color: var(--brand);
}

.logo-icon {
  font-size: 24px;
}

.login-head h2 {
  margin: 14px 0 6px;
  font-size: 22px;
}

.login-head p {
  margin: 0;
  color: var(--text-sub);
  font-size: 13px;
}

.login-tabs {
  margin-top: 18px;
}

.login-tabs :deep(.el-tabs__item) {
  font-size: 15px;
}

.submit-btn {
  width: 100%;
  margin-top: 6px;
}

.tip-row {
  margin-top: 12px;
  text-align: center;
  color: var(--text-sub);
  font-size: 12px;
}

.back-home {
  margin-top: 10px;
  text-align: center;
}
</style>
