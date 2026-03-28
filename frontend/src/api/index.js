import axios from 'axios'
import router from '@/router'

// 创建axios实例
const request = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    // 检查是否有错误
    if (response.status >= 400) {
      console.error('响应错误:', res.error || res.message)
      return Promise.reject(new Error(res.error || res.message || 'Error'))
    }
    return res
  },
  error => {
    console.error('响应错误:', error)
    // 401 未授权：清除登录状态，跳转登录页
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
      return Promise.reject(new Error('登录已过期，请重新登录'))
    }
    if (error.response) {
      const errorData = error.response.data
      return Promise.reject(new Error(errorData.error || errorData.message || '请求失败'))
    }
    return Promise.reject(error)
  }
)

export default request