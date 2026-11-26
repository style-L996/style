<template>
  <div class="profile page-container">
    <aside class="panel user-card">
      <el-avatar :size="76" :src="store.user?.avatar || ''">
        {{ (store.user?.nickname || 'U').slice(0, 1) }}
      </el-avatar>
      <div class="user-name">{{ store.user?.nickname }}</div>
      <div class="user-sub">账号：{{ store.user?.username }}</div>
      <el-tag :type="store.isAdmin ? 'warning' : 'info'" size="small" effect="plain">
        {{ store.isAdmin ? '管理员' : '普通学生' }}
      </el-tag>
      <div class="user-stats">
        <div class="stat-item">
          <b>{{ myProducts.length }}</b>
          <span>发布</span>
        </div>
        <div class="stat-item">
          <b>{{ favorites.length }}</b>
          <span>收藏</span>
        </div>
        <div class="stat-item">
          <b>{{ myMessages.length }}</b>
          <span>留言</span>
        </div>
      </div>
      <el-button class="publish-btn" type="primary" :icon="Plus" @click="router.push('/publish')">
        发布闲置
      </el-button>
    </aside>

    <section class="panel content-card">
      <el-tabs v-model="activeTab">
        <!-- 我的发布 -->
        <el-tab-pane label="我的发布" name="products">
          <div v-loading="loading.products">
            <div v-if="myProducts.length" class="product-list">
              <div v-for="p in myProducts" :key="p.id" class="product-row">
                <el-image
                  v-if="p.images && p.images.length"
                  :src="p.images[0]"
                  fit="cover"
                  class="row-cover"
                  @click="router.push(`/product/${p.id}`)"
                >
                  <template #error>
                    <div class="img-placeholder row-cover"><el-icon><Picture /></el-icon></div>
                  </template>
                </el-image>
                <div v-else class="img-placeholder row-cover" @click="router.push(`/product/${p.id}`)">
                  <el-icon><Picture /></el-icon>
                </div>

                <div class="row-info">
                  <div class="row-title" @click="router.push(`/product/${p.id}`)">{{ p.title }}</div>
                  <div class="row-meta">
                    <span class="row-price">¥{{ formatPrice(p.price) }}</span>
                    <el-tag size="small" :type="statusType(p.status)" effect="light">
                      {{ p.status_text }}
                    </el-tag>
                    <span class="row-sub">{{ p.views }} 浏览 · {{ p.message_count }} 留言</span>
                  </div>
                  <div class="row-time">{{ p.create_time }}</div>
                </div>

                <div class="row-actions">
                  <el-button size="small" @click="router.push(`/publish/${p.id}`)">编辑</el-button>
                  <el-button
                    v-if="p.status === 1"
                    size="small"
                    type="warning"
                    plain
                    @click="changeStatus(p, 0)"
                  >
                    下架
                  </el-button>
                  <el-button
                    v-else-if="p.status === 0"
                    size="small"
                    type="success"
                    plain
                    @click="changeStatus(p, 1)"
                  >
                    上架
                  </el-button>
                  <el-button
                    v-if="p.status !== 2"
                    size="small"
                    type="primary"
                    plain
                    @click="changeStatus(p, 2)"
                  >
                    标记已售
                  </el-button>
                  <el-button size="small" type="danger" plain @click="removeProduct(p)">删除</el-button>
                </div>
              </div>
            </div>
            <el-empty v-else description="还没有发布过闲置" />
          </div>
        </el-tab-pane>

        <!-- 我的收藏 -->
        <el-tab-pane label="我的收藏" name="favorites">
          <div v-loading="loading.favorites">
            <div v-if="favorites.length" class="fav-grid">
              <div v-for="p in favorites" :key="p.id" class="fav-card" @click="router.push(`/product/${p.id}`)">
                <el-image v-if="p.images && p.images.length" :src="p.images[0]" fit="cover" class="fav-cover">
                  <template #error>
                    <div class="img-placeholder fav-cover"><el-icon><Picture /></el-icon></div>
                  </template>
                </el-image>
                <div v-else class="img-placeholder fav-cover"><el-icon><Picture /></el-icon></div>
                <div class="fav-body">
                  <div class="fav-title">{{ p.title }}</div>
                  <div class="fav-footer">
                    <span class="row-price">¥{{ formatPrice(p.price) }}</span>
                    <el-button link type="danger" size="small" @click.stop="cancelFavorite(p)">
                      取消收藏
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="还没有收藏任何商品" />
          </div>
        </el-tab-pane>

        <!-- 我的留言 -->
        <el-tab-pane label="我的留言" name="messages">
          <div v-loading="loading.messages">
            <div v-if="myMessages.length" class="msg-list">
              <div v-for="m in myMessages" :key="m.id" class="msg-row">
                <div class="msg-body">
                  <div class="msg-text">{{ m.content }}</div>
                  <div class="msg-meta">
                    来自商品「{{ m.product_title || '已删除商品' }}」 · {{ m.create_time }}
                  </div>
                </div>
                <el-button link type="danger" size="small" @click="removeMessage(m)">删除</el-button>
              </div>
            </div>
            <el-empty v-else description="还没有发表过留言" />
          </div>
        </el-tab-pane>

        <!-- 编辑资料 -->
        <el-tab-pane label="编辑资料" name="info">
          <el-form :model="profileForm" label-width="90px" class="profile-form">
            <el-form-item label="头像">
              <el-upload
                class="avatar-uploader"
                :show-file-list="false"
                :http-request="handleAvatarUpload"
                accept="image/*"
              >
                <el-avatar :size="72" :src="profileForm.avatar || ''">
                  {{ (profileForm.nickname || 'U').slice(0, 1) }}
                </el-avatar>
                <div class="avatar-tip">点击更换头像</div>
              </el-upload>
            </el-form-item>
            <el-form-item label="昵称">
              <el-input v-model="profileForm.nickname" maxlength="50" style="width: 260px" />
            </el-form-item>
            <el-form-item label="联系电话">
              <el-input v-model="profileForm.phone" maxlength="20" style="width: 260px" placeholder="方便买家联系你" />
            </el-form-item>
            <el-form-item label="QQ/微信">
              <el-input v-model="profileForm.qq" maxlength="30" style="width: 260px" placeholder="选填" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="savingProfile" @click="saveProfile">保存资料</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 修改密码 -->
        <el-tab-pane label="修改密码" name="password">
          <el-form ref="pwdRef" :model="pwdForm" :rules="pwdRules" label-width="90px" class="profile-form">
            <el-form-item label="原密码" prop="old_password">
              <el-input v-model="pwdForm.old_password" type="password" show-password style="width: 260px" />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="pwdForm.new_password" type="password" show-password style="width: 260px" />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm">
              <el-input v-model="pwdForm.confirm" type="password" show-password style="width: 260px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="savingPwd" @click="changePassword">确认修改</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Picture } from '@element-plus/icons-vue'
