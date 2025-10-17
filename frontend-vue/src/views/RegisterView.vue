<template>
  <div class="register-container">
    <div class="register-card">
      <h2>用户注册</h2>
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-row">
          <div class="form-group">
            <label for="studentId">学号 *</label>
            <input
              id="studentId"
              v-model="registerForm.student_id"
              type="text"
              placeholder="请输入学号"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="username">用户名 *</label>
            <input
              id="username"
              v-model="registerForm.username"
              type="text"
              placeholder="请输入用户名"
              required
            />
          </div>
        </div>
        
        <div class="form-group">
          <label for="realName">真实姓名 *</label>
          <input
            id="realName"
            v-model="registerForm.real_name"
            type="text"
            placeholder="请输入真实姓名"
            required
          />
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="phone">手机号 *</label>
            <input
              id="phone"
              v-model="registerForm.phone"
              type="tel"
              placeholder="请输入手机号"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="email">邮箱 *</label>
            <input
              id="email"
              v-model="registerForm.email"
              type="email"
              placeholder="请输入邮箱"
              required
            />
          </div>
        </div>
        
        <div class="form-group">
          <label for="password">密码 *</label>
          <input
            id="password"
            v-model="registerForm.password"
            type="password"
            placeholder="至少8位，包含字母和数字"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">确认密码 *</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            required
          />
        </div>
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>
        
        <button type="submit" class="register-btn" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      
      <div class="register-footer">
        <p>已有账号？ <router-link to="/login">立即登录</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const registerForm = ref({
  student_id: '',
  username: '',
  real_name: '',
  phone: '',
  email: '',
  password: ''
})

const confirmPassword = ref('')
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const validateForm = () => {
  if (!registerForm.value.student_id || !registerForm.value.username || 
      !registerForm.value.real_name || !registerForm.value.phone || 
      !registerForm.value.email || !registerForm.value.password) {
    return '请填写所有必填字段'
  }
  
  if (registerForm.value.password !== confirmPassword.value) {
    return '两次输入的密码不一致'
  }
  
  if (registerForm.value.password.length < 8) {
    return '密码至少需要8位字符'
  }
  
  const hasLetter = /[a-zA-Z]/.test(registerForm.value.password)
  const hasNumber = /[0-9]/.test(registerForm.value.password)
  if (!hasLetter || !hasNumber) {
    return '密码必须包含字母和数字'
  }
  
  const phoneRegex = /^1[3-9][0-9]{9}$/
  if (!phoneRegex.test(registerForm.value.phone)) {
    return '请输入正确的手机号格式'
  }
  
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  if (!emailRegex.test(registerForm.value.email)) {
    return '请输入正确的邮箱格式'
  }
  
  return null
}

const handleRegister = async () => {
  const validationError = validateForm()
  if (validationError) {
    errorMessage.value = validationError
    return
  }
  
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  
  try {
    const result = await userStore.register(registerForm.value)
    
    if (result.success) {
      successMessage.value = '注册成功！即将跳转到登录页面...'
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      errorMessage.value = result.message
    }
  } catch {
    errorMessage.value = '注册失败，请检查网络连接'
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
  min-height: 80vh;
  padding: 40px;
}

.register-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  padding: 50px;
  width: 100%;
  max-width: 700px;
}

.register-card h2 {
  text-align: center;
  margin-bottom: 40px;
  color: #2c3e50;
  font-size: 2rem;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-group label {
  font-weight: 500;
  color: #2c3e50;
  font-size: 16px;
}

.form-group input {
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.register-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 15px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.success-message {
  color: #155724;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
}

.register-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.register-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.register-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.register-footer {
  text-align: center;
  margin-top: 20px;
}

.register-footer a {
  color: #007bff;
  text-decoration: none;
}

.register-footer a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .register-card {
    padding: 20px;
  }
}
</style>