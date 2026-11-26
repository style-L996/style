<template>
  <div class="admin-page panel">
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索账号或昵称"
        clearable
        style="width: 240px"
        :prefix-icon="Search"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
    </div>

    <el-table v-loading="loading" :data="list" stripe>
      <el-table-column label="ID" prop="id" width="70" />
      <el-table-column label="用户" min-width="160">
        <template #default="{ row }">
          <div class="user-cell">
            <el-avatar :size="32" :src="row.avatar || ''">
              {{ (row.nickname || 'U').slice(0, 1) }}
            </el-avatar>
            <div>
              <div class="user-nickname">{{ row.nickname }}</div>
              <div class="user-account">{{ row.username }}</div>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="角色" width="100">
        <template #default="{ row }">
          <el-tag size="small" :type="row.role === 1 ? 'warning' : 'info'" effect="plain">
            {{ row.role === 1 ? '管理员' : '学生' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="发布数" prop="product_count" width="90" />
      <el-table-column label="注册时间" prop="create_time" min-width="160" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag size="small" :type="row.status === 1 ? 'success' : 'danger'" effect="light">
            {{ row.status === 1 ? '正常' : '已禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="row.role !== 1"
            link
            :type="row.status === 1 ? 'warning' : 'success'"
            @click="toggleStatus(row)"
          >
            {{ row.status === 1 ? '禁用' : '启用' }}
          </el-button>
          <el-button v-if="row.role !== 1" link type="danger" @click="removeUser(row)">删除</el-button>
          <span v-if="row.role === 1" class="protected-text">受保护</span>
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
import { Search } from '@element-plus/icons-vue'
import { adminApi } from '../../api'

const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const keyword = ref('')
const loading = ref(false)

async function loadList() {
  loading.value = true
  try {
    const data = await adminApi.users({
      page: page.value,
      page_size: pageSize,
      keyword: keyword.value || undefined
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

async function toggleStatus(row) {
  const action = row.status === 1 ? '禁用' : '启用'
  try {
    await adminApi.toggleUserStatus(row.id)
    ElMessage.success(`${action}成功`)
    loadList()
  } catch (e) {
    /* 拦截器已提示 */
  }
}

function removeUser(row) {
  ElMessageBox.confirm(`确定删除用户「${row.nickname}」吗？该操作不可恢复。`, '提示', {
    type: 'warning'
  })
    .then(async () => {
      await adminApi.removeUser(row.id)
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

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-nickname {
  font-weight: 600;
}

.user-account {
  color: var(--text-sub);
  font-size: 12px;
}

.protected-text {
  color: var(--text-sub);
  font-size: 12px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
