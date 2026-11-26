<template>
  <div class="publish page-container">
    <div class="panel publish-panel">
      <h2 class="page-title">{{ isEdit ? '编辑闲置' : '发布闲置' }}</h2>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px" @submit.prevent>
        <el-form-item label="商品标题" prop="title">
          <el-input v-model="form.title" maxlength="100" show-word-limit placeholder="例如：九成新机械键盘，手感超好" />
        </el-form-item>

        <el-form-item label="商品分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 240px">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="出售价格" prop="price">
          <el-input-number v-model="form.price" :min="0.01" :max="999999" :precision="2" :step="10" />
          <span class="unit">元</span>
        </el-form-item>

        <el-form-item label="商品原价">
          <el-input-number v-model="form.original_price" :min="0" :max="999999" :precision="2" :step="10" />
          <span class="unit">元（选填）</span>
        </el-form-item>

        <el-form-item label="商品图片">
          <el-upload
            v-model:file-list="fileList"
            list-type="picture-card"
            :limit="4"
            :http-request="handleUpload"
            :before-upload="beforeUpload"
            :on-remove="syncImages"
            accept="image/*"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">最多上传 4 张图片，单张不超过 5MB</div>
        </el-form-item>

        <el-form-item label="商品描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="5"
            maxlength="1000"
            show-word-limit
            placeholder="介绍一下商品的新旧程度、使用情况、交易方式等"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
            {{ isEdit ? '保存修改' : '立即发布' }}
          </el-button>
          <el-button size="large" @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { productApi, categoryApi, uploadApi } from '../api'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()

const formRef = ref()
const categories = ref([])
const fileList = ref([])
const submitting = ref(false)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  title: '',
  category_id: null,
  price: 0,
  original_price: null,
  description: '',
  images: []
})

const rules = {
  title: [{ required: true, message: '请输入商品标题', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择商品分类', trigger: 'change' }],
  price: [
    { required: true, message: '请填写出售价格', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!value || value <= 0) callback(new Error('价格必须大于 0'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

function beforeUpload(file) {
  const isImage = /image\/(png|jpg|jpeg|gif|webp)/.test(file.type)
  if (!isImage) {
    ElMessage.error('仅支持 png/jpg/jpeg/gif/webp 格式图片')
    return false
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 5MB')
    return false
  }
  return true
}

async function handleUpload(options) {
  try {
    const data = await uploadApi.upload(options.file)
    const uid = options.file.uid
    const item = fileList.value.find(f => f.uid === uid)
    if (item) {
      item.url = data.url
      item.status = 'success'
    }
    syncImages()
    options.onSuccess && options.onSuccess(data)
  } catch (e) {
    options.onError && options.onError(e)
  }
}

function syncImages() {
  form.images = fileList.value
    .map(f => f.url || (f.response && f.response.url))
    .filter(Boolean)
}

async function loadCategories() {
  categories.value = await categoryApi.list()
}

async function loadProduct(id) {
  const data = await productApi.detail(id)
  if (data.user_id !== store.user?.id) {
    ElMessage.error('只能编辑自己发布的商品')
    router.replace('/profile')
    return
  }
  form.title = data.title
  form.category_id = data.category_id
  form.price = data.price
  form.original_price = data.original_price
  form.description = data.description
  form.images = data.images || []
  fileList.value = form.images.map((url, i) => ({ name: `图片${i + 1}`, url }))
}

async function handleSubmit() {
  await formRef.value.validate()
  if (form.images.length === 0) {
    ElMessage.warning('请至少上传一张商品图片')
    return
  }
  submitting.value = true
  const payload = {
    title: form.title,
    category_id: form.category_id,
    price: form.price,
    original_price: form.original_price || null,
    description: form.description,
    images: form.images
  }
  try {
    if (isEdit.value) {
      await productApi.update(route.params.id, payload)
      ElMessage.success('修改成功')
      router.push(`/product/${route.params.id}`)
    } else {
      const data = await productApi.create(payload)
      ElMessage.success('发布成功')
      router.push(`/product/${data.id}`)
    }
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await loadCategories()
  if (isEdit.value) loadProduct(route.params.id)
})
</script>

<style scoped>
.publish {
  max-width: 760px;
}

.publish-panel {
  padding: 26px 30px 30px;
}

.unit {
  margin-left: 8px;
  color: var(--text-sub);
}

.upload-tip {
  width: 100%;
  color: var(--text-sub);
  font-size: 12px;
  line-height: 1.6;
}
</style>
