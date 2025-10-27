<template>
  <div class="register-container">
    <el-card class="register-card" shadow="always">
      <template #header>
        <div class="card-header">
          <el-icon :size="48" color="#67c23a"><UserFilled /></el-icon>
          <h2>用户注册</h2>
          <p>加入校内二手交易平台</p>
        </div>
      </template>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="rules"
        label-position="top"
        size="large"
        @submit.prevent="handleRegister"
      >
        <el-row :gutter="20">
          <el-col :span="24" :md="12">
            <el-form-item label="学号" prop="student_id">
              <el-input
                v-model="registerForm.student_id"
                placeholder="请输入学号"
                clearable
              >
                <template #prefix>
                  <el-icon><Postcard /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>

          <el-col :span="24" :md="12">
            <el-form-item label="用户名" prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="请输入用户名"
                clearable
              >
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="真实姓名" prop="real_name">
          <el-input
            v-model="registerForm.real_name"
            placeholder="请输入真实姓名"
            clearable
          >
            <template #prefix>
              <el-icon><Avatar /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="24" :md="12">
            <el-form-item label="手机号" prop="phone">
              <el-input
                v-model="registerForm.phone"
                placeholder="请输入手机号"
                maxlength="11"
                clearable
              >
                <template #prefix>
                  <el-icon><Iphone /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>

          <el-col :span="24" :md="12">
            <el-form-item label="邮箱" prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="请输入邮箱"
                clearable
              >
                <template #prefix>
                  <el-icon><Message /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="至少8位，包含字母和数字"
            show-password
            clearable
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
          <div class="password-strength">
            <span>密码强度：</span>
            <el-progress
              :percentage="passwordStrength"
              :color="passwordStrengthColor"
              :show-text="false"
              style="width: 120px"
            />
            <span class="strength-text">{{ passwordStrengthText }}</span>
          </div>
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
            clearable
            @keyup.enter="handleRegister"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="agreement">
          <el-checkbox v-model="registerForm.agreement">
            我已阅读并同意
            <el-link type="primary" :underline="false">《用户协议》</el-link>
            和
            <el-link type="primary" :underline="false">《隐私政策》</el-link>
          </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="success"
            :loading="loading"
            native-type="submit"
            style="width: 100%"
            size="large"
          >
            {{ loading ? '注册中...' : '注册' }}
          </el-button>
        </el-form-item>
      </el-form>

      <el-divider>或</el-divider>

      <div class="login-link">
        <span>已有账号？</span>
        <el-link type="primary" @click="router.push('/login')">
          立即登录
        </el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, Iphone, Message, Avatar, Postcard, UserFilled } from '@element-plus/icons-vue'
import type { RegisterParams } from '@/types'

const router = useRouter()
const userStore = useUserStore()

const registerFormRef = ref<FormInstance>()
const loading = ref(false)

interface RegisterForm extends RegisterParams {
  confirmPassword: string
  agreement: boolean
}

const registerForm = ref<RegisterForm>({
  student_id: '',
  username: '',
  real_name: '',
  phone: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreement: false
})

const passwordStrength = computed((): number => {
  const pwd = registerForm.value.password
  if (!pwd) return 0

  let strength = 0
  if (pwd.length >= 8) strength += 25
  if (pwd.length >= 12) strength += 25
  if (/\d/.test(pwd)) strength += 20
  if (/[a-z]/.test(pwd)) strength += 15
  if (/[A-Z]/.test(pwd)) strength += 15

  return Math.min(strength, 100)
})

const passwordStrengthColor = computed((): string => {
  if (passwordStrength.value < 40) return '#f56c6c'
  if (passwordStrength.value < 70) return '#e6a23c'
  return '#67c23a'
})

const passwordStrengthText = computed((): string => {
  if (passwordStrength.value < 40) return '弱'
  if (passwordStrength.value < 70) return '中'
  return '强'
})

const validateStudentId = (_rule: unknown, value: string, callback: (error?: Error) => void): void => {
  if (!value) {
    callback(new Error('请输入学号'))
  } else if (!/^\d{8,12}$/.test(value)) {
    callback(new Error('学号格式不正确(8-12位数字)'))
  } else {
    callback()
  }
}

const validatePhone = (_rule: unknown, value: string, callback: (error?: Error) => void): void => {
  if (!value) {
    callback(new Error('请输入手机号'))
  } else if (!/^1[3-9]\d{9}$/.test(value)) {
    callback(new Error('手机号格式不正确'))
  } else {
    callback()
  }
}

const validateEmail = (_rule: unknown, value: string, callback: (error?: Error) => void): void => {
  if (!value) {
    callback(new Error('请输入邮箱'))
  } else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(value)) {
    callback(new Error('邮箱格式不正确'))
  } else {
    callback()
  }
}

const validatePassword = (_rule: unknown, value: string, callback: (error?: Error) => void): void => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 8) {
    callback(new Error('密码长度至少为8位'))
  } else if (!/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/.test(value)) {
    callback(new Error('密码必须包含字母和数字'))
  } else {
    if (registerForm.value.confirmPassword) {
      registerFormRef.value?.validateField('confirmPassword')
    }
    callback()
  }
}

const validateConfirmPassword = (_rule: unknown, value: string, callback: (error?: Error) => void): void => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.value.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateAgreement = (_rule: unknown, value: boolean, callback: (error?: Error) => void): void => {
  if (!value) {
    callback(new Error('请阅读并同意用户协议'))
  } else {
    callback()
  }
}

const rules: FormRules<RegisterForm> = {
  student_id: [{ validator: validateStudentId, trigger: 'blur' }],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度在2-20个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/, message: '用户名只能包含字母、数字、下划线和中文', trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在2-20个字符', trigger: 'blur' }
  ],
  phone: [{ validator: validatePhone, trigger: 'blur' }],
  email: [{ validator: validateEmail, trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }],
  agreement: [{ validator: validateAgreement, trigger: 'change' }]
}

const handleRegister = async (): Promise<void> => {
  if (!registerFormRef.value) return

  try {
    await registerFormRef.value.validate()
    loading.value = true

    const result = await userStore.register({
      student_id: registerForm.value.student_id,
      username: registerForm.value.username,
      real_name: registerForm.value.real_name,
      phone: registerForm.value.phone,
      email: registerForm.value.email,
      password: registerForm.value.password
    })

    if (result.success) {
      ElMessage.success('注册成功!请登录')
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else {
      ElMessage.error(result.message || '注册失败')
    }
  } catch (error) {
    console.error('Register validation failed:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
  padding: 40px 20px;
}

.register-card {
  width: 100%;
  max-width: 680px;
}

.card-header {
  text-align: center;
  padding: 20px 0;
}

.card-header h2 {
  margin: 20px 0 10px 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.card-header p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.password-strength {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
}

.strength-text {
  font-weight: 600;
}

.login-link {
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.login-link span {
  margin-right: 8px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
}

:deep(.el-input__wrapper) {
  transition: all 0.3s;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--el-color-primary) inset;
}

:deep(.el-checkbox) {
  height: auto;
  white-space: normal;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .register-container {
    padding: 20px 10px;
  }

  .register-card {
    max-width: 100%;
  }

  .card-header h2 {
    font-size: 24px;
  }

  :deep(.el-col) {
    width: 100%;
  }
}
</style>
