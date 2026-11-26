<template>
  <div v-loading="loading" class="detail page-container">
    <el-page-header content="商品详情" @back="router.push('/')" />

    <div v-if="product" class="detail-main">
      <div class="gallery panel">
        <el-carousel v-if="images.length" height="380px" :autoplay="false" indicator-position="outside">
          <el-carousel-item v-for="(img, i) in images" :key="i">
            <el-image :src="img" fit="contain" class="gallery-img">
              <template #error>
                <div class="img-placeholder gallery-img"><el-icon><Picture /></el-icon></div>
              </template>
            </el-image>
          </el-carousel-item>
        </el-carousel>
        <div v-else class="img-placeholder gallery-empty">
          <el-icon><Picture /></el-icon>
        </div>
      </div>

      <div class="info">
        <h2 class="title">{{ product.title }}</h2>
        <div class="price-box">
          <span class="price">¥{{ formatPrice(product.price) }}</span>
          <span v-if="product.original_price" class="origin">
            原价 ¥{{ formatPrice(product.original_price) }}
          </span>
          <el-tag class="status-tag" :type="statusType" effect="light">
            {{ product.status_text }}
          </el-tag>
        </div>

        <div class="meta">
          <span>{{ product.views }} 次浏览</span>
          <el-divider direction="vertical" />
          <span>分类：{{ product.category_name }}</span>
          <el-divider direction="vertical" />
          <span>发布于 {{ product.create_time }}</span>
        </div>

        <div class="seller panel">
          <el-avatar :size="46" :src="product.seller?.avatar || ''">
            {{ (product.seller?.nickname || 'U').slice(0, 1) }}
          </el-avatar>
          <div class="seller-info">
            <div class="seller-name">{{ product.seller?.nickname }}</div>
            <div class="seller-sub">卖家 · 已发布闲置</div>
          </div>
          <el-button type="primary" plain :icon="ChatDotRound" @click="showContact = true">
            联系卖家
          </el-button>
        </div>

        <div class="actions">
          <el-button
            :type="product.is_favorite ? 'warning' : 'default'"
            :icon="product.is_favorite ? StarFilled : Star"
            @click="toggleFavorite"
          >
            {{ product.is_favorite ? '已收藏' : '收藏' }}
          </el-button>
          <el-button
            v-if="isOwner"
            type="primary"
            :icon="Edit"
            @click="router.push(`/publish/${product.id}`)"
          >
            编辑商品
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="product" class="bottom">
      <section class="panel desc-panel">
        <h3 class="section-title">商品描述</h3>
        <p class="desc">{{ product.description || '卖家很懒，什么都没有写～' }}</p>
      </section>

      <section class="panel msg-panel">
        <h3 class="section-title">
          留言 <span class="msg-count">{{ messagesTotal }}</span>
        </h3>

        <div v-if="store.isLogin" class="msg-form">
          <el-input
            v-model="msgContent"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
            placeholder="想问问卖家什么？"
          />
          <div class="msg-form-footer">
            <el-button type="primary" :loading="sending" @click="sendMessage">发表留言</el-button>
          </div>
        </div>
        <div v-else class="msg-login-tip">
          <el-button link type="primary" @click="router.push({ path: '/login', query: { redirect: route.fullPath } })">
            登录
          </el-button>
          后可以留言
        </div>

        <div v-if="messages.length" class="msg-list">
          <div v-for="m in messages" :key="m.id" class="msg-item">
            <el-avatar :size="36" :src="m.user?.avatar || ''">
              {{ (m.user?.nickname || 'U').slice(0, 1) }}
            </el-avatar>
            <div class="msg-body">
              <div class="msg-head">
                <span class="msg-user">{{ m.user?.nickname }}</span>
                <span class="msg-time">{{ m.create_time }}</span>
                <el-button
                  v-if="store.isLogin && (store.isAdmin || m.user_id === store.user?.id)"
                  link
                  type="danger"
                  size="small"
                  @click="removeMessage(m)"
                >
                  删除
                </el-button>
              </div>
              <div class="msg-content">{{ m.content }}</div>
            </div>
          </div>
        </div>
        <el-empty v-else description="还没有人留言，来抢沙发吧" :image-size="80" />
      </section>
    </div>

    <el-dialog v-model="showContact" title="联系卖家" width="360px">
      <div class="contact-list">
        <div class="contact-item">
          <span class="contact-label">昵称</span>
          <span>{{ product?.seller?.nickname }}</span>
        </div>
        <div class="contact-item">
          <span class="contact-label">电话</span>
          <span>{{ product?.seller?.phone || '未填写' }}</span>
        </div>
        <div class="contact-item">
          <span class="contact-label">QQ/微信</span>
          <span>{{ product?.seller?.qq || '未填写' }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Picture, Star, StarFilled, ChatDotRound, Edit } from '@element-plus/icons-vue'
import { productApi, messageApi, favoriteApi } from '../api'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()

