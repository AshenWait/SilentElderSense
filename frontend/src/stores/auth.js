import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  // 同时检查 token 和 user 才认为已登录
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.username === 'admin')

  const login = async (credentials) => {
    try {
      const response = await loginApi(credentials)

      // 后端返回格式: { message, user_id, username, access_token }
      if (response.user_id && response.username) {
        user.value = {
          id: response.user_id,
          username: response.username
        }

        // 保存 token 到 localStorage
        if (response.access_token) {
          token.value = response.access_token
          localStorage.setItem('token', response.access_token)
        }

        // 保存用户信息到 localStorage
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

  // 初始化用户信息（必须同时有 token 和 user）
  const initUser = () => {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')

    // 只有两者都存在才恢复登录状态
    if (savedToken && savedUser) {
      try {
        user.value = JSON.parse(savedUser)
        token.value = savedToken
      } catch (error) {
        console.error('解析用户信息失败:', error)
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    } else {
      // 清除不完整的登录状态
      localStorage.removeItem('token')
      localStorage.removeItem('user')
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
