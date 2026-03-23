import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  const login = async (credentials) => {
    try {
      const response = await loginApi(credentials)

      if (response.token && response.user) {
        token.value = response.token
        user.value = response.user

        // 保存到 localStorage
        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))

        return true
      }
      return false
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 初始化用户信息
  const initUser = () => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (error) {
        console.error('解析用户信息失败:', error)
        localStorage.removeItem('user')
      }
    }
  }

  initUser()

  return {
    user,
    token,
    isAuthenticated,
    isAdmin,
    login,
    logout
  }
})