const product = ref(null)
const messages = ref([])
const messagesTotal = ref(0)
const loading = ref(false)
const sending = ref(false)
const msgContent = ref('')
const showContact = ref(false)

const images = computed(() => product.value?.images || [])
const isOwner = computed(() => store.isLogin && product.value?.user_id === store.user?.id)
const statusType = computed(() => {
  const s = product.value?.status
  return s === 1 ? 'success' : s === 2 ? 'warning' : 'info'
})

function formatPrice(v) {
  return Number(v || 0).toFixed(2).replace(/\.00$/, '')
}

async function loadProduct() {
  loading.value = true
  try {
    product.value = await productApi.detail(route.params.id)
    loadMessages()
  } catch (e) {
    product.value = null
  } finally {
    loading.value = false
  }
}

async function loadMessages() {
  try {
    const data = await messageApi.list(route.params.id, { page: 1, page_size: 20 })
    messages.value = data.list
    messagesTotal.value = data.total
  } catch (e) {
    messages.value = []
  }
}

async function toggleFavorite() {
  if (!store.isLogin) {
    ElMessage.warning('请先登录')
    router.push({ path: '/login', query: { redirect: route.fullPath } })
    return
  }
  try {
    if (product.value.is_favorite) {
      await favoriteApi.remove(product.value.id)
      product.value.is_favorite = false
      ElMessage.success('已取消收藏')
    } else {
      await favoriteApi.add(product.value.id)
      product.value.is_favorite = true
      ElMessage.success('收藏成功')
    }
  } catch (e) {
    /* 拦截器已提示 */
  }
}

async function sendMessage() {
  const content = msgContent.value.trim()
  if (!content) {
    ElMessage.warning('请输入留言内容')
    return
  }
  sending.value = true
  try {
    await messageApi.create(product.value.id, { content })
    msgContent.value = ''
    ElMessage.success('留言成功')
    loadMessages()
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    sending.value = false
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

watch(() => route.params.id, loadProduct)
onMounted(loadProduct)
</script>

<style scoped>
.detail-main {
  display: grid;
  grid-template-columns: 520px 1fr;
  gap: 20px;
  margin-top: 18px;
}

.gallery {
  padding: 14px;
}

.gallery-img {
  width: 100%;
  height: 100%;
  background: #fafafa;
}

.gallery-empty {
  height: 380px;
  border-radius: 8px;
}

.info {
  display: flex;
  flex-direction: column;
  gap: 14px;
  background: #fff;
  border-radius: var(--radius);
  padding: 22px 24px;
  box-shadow: 0 2px 12px rgba(28, 39, 60, 0.06);
}

.title {
  margin: 0;
  font-size: 22px;
  line-height: 1.4;
}

.price-box {
  display: flex;
  align-items: baseline;
  gap: 10px;
  padding: 14px 16px;
  border-radius: 8px;
  background: var(--brand-light);
}

.price {
  color: var(--brand);
  font-size: 28px;
  font-weight: 700;
}

.origin {
  color: #b4b9c4;
  text-decoration: line-through;
  font-size: 13px;
}

.status-tag {
  margin-left: auto;
}

.meta {
  color: var(--text-sub);
  font-size: 13px;
}

.seller {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  box-shadow: none;
  border: 1px solid var(--border);
}

.seller-info {
  flex: 1;
}

.seller-name {
  font-weight: 600;
}

.seller-sub {
  color: var(--text-sub);
  font-size: 12px;
  margin-top: 2px;
}

.actions {
  margin-top: auto;
  display: flex;
  gap: 10px;
}

.bottom {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
}

.desc-panel,
.msg-panel {
  padding: 20px 24px;
}

.section-title {
  margin: 0 0 14px;
  font-size: 16px;
}

.msg-count {
  color: var(--text-sub);
  font-size: 13px;
  font-weight: 400;
}

.desc {
  margin: 0;
  color: #4a5160;
  line-height: 1.8;
  white-space: pre-wrap;
}

.msg-form-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.msg-login-tip {
  padding: 12px 0;
  color: var(--text-sub);
}

.msg-list {
  margin-top: 10px;
}

.msg-item {
  display: flex;
  gap: 10px;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
}

.msg-item:last-child {
  border-bottom: none;
}

.msg-body {
  flex: 1;
}

.msg-head {
  display: flex;
  align-items: center;
  gap: 10px;
}

.msg-user {
  font-weight: 600;
}

.msg-time {
  color: var(--text-sub);
  font-size: 12px;
}

.msg-content {
  margin-top: 4px;
  color: #4a5160;
  line-height: 1.6;
  white-space: pre-wrap;
}

.contact-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.contact-item {
  display: flex;
  justify-content: space-between;
}

.contact-label {
  color: var(--text-sub);
}

@media (max-width: 1000px) {
  .detail-main,
  .bottom {
    grid-template-columns: 1fr;
  }
}
</style>
