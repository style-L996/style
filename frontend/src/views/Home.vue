<template>
  <div class="home page-container">
    <!-- 顶部横幅 -->
    <section class="banner">
      <div class="banner-text">
        <h1>让闲置流转起来</h1>
        <p>校园里的好物，值得被更多人看见</p>
      </div>
      <el-button type="primary" size="large" :icon="Plus" @click="goPublish">
        发布闲置
      </el-button>
    </section>

    <!-- 分类筛选 -->
    <section class="filter-bar panel">
      <div class="filter-row">
        <span class="filter-label">分类：</span>
        <div class="chips">
          <span class="chip" :class="{ active: categoryId === 0 }" @click="selectCategory(0)">
            全部
          </span>
          <span
            v-for="c in categories"
            :key="c.id"
            class="chip"
            :class="{ active: categoryId === c.id }"
            @click="selectCategory(c.id)"
          >
            {{ c.name }}
            <em v-if="c.product_count">{{ c.product_count }}</em>
          </span>
        </div>
      </div>

      <div class="filter-row">
        <span class="filter-label">排序：</span>
        <el-radio-group v-model="sort" size="small" @change="loadProducts">
          <el-radio-button value="new">最新发布</el-radio-button>
          <el-radio-button value="hot">浏览最多</el-radio-button>
          <el-radio-button value="price_asc">价格从低到高</el-radio-button>
          <el-radio-button value="price_desc">价格从高到低</el-radio-button>
        </el-radio-group>
        <div v-if="keyword" class="keyword-tip">
          搜索「{{ keyword }}」
          <el-icon class="clear-icon" @click="clearKeyword"><Close /></el-icon>
        </div>
      </div>
    </section>

    <!-- 商品列表 -->
    <section v-loading="loading" class="product-area">
      <div v-if="products.length" class="product-grid">
        <div
          v-for="p in products"
          :key="p.id"
          class="product-card panel"
          @click="router.push(`/product/${p.id}`)"
        >
          <div class="cover">
            <el-image v-if="p.images && p.images.length" :src="p.images[0]" fit="cover">
              <template #error>
                <div class="img-placeholder cover-fallback"><el-icon><Picture /></el-icon></div>
              </template>
            </el-image>
            <div v-else class="img-placeholder cover-fallback">
              <el-icon><Picture /></el-icon>
            </div>
            <span v-if="p.status_text !== '在售'" class="status-badge">{{ p.status_text }}</span>
          </div>
          <div class="card-body">
            <h3 class="card-title">{{ p.title }}</h3>
            <div class="price-line">
              <span class="price">¥{{ formatPrice(p.price) }}</span>
              <span v-if="p.original_price" class="origin-price">
                ¥{{ formatPrice(p.original_price) }}
              </span>
            </div>
            <div class="meta-line">
              <el-tag size="small" effect="plain" round>{{ p.category_name }}</el-tag>
              <span class="meta-text">{{ p.views }} 浏览 · {{ p.message_count }} 留言</span>
            </div>
          </div>
        </div>
      </div>

      <el-empty v-else-if="!loading" description="暂无相关闲置商品" />

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          background
          layout="prev, pager, next, total"
          :total="total"
          :page-size="pageSize"
          @current-change="loadProducts"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Picture, Close } from '@element-plus/icons-vue'
import { productApi, categoryApi } from '../api'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()

const categories = ref([])
const products = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 12
const loading = ref(false)
const categoryId = ref(0)
const sort = ref('new')
const keyword = ref(route.query.keyword || '')

function formatPrice(v) {
  return Number(v).toFixed(2).replace(/\.00$/, '')
}

async function loadCategories() {
  try {
    categories.value = await categoryApi.list()
  } catch (e) {
    /* 拦截器已提示 */
  }
}

async function loadProducts() {
  loading.value = true
  try {
    const data = await productApi.list({
      page: page.value,
      page_size: pageSize,
      keyword: keyword.value || undefined,
      category_id: categoryId.value || undefined,
      sort: sort.value
    })
    products.value = data.list
    total.value = data.total
  } catch (e) {
    products.value = []
  } finally {
    loading.value = false
  }
}

function selectCategory(id) {
  categoryId.value = id
  page.value = 1
  loadProducts()
}

function clearKeyword() {
  keyword.value = ''
  page.value = 1
  router.replace({ path: '/', query: {} })
  loadProducts()
}

function goPublish() {
  if (!store.isLogin) {
    ElMessage.warning('请先登录')
    router.push({ path: '/login', query: { redirect: '/publish' } })
    return
  }
  router.push('/publish')
}

watch(
  () => route.query.keyword,
  val => {
    keyword.value = val || ''
    page.value = 1
    loadProducts()
  }
)

onMounted(() => {
  loadCategories()
  loadProducts()
})
</script>

<style scoped>
.banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 34px 36px;
  margin-bottom: 18px;
  border-radius: 14px;
  background: linear-gradient(120deg, #ff7a45 0%, #ff9a76 55%, #ffc4a8 100%);
  color: #fff;
  box-shadow: 0 8px 22px rgba(255, 107, 53, 0.25);
}

.banner-text h1 {
  margin: 0 0 8px;
  font-size: 30px;
}

.banner-text p {
  margin: 0;
  opacity: 0.92;
  font-size: 15px;
}

.banner :deep(.el-button--primary) {
  background: #fff;
  border-color: #fff;
  color: var(--brand);
  height: 44px;
  font-weight: 600;
}

.filter-bar {
  padding: 18px 22px;
  margin-bottom: 18px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-row + .filter-row {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px dashed var(--border);
}

.filter-label {
  color: var(--text-sub);
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  padding: 5px 14px;
  border-radius: 16px;
  background: #f4f5f9;
  color: var(--text-sub);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
}

.chip em {
  margin-left: 4px;
  font-style: normal;
  font-size: 11px;
  opacity: 0.7;
}

.chip:hover {
  color: var(--brand);
}

.chip.active {
  background: var(--brand);
  color: #fff;
}

.keyword-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
  color: var(--brand);
  font-size: 13px;
}

.clear-icon {
  cursor: pointer;
}

.product-area {
  min-height: 320px;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.product-card {
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 24px rgba(28, 39, 60, 0.12);
}

.cover {
  position: relative;
  height: 190px;
}

.cover :deep(.el-image) {
  width: 100%;
  height: 100%;
}

.cover-fallback {
  width: 100%;
  height: 100%;
}

.status-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 2px 10px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 12px;
}

.card-body {
  padding: 12px 14px 16px;
}

.card-title {
  margin: 0 0 8px;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
  height: 42px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.price-line {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.price {
  color: var(--brand);
  font-size: 18px;
  font-weight: 700;
}

.origin-price {
  color: #b4b9c4;
  font-size: 12px;
  text-decoration: line-through;
}

.meta-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}

.meta-text {
  color: var(--text-sub);
  font-size: 12px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

@media (max-width: 1100px) {
  .product-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 820px) {
  .product-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .banner {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
