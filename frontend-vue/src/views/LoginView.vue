<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, UserFilled } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

interface LoginForm {
  loginField: string
  password: string
}

const loginForm = ref<LoginForm>({
  loginField: '',
  password: ''
})

const rules: FormRules<LoginForm> = {
  loginField: [
    { required: true, message: '请输入用户名、学号或手机号', trigger: 'blur' },
    { min: 2, message: '长度至少为 2 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为 6 位', trigger: 'blur' }
  ]
}

const handleLogin = async (): Promise<void> => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()
    loading.value = true

    const result = await userStore.login({
      login_field: loginForm.value.loginField,
      password: loginForm.value.password
    })

    if (result.success) {
      ElMessage.success('登录成功!')

      router.push('/')
    } else {
      ElMessage.error(result.message || '登录失败')
    }
  } catch (error) {
    console.error('Login validation failed:', error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <el-card class="login-card" shadow="always">
      <template #header>
        <div class="card-header">
          <el-icon :size="48" color="#409eff"><UserFilled /></el-icon>
          <h2>用户登录</h2>
          <p>欢迎回到校内二手交易平台</p>
        </div>
      </template>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        label-position="top"
        size="large"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="用户名/学号/手机号" prop="loginField">
          <el-input
            v-model="loginForm.loginField"
            placeholder="请输入用户名、学号或手机号"
            clearable
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
            clearable
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            native-type="submit"
            style="width: 100%"
            size="large"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <el-divider>或</el-divider>

      <div class="register-link">
        <span>还没有账号？</span>
        <el-link type="primary" @click="router.push('/register')">
          立即注册
        </el-link>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
/* 使用设计系统变量的卡片式登录页面 */

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 200px);
  padding: var(--spacing-3xl) var(--spacing-lg);
}

.login-card {
  width: 100%;
  max-width: 480px;
}

.card-header {
  text-align: center;
  padding: var(--spacing-lg) 0;
}

.card-header h2 {
  margin: var(--spacing-lg) 0 var(--spacing-sm) 0;
  font-size: var(--font-size-4xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.card-header p {
  margin: 0;
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
}

.register-link {
  text-align: center;
  font-size: var(--font-size-base);
  color: var(--color-text-regular);
}

.register-link span {
  margin-right: var(--spacing-sm);
}

:deep(.el-form-item__label) {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

:deep(.el-input__wrapper) {
  transition: all var(--transition-base);
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--color-primary) inset;
}

@media (max-width: 768px) {
  .login-container {
    padding: var(--spacing-lg) var(--spacing-sm);
  }

  .login-card {
    max-width: 100%;
  }

  .card-header h2 {
    font-size: var(--font-size-3xl);
  }
}
</style>
