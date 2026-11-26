<template>
  <div class="admin-page panel">
    <div class="toolbar">
      <el-button type="primary" :icon="Plus" @click="openDialog()">新增分类</el-button>
      <span class="toolbar-tip">分类下有商品时不可删除</span>
    </div>

    <el-table v-loading="loading" :data="list" stripe>
      <el-table-column label="排序号" prop="sort" width="100" />
      <el-table-column label="分类名称" prop="name" min-width="180" />
      <el-table-column label="在售商品数" width="120">
        <template #default="{ row }">
          <el-tag size="small" effect="plain">{{ row.product_count || 0 }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="removeCategory(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑分类' : '新增分类'" width="420px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" maxlength="50" placeholder="如：数码电子" />
        </el-form-item>
        <el-form-item label="排序号" prop="sort">
          <el-input-number v-model="form.sort" :min="0" :max="9999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { categoryApi } from '../../api'

const list = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)
const editing = ref(null)
const formRef = ref()

const form = reactive({ name: '', sort: 0 })

const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
}

async function loadList() {
  loading.value = true
  try {
    list.value = await categoryApi.list()
  } catch (e) {
    list.value = []
  } finally {
    loading.value = false
  }
}

function openDialog(row) {
  editing.value = row || null
  form.name = row ? row.name : ''
  form.sort = row ? row.sort : 0
  dialogVisible.value = true
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (editing.value) {
      await categoryApi.update(editing.value.id, { name: form.name, sort: form.sort })
      ElMessage.success('修改成功')
    } else {
      await categoryApi.create({ name: form.name, sort: form.sort })
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    loadList()
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    saving.value = false
  }
}

function removeCategory(row) {
  ElMessageBox.confirm(`确定删除分类「${row.name}」吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await categoryApi.remove(row.id)
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
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.toolbar-tip {
  color: var(--text-sub);
  font-size: 12px;
}
</style>
