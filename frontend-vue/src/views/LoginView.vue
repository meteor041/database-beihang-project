<template>
  <div class="login-container">
    <v-card class="login-card" elevation="8">
      <v-card-title class="text-center card-header">
        <div class="d-flex flex-column align-center">
          <v-icon size="48" color="primary">mdi-account-circle</v-icon>
          <h2 class="text-h4 mt-4 mb-2">用户登录</h2>
          <p class="text-body-2 text-grey">欢迎回到校内二手交易平台</p>
        </div>
      </v-card-title>

      <v-card-text class="px-8 py-6">
        <v-form ref="loginFormRef" @submit.prevent="handleLogin">
          <v-text-field
            v-model="loginForm.loginField"
            label="用户名/学号/手机号"
            placeholder="请输入用户名、学号或手机号"
            prepend-inner-icon="mdi-account"
            :rules="[rules.required, rules.minLength]"
            :error-messages="errors.loginField"
            clearable
            variant="outlined"
            class="mb-2"
          ></v-text-field>

          <v-text-field
            v-model="loginForm.password"
            label="密码"
            placeholder="请输入密码"
            prepend-inner-icon="mdi-lock"
            :type="showPassword ? 'text' : 'password'"
            :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
            @click:append-inner="showPassword = !showPassword"
            :rules="[rules.required, rules.passwordMinLength]"
            :error-messages="errors.password"
            clearable
            variant="outlined"
            class="mb-4"
            @keyup.enter="handleLogin"
          ></v-text-field>

          <v-btn
            type="submit"
            color="primary"
            size="large"
            block
            :loading="loading"
            class="mb-4"
          >
            {{ loading ? '登录中...' : '登录' }}
          </v-btn>
        </v-form>

        <v-divider class="my-4">
          <span class="text-grey px-2">或</span>
        </v-divider>

        <div class="text-center">
          <span class="text-body-2">还没有账号？</span>
          <v-btn variant="text" color="primary" @click="router.push('/register')">
            立即注册
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useNotification } from '@/composables/useNotification'

const router = useRouter()
const userStore = useUserStore()
const notification = useNotification()

const loginFormRef = ref()
const loading = ref(false)
const showPassword = ref(false)

interface LoginForm {
  loginField: string
  password: string
}

const loginForm = ref<LoginForm>({
  loginField: '',
  password: ''
})

const errors = ref({
  loginField: '',
  password: ''
})

// 验证规则
const rules = {
  required: (value: string) => !!value || '此字段为必填项',
  minLength: (value: string) => value.length >= 2 || '长度至少为 2 个字符',
  passwordMinLength: (value: string) => value.length >= 6 || '密码长度至少为 6 位'
}

const handleLogin = async (): Promise<void> => {
  errors.value = { loginField: '', password: '' }

  // 手动验证
  if (!loginForm.value.loginField) {
    errors.value.loginField = '请输入用户名、学号或手机号'
    return
  }
  if (loginForm.value.loginField.length < 2) {
    errors.value.loginField = '长度至少为 2 个字符'
    return
  }
  if (!loginForm.value.password) {
    errors.value.password = '请输入密码'
    return
  }
  if (loginForm.value.password.length < 6) {
    errors.value.password = '密码长度至少为 6 位'
    return
  }

  try {
    loading.value = true

    const result = await userStore.login({
      login_field: loginForm.value.loginField,
      password: loginForm.value.password
    })

    if (result.success) {
      notification.success('登录成功!')
      router.push('/')
    } else {
      notification.error(result.message || '登录失败')
    }
  } catch (error) {
    console.error('Login failed:', error)
    notification.error('登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
  padding: 40px 20px;
}

.login-card {
  width: 100%;
  max-width: 480px;
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

@media (max-width: 768px) {
  .login-container {
    padding: 20px 10px;
  }

  .login-card {
    max-width: 100%;
  }

  .card-header h2 {
    font-size: 24px;
  }
}
</style>