import { productApi, favoriteApi, messageApi, authApi, uploadApi } from '../api'
import { useUserStore } from '../stores/user'

const router = useRouter()
const store = useUserStore()

const activeTab = ref('products')
const myProducts = ref([])
const favorites = ref([])
const myMessages = ref([])
const loading = reactive({ products: false, favorites: false, messages: false })

const savingProfile = ref(false)
const savingPwd = ref(false)
const pwdRef = ref()

const profileForm = reactive({
  nickname: store.user?.nickname || '',
  phone: store.user?.phone || '',
  qq: store.user?.qq || '',
  avatar: store.user?.avatar || ''
})

const pwdForm = reactive({ old_password: '', new_password: '', confirm: '' })

const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码至少 6 位', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== pwdForm.new_password) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

function formatPrice(v) {
  return Number(v || 0).toFixed(2).replace(/\.00$/, '')
}

function statusType(s) {
  return s === 1 ? 'success' : s === 2 ? 'warning' : 'info'
}

async function loadProducts() {
  loading.products = true
  try {
    // 前台列表默认只返回在售商品，因此按状态分别拉取后合并
    const params = { user_id: store.user.id, page: 1, page_size: 50 }
    const [onSale, sold, offSale] = await Promise.all([
      productApi.list({ ...params, status: 1 }),
      productApi.list({ ...params, status: 2 }),
      productApi.list({ ...params, status: 0 })
    ])
    myProducts.value = [...onSale.list, ...sold.list, ...offSale.list].sort((a, b) =>
      b.create_time.localeCompare(a.create_time)
    )
  } catch (e) {
    myProducts.value = []
  } finally {
    loading.products = false
  }
}

async function loadFavorites() {
  loading.favorites = true
  try {
    const data = await favoriteApi.list({ page: 1, page_size: 50 })
    favorites.value = data.list
  } catch (e) {
    favorites.value = []
  } finally {
    loading.favorites = false
  }
}

async function loadMessages() {
  loading.messages = true
  try {
    const data = await messageApi.myList({ page: 1, page_size: 50 })
    myMessages.value = data.list
  } catch (e) {
    myMessages.value = []
  } finally {
    loading.messages = false
  }
}

