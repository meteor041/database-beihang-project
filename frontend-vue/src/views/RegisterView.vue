<template>
  <div class="register-container">
    <v-card class="register-card" elevation="8">
      <v-card-title class="text-center card-header">
        <div class="d-flex flex-column align-center">
          <v-icon size="48" color="success">mdi-account-plus</v-icon>
          <h2 class="text-h4 mt-4 mb-2">用户注册</h2>
          <p class="text-body-2 text-grey">加入校内二手交易平台</p>
        </div>
      </v-card-title>

      <v-card-text class="px-8 py-6">
        <v-form ref="registerFormRef" @submit.prevent="handleRegister">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="registerForm.student_id"
                label="学号"
                placeholder="请输入学号"
                prepend-inner-icon="mdi-card-account-details"
                :error-messages="errors.student_id"
                clearable
                variant="outlined"
              ></v-text-field>
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field
                v-model="registerForm.username"
                label="用户名"
                placeholder="请输入用户名"
                prepend-inner-icon="mdi-account"
                :error-messages="errors.username"
                clearable
                variant="outlined"
              ></v-text-field>
            </v-col>
          </v-row>

          <v-text-field
            v-model="registerForm.real_name"
            label="真实姓名"
            placeholder="请输入真实姓名"
            prepend-inner-icon="mdi-account-circle"
            :error-messages="errors.real_name"
            clearable
            variant="outlined"
            class="mb-2"
          ></v-text-field>

          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="registerForm.phone"
                label="手机号"
                placeholder="请输入手机号"
                prepend-inner-icon="mdi-cellphone"
                :error-messages="errors.phone"
                maxlength="11"
                clearable
                variant="outlined"
              ></v-text-field>
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field
                v-model="registerForm.email"
                label="邮箱"
                placeholder="请输入邮箱"
                prepend-inner-icon="mdi-email"
                :error-messages="errors.email"
                clearable
                variant="outlined"
              ></v-text-field>
            </v-col>
          </v-row>

          <v-text-field
            v-model="registerForm.password"
            label="密码"
            placeholder="至少8位，包含字母和数字"
            prepend-inner-icon="mdi-lock"
            :type="showPassword ? 'text' : 'password'"
            :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
            @click:append-inner="showPassword = !showPassword"
            :error-messages="errors.password"
            clearable
            variant="outlined"
            class="mb-2"
          ></v-text-field>

          <!-- 密码强度指示器 -->
          <div class="password-strength mb-4">
            <span class="text-caption">密码强度：</span>
            <v-progress-linear
              :model-value="passwordStrength"
              :color="passwordStrengthColor"
              height="8"
              rounded
              class="mx-2"
              style="width: 120px"
            ></v-progress-linear>
            <span class="strength-text text-caption font-weight-bold">{{ passwordStrengthText }}</span>
          </div>

          <v-text-field
            v-model="registerForm.confirmPassword"
            label="确认密码"
            placeholder="请再次输入密码"
            prepend-inner-icon="mdi-lock-check"
            :type="showConfirmPassword ? 'text' : 'password'"
            :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
            @click:append-inner="showConfirmPassword = !showConfirmPassword"
            :error-messages="errors.confirmPassword"
            clearable
            variant="outlined"
            class="mb-4"
            @keyup.enter="handleRegister"
          ></v-text-field>

          <v-checkbox
            v-model="registerForm.agreement"
            :error-messages="errors.agreement"
            class="mb-2"
          >
            <template v-slot:label>
              <span class="text-body-2">
                我已阅读并同意
                <a href="#" class="text-primary text-decoration-none">《用户协议》</a>
                和
                <a href="#" class="text-primary text-decoration-none">《隐私政策》</a>
              </span>
            </template>
          </v-checkbox>

          <v-btn
            type="submit"
            color="success"
            size="large"
            block
            :loading="loading"
            class="mb-4"
          >
            {{ loading ? '注册中...' : '注册' }}
          </v-btn>
        </v-form>

        <v-divider class="my-4">
          <span class="text-grey px-2">或</span>
        </v-divider>

        <div class="text-center">
          <span class="text-body-2">已有账号？</span>
          <v-btn variant="text" color="primary" @click="router.push('/login')">
            立即登录
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotification } from '@/composables/useNotification'
import type { RegisterParams } from '@/types'

