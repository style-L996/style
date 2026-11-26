<template>
  <div class="admin-page panel">
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索商品标题"
        clearable
        style="width: 220px"
        :prefix-icon="Search"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
      <el-select v-model="status" placeholder="全部状态" clearable style="width: 140px" @change="handleSearch">
        <el-option label="在售" :value="1" />
        <el-option label="已售" :value="2" />
        <el-option label="已下架" :value="0" />
      </el-select>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
    </div>

    <el-table v-loading="loading" :data="list" stripe>
      <el-table-column label="商品" min-width="260">
        <template #default="{ row }">
          <div class="product-cell">
            <el-image
              v-if="row.images && row.images.length"
              :src="row.images[0]"
              fit="cover"
              class="cell-cover"
            >
              <template #error>
                <div class="img-placeholder cell-cover"><el-icon><Picture /></el-icon></div>
              </template>
            </el-image>
            <div v-else class="img-placeholder cell-cover"><el-icon><Picture /></el-icon></div>
            <div>
              <div class="cell-title">{{ row.title }}</div>
              <div class="cell-sub">{{ row.category_name }} · {{ row.seller?.nickname || '-' }}</div>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="价格" width="110">
        <template #default="{ row }">
          <span class="price">¥{{ formatPrice(row.price) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="浏览" prop="views" width="80" />
      <el-table-column label="留言" prop="message_count" width="80" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag size="small" :type="statusType(row.status)" effect="light">
            {{ row.status_text }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="发布时间" prop="create_time" min-width="160" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 1"
            link
            type="warning"
            @click="changeStatus(row, 0)"
          >
            下架
          </el-button>
          <el-button
            v-else-if="row.status === 0"
            link
            type="success"
            @click="changeStatus(row, 1)"
          >
            上架
          </el-button>
          <el-button link type="primary" @click="viewProduct(row)">查看</el-button>
          <el-button link type="danger" @click="removeProduct(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="page"
        background
        layout="prev, pager, next, total"
        :total="total"
        :page-size="pageSize"
        @current-change="loadList"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Picture } from '@element-plus/icons-vue'
import { adminApi } from '../../api'

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const keyword = ref('')
const status = ref(null)
const loading = ref(false)

function formatPrice(v) {
  return Number(v || 0).toFixed(2).replace(/\.00$/, '')
}

function statusType(s) {
  return s === 1 ? 'success' : s === 2 ? 'warning' : 'info'
}

async function loadList() {
  loading.value = true
  try {
    const data = await adminApi.products({
      page: page.value,
      page_size: pageSize,
      keyword: keyword.value || undefined,
      status: status.value === null ? undefined : status.value
    })
    list.value = data.list
    total.value = data.total
  } catch (e) {
    list.value = []
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  loadList()
}

async function changeStatus(row, next) {
  try {
    await adminApi.changeProductStatus(row.id, next)
    ElMessage.success('操作成功')
    loadList()
  } catch (e) {
    /* 拦截器已提示 */
  }
}

function viewProduct(row) {
  window.open(`/product/${row.id}`, '_blank')
}

function removeProduct(row) {
  ElMessageBox.confirm(`确定删除商品「${row.title}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await adminApi.removeProduct(row.id)
      ElMessage.success('删除成功')
      loadList()
    })
    .catch(() => {})
}

onMounted(loadList)
</script>

<style scoped>
.admin-page {
  padding: 20px 22px;
}

.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.product-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.cell-cover {
  width: 52px;
  height: 52px;
  border-radius: 6px;
  flex-shrink: 0;
}

.cell-title {
  font-weight: 600;
  line-height: 1.4;
}

.cell-sub {
  margin-top: 2px;
  color: var(--text-sub);
  font-size: 12px;
}

.price {
  color: var(--brand);
  font-weight: 700;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
