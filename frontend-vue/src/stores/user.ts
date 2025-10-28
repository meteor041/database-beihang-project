import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { userAPI } from '@/api'
import type { User, LoginParams, RegisterParams } from '@/types'

export const useUserStore = defineStore('user', () => {
  // 状态
  const currentUser = ref<User | null>(null)
  const isLoggedIn = ref(false)
  const token = ref('')

  // 计算属性
  const userId = computed(() => currentUser.value?.user_id)
  const username = computed(() => currentUser.value?.username)
  const avatar = computed(() => currentUser.value?.avatar)
  const creditScore = computed(() => currentUser.value?.credit_score)

  // 初始化用户状态
  const initUser = () => {
    if (typeof window === 'undefined') return

    try {
      const savedUser = localStorage.getItem('user')
      const savedToken = localStorage.getItem('token')

      if (savedUser) {
        currentUser.value = JSON.parse(savedUser)
        isLoggedIn.value = true
      }

      token.value = savedToken ?? ''
    } catch (error) {
      console.error('Failed to restore user from localStorage:', error)
      currentUser.value = null
      isLoggedIn.value = false
      token.value = ''
      localStorage.removeItem('user')
      localStorage.removeItem('token')
    }
  }

  // 登录
  const login = async (loginData: LoginParams) => {
    try {
      const response = await userAPI.login(loginData)
      const user = response.user as User | undefined

      if (user) {
        currentUser.value = user
        isLoggedIn.value = true

        // 保存到本地存储
        localStorage.setItem('user', JSON.stringify(user))
        if (response.token) {
          token.value = response.token
          localStorage.setItem('token', response.token)
        } else {
          token.value = ''
          localStorage.removeItem('token')
        }

        return { success: true, message: response.message || '登录成功' }
      }

      return { success: false, message: '登录失败' }
    } catch (error: any) {
      console.error('Login error:', error)
      return {
        success: false,
        message: error.response?.data?.error || '登录失败，请检查网络连接'
      }
    }
  }

  // 注册
  const register = async (registerData: RegisterParams) => {
    try {
      const response = await userAPI.register(registerData)
      return { success: true, message: response.message || '注册成功', userId: response.user_id }
    } catch (error: any) {
      console.error('Register error:', error)
      return {
        success: false,
        message: error.response?.data?.error || '注册失败，请检查网络连接'
      }
    }
  }

  // 登出
  const logout = () => {
    currentUser.value = null
    isLoggedIn.value = false
    token.value = ''

    // 清除本地存储
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  // 更新用户信息
  const updateUserInfo = async (updateData: Partial<User>) => {
    if (!currentUser.value) return { success: false, message: '用户未登录' }

    try {
      await userAPI.updateUser(currentUser.value.user_id, updateData)

      // 更新本地用户信息
      currentUser.value = { ...currentUser.value, ...updateData }
      localStorage.setItem('user', JSON.stringify(currentUser.value))

      return { success: true, message: '用户信息更新成功' }
    } catch (error: any) {
      console.error('Update user error:', error)
      return {
        success: false,
        message: error.response?.data?.error || '更新失败'
      }
    }
  }

  // 刷新用户信息
  const refreshUserInfo = async () => {
    if (!currentUser.value) return

    try {
      const response = await userAPI.getUser(currentUser.value.user_id)
      currentUser.value = response.user as User
      localStorage.setItem('user', JSON.stringify(currentUser.value))
    } catch (error) {
      console.error('Refresh user info error:', error)
    }
  }

  if (typeof window !== 'undefined' && !isLoggedIn.value && !currentUser.value) {
    initUser()
  }

  return {
    // 状态
    currentUser,
    isLoggedIn,
    token,

    // 计算属性
    userId,
    username,
    avatar,
    creditScore,

    // 方法
    initUser,
    login,
    register,
    logout,
    updateUserInfo,
    refreshUserInfo
  }
})
