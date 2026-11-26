<template>
  <div class="admin-page panel">
    <el-table v-loading="loading" :data="list" stripe>
      <el-table-column label="ID" prop="id" width="70" />
      <el-table-column label="留言人" min-width="130">
        <template #default="{ row }">
          <div class="user-cell">
            <el-avatar :size="28" :src="row.user?.avatar || ''">
              {{ (row.user?.nickname || 'U').slice(0, 1) }}
            </el-avatar>
            <span>{{ row.user?.nickname || '-' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="留言内容" prop="content" min-width="240" show-overflow-tooltip />
      <el-table-column label="所属商品" min-width="200">
        <template #default="{ row }">
          <el-button
            v-if="row.product_title"
            link
            type="primary"
            @click="viewProduct(row.product_id)"
          >
            {{ row.product_title }}
          </el-button>
          <span v-else class="deleted-text">商品已删除</span>
        </template>
      </el-table-column>
      <el-table-column label="留言时间" prop="create_time" min-width="160" />
      <el-table-column label="操作" width="90" fixed="right">
        <template #default="{ row }">
          <el-button link type="danger" @click="removeMessage(row)">删除</el-button>
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
import { adminApi } from '../../api'

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const loading = ref(false)

async function loadList() {
  loading.value = true
  try {
    const data = await adminApi.messages({ page: page.value, page_size: pageSize })
    list.value = data.list
    total.value = data.total
  } catch (e) {
    list.value = []
  } finally {
    loading.value = false
  }
}

function viewProduct(id) {
  if (id) window.open(`/product/${id}`, '_blank')
}

function removeMessage(row) {
  ElMessageBox.confirm('确定删除这条留言吗？', '提示', { type: 'warning' })
    .then(async () => {
      await adminApi.removeMessage(row.id)
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

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.deleted-text {
  color: var(--text-sub);
  font-size: 12px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