async function changeStatus(p, status) {
  try {
    await productApi.changeStatus(p.id, status)
    ElMessage.success('操作成功')
    loadProducts()
  } catch (e) {
    /* 拦截器已提示 */
  }
}

function removeProduct(p) {
  ElMessageBox.confirm(`确定删除商品「${p.title}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await productApi.remove(p.id)
      ElMessage.success('删除成功')
      loadProducts()
    })
    .catch(() => {})
}

async function cancelFavorite(p) {
  try {
    await favoriteApi.remove(p.id)
    ElMessage.success('已取消收藏')
    loadFavorites()
  } catch (e) {
    /* 拦截器已提示 */
  }
}

function removeMessage(m) {
  ElMessageBox.confirm('确定删除这条留言吗？', '提示', { type: 'warning' })
    .then(async () => {
      await messageApi.remove(m.id)
      ElMessage.success('删除成功')
      loadMessages()
    })
    .catch(() => {})
}

async function handleAvatarUpload(options) {
  try {
    const data = await uploadApi.upload(options.file)
    profileForm.avatar = data.url
    options.onSuccess && options.onSuccess(data)
  } catch (e) {
    options.onError && options.onError(e)
  }
}

async function saveProfile() {
  savingProfile.value = true
  try {
    const user = await authApi.updateProfile({
      nickname: profileForm.nickname,
      phone: profileForm.phone,
      qq: profileForm.qq,
      avatar: profileForm.avatar
    })
    store.setUser(user)
    ElMessage.success('资料修改成功')
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    savingProfile.value = false
  }
}

async function changePassword() {
  await pwdRef.value.validate()
  savingPwd.value = true
  try {
    await authApi.changePassword({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    ElMessage.success('密码修改成功')
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirm = ''
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    savingPwd.value = false
  }
}

onMounted(() => {
  loadProducts()
  loadFavorites()
  loadMessages()
})
</script>

<style scoped>
.profile {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 18px;
  align-items: start;
}

.user-card {
  padding: 26px 20px;
  text-align: center;
  position: sticky;
  top: 88px;
}

.user-name {
  margin-top: 12px;
  font-size: 17px;
  font-weight: 600;
}

.user-sub {
  margin: 4px 0 10px;
  color: var(--text-sub);
  font-size: 12px;
}

.user-stats {
  display: flex;
  justify-content: space-around;
  margin: 18px 0;
  padding: 14px 0;
  border-top: 1px dashed var(--border);
  border-bottom: 1px dashed var(--border);
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-item b {
  font-size: 18px;
  color: var(--brand);
}

.stat-item span {
  color: var(--text-sub);
  font-size: 12px;
}

.publish-btn {
  width: 100%;
}

.content-card {
  padding: 16px 24px 24px;
  min-height: 480px;
}

.product-list {
  display: flex;
  flex-direction: column;
}

.product-row {
  display: flex;
  gap: 14px;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
}

.row-cover {
  width: 90px;
  height: 90px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  cursor: pointer;
}

.row-info {
  flex: 1;
  min-width: 0;
}

.row-title {
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}

.row-title:hover {
  color: var(--brand);
}

.row-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}

.row-price {
  color: var(--brand);
  font-weight: 700;
  font-size: 16px;
}

.row-sub {
  color: var(--text-sub);
  font-size: 12px;
}

.row-time {
  margin-top: 8px;
  color: var(--text-sub);
  font-size: 12px;
}

.row-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: center;
}

.fav-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.fav-card {
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.fav-card:hover {
  box-shadow: 0 6px 16px rgba(28, 39, 60, 0.1);
}

.fav-cover {
  width: 100%;
  height: 130px;
}

.fav-body {
  padding: 10px 12px 12px;
}

.fav-title {
  font-size: 14px;
  font-weight: 600;
  height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.fav-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}

.msg-list {
  display: flex;
  flex-direction: column;
}

.msg-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
}

.msg-body {
  flex: 1;
}

.msg-text {
  color: #4a5160;
}

.msg-meta {
  margin-top: 6px;
  color: var(--text-sub);
  font-size: 12px;
}

.profile-form {
  max-width: 520px;
  padding-top: 8px;
}

.avatar-uploader {
  cursor: pointer;
  text-align: center;
}

.avatar-tip {
  margin-top: 6px;
  color: var(--text-sub);
  font-size: 12px;
}

@media (max-width: 900px) {
  .profile {
    grid-template-columns: 1fr;
  }
  .user-card {
    position: static;
  }
  .fav-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
