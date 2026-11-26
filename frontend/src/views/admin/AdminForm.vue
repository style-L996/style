<template>
  <div class="admin-form-page">
    <section class="panel form-panel">
      <h3 class="form-title">管理员登记</h3>
      <p class="form-tip">
        登记成功后，该账号可使用「后台管理」入口登录，拥有用户、商品、分类、留言等全部管理权限。
      </p>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        class="form-body"
        @submit.prevent
      >
        <el-form-item label="登录账号" prop="username">
          <el-input v-model="form.username" maxlength="50" placeholder="3-50 位，登录时使用" />
        </el-form-item>
        <el-form-item label="管理员昵称">
          <el-input v-model="form.nickname" maxlength="50" placeholder="不填则默认使用账号" />
        </el-form-item>
        <el-form-item label="登录密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="至少 6 位" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm">
          <el-input v-model="form.confirm" type="password" show-password placeholder="请再次输入密码" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.phone" maxlength="20" placeholder="选填" />
        </el-form-item>
        <el-form-item label="QQ/微信">
          <el-input v-model="form.qq" maxlength="30" placeholder="选填" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
            登记管理员
          </el-button>
          <el-button size="large" @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </section>

    <el-alert
      class="notice"
      type="warning"
      :closable="false"
      show-icon
      title="请谨慎登记管理员账号，管理员拥有全部后台操作权限。"
    />
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '../../api'

const router = useRouter()
const formRef = ref()
const submitting = ref(false)

const form = reactive({
  username: '',
  nickname: '',
  password: '',
  confirm: '',
  phone: '',
  qq: ''
})

const rules = {
  username: [
    { required: true, message: '请输入登录账号', trigger: 'blur' },
    { min: 3, max: 50, message: '账号长度需为 3-50 位', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入登录密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.password) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

function resetForm() {
  formRef.value.resetFields()
  form.nickname = ''
  form.phone = ''
  form.qq = ''
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    await adminApi.createAdmin({
      username: form.username,
      nickname: form.nickname,
      password: form.password,
      phone: form.phone,
      qq: form.qq
    })
    ElMessageBox.alert(`管理员「${form.nickname || form.username}」登记成功，可使用该账号登录后台。`, '登记成功', {
      type: 'success',
      confirmButtonText: '知道了'
    }).then(() => {
      resetForm()
      router.push('/admin/users')
    })
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.admin-form-page {
  max-width: 720px;
}

.form-panel {
  padding: 26px 30px 30px;
}

.form-title {
  margin: 0 0 8px;
  font-size: 18px;
}

.form-tip {
  margin: 0 0 22px;
  color: var(--text-sub);
  font-size: 13px;
  line-height: 1.7;
}

.form-body {
  max-width: 560px;
}

.form-body :deep(.el-input) {
  width: 100%;
  max-width: 320px;
}

.notice {
  margin-top: 16px;
}
</style>