const router = useRouter()
const userStore = useUserStore()
const notification = useNotification()

const registerFormRef = ref()
const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

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

const errors = ref({
  student_id: '',
  username: '',
  real_name: '',
  phone: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreement: ''
})

// 密码强度计算
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
  if (passwordStrength.value < 40) return 'error'
  if (passwordStrength.value < 70) return 'warning'
  return 'success'
})

const passwordStrengthText = computed((): string => {
  if (passwordStrength.value < 40) return '弱'
  if (passwordStrength.value < 70) return '中'
  return '强'
})

// 表单验证
const validateForm = (): boolean => {
  errors.value = {
    student_id: '',
    username: '',
    real_name: '',
    phone: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreement: ''
  }

  let isValid = true

  // 验证学号
  if (!registerForm.value.student_id) {
    errors.value.student_id = '请输入学号'
    isValid = false
  } else if (!/^\d{8,12}$/.test(registerForm.value.student_id)) {
    errors.value.student_id = '学号格式不正确(8-12位数字)'
    isValid = false
  }

  // 验证用户名
  if (!registerForm.value.username) {
    errors.value.username = '请输入用户名'
    isValid = false
  } else if (registerForm.value.username.length < 2 || registerForm.value.username.length > 20) {
    errors.value.username = '用户名长度在2-20个字符'
    isValid = false
  } else if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(registerForm.value.username)) {
    errors.value.username = '用户名只能包含字母、数字、下划线和中文'
    isValid = false
  }

  // 验证真实姓名
  if (!registerForm.value.real_name) {
    errors.value.real_name = '请输入真实姓名'
    isValid = false
  } else if (registerForm.value.real_name.length < 2 || registerForm.value.real_name.length > 20) {
    errors.value.real_name = '姓名长度在2-20个字符'
    isValid = false
  }

  // 验证手机号
  if (!registerForm.value.phone) {
    errors.value.phone = '请输入手机号'
    isValid = false
  } else if (!/^1[3-9]\d{9}$/.test(registerForm.value.phone)) {
    errors.value.phone = '手机号格式不正确'
    isValid = false
  }

  // 验证邮箱
  if (!registerForm.value.email) {
    errors.value.email = '请输入邮箱'
    isValid = false
  } else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(registerForm.value.email)) {
    errors.value.email = '邮箱格式不正确'
    isValid = false
  }

  // 验证密码
  if (!registerForm.value.password) {
    errors.value.password = '请输入密码'
    isValid = false
  } else if (registerForm.value.password.length < 8) {
    errors.value.password = '密码长度至少为8位'
    isValid = false
  } else if (!/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/.test(registerForm.value.password)) {
    errors.value.password = '密码必须包含字母和数字'
    isValid = false
  }

  // 验证确认密码
  if (!registerForm.value.confirmPassword) {
    errors.value.confirmPassword = '请再次输入密码'
    isValid = false
  } else if (registerForm.value.confirmPassword !== registerForm.value.password) {
    errors.value.confirmPassword = '两次输入的密码不一致'
    isValid = false
  }

  // 验证协议
  if (!registerForm.value.agreement) {
    errors.value.agreement = '请阅读并同意用户协议'
    isValid = false
  }

  return isValid
}

const handleRegister = async (): Promise<void> => {
  if (!validateForm()) {
    return
  }

  try {
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
      notification.success('注册成功!请登录')
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else {
      notification.error(result.message || '注册失败')
    }
  } catch (error) {
    console.error('Register failed:', error)
    notification.error('注册失败，请稍后重试')
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
  padding: 32px 20px 20px;
}

.card-header h2 {
  font-weight: 600;
  color: #303133;
}

.card-header p {
  color: #909399;
}

.password-strength {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #606266;
}

.strength-text {
  min-width: 20px;
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
}
</style>
