import request from './index'

// 登录
export function login(data) {
  return request({
    url: '/login',
    method: 'post',
    data
  })
}

// 登出
export function logout() {
  return request({
    url: '/logout',
    method: 'post'
  })
}

// 获取用户信息
export function getUserInfo() {
  return request({
    url: '/userinfo',
    method: 'get'
  })
}

// 刷新token
export function refreshToken() {
  return request({
    url: '/refresh',
    method: 'post'
  })
}