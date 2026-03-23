import request from './index'

// 场景管理
export function getScenes() {
  return request({
    url: '/system/scenes',
    method: 'get'
  })
}

export function createScene(data) {
  return request({
    url: '/system/scenes',
    method: 'post',
    data
  })
}

export function updateScene(id, data) {
  return request({
    url: `/system/scenes/${id}`,
    method: 'put',
    data
  })
}

export function deleteScene(id) {
  return request({
    url: `/system/scenes/${id}`,
    method: 'delete'
  })
}

// 监测时段管理
export function getTimePeriods() {
  return request({
    url: '/system/time-periods',
    method: 'get'
  })
}

export function createTimePeriod(data) {
  return request({
    url: '/system/time-periods',
    method: 'post',
    data
  })
}

export function updateTimePeriod(id, data) {
  return request({
    url: `/system/time-periods/${id}`,
    method: 'put',
    data
  })
}

export function deleteTimePeriod(id) {
  return request({
    url: `/system/time-periods/${id}`,
    method: 'delete'
  })
}

// 告警规则管理
export function getAlertRules() {
  return request({
    url: '/system/alert-rules',
    method: 'get'
  })
}

export function createAlertRule(data) {
  return request({
    url: '/system/alert-rules',
    method: 'post',
    data
  })
}

export function updateAlertRule(id, data) {
  return request({
    url: `/system/alert-rules/${id}`,
    method: 'put',
    data
  })
}

export function deleteAlertRule(id) {
  return request({
    url: `/system/alert-rules/${id}`,
    method: 'delete'
  })
}

// 用户管理
export function getUsers() {
  return request({
    url: '/system/users',
    method: 'get'
  })
}

export function createUser(data) {
  return request({
    url: '/system/users',
    method: 'post',
    data
  })
}

export function updateUser(id, data) {
  return request({
    url: `/system/users/${id}`,
    method: 'put',
    data
  })
}

export function deleteUser(id) {
  return request({
    url: `/system/users/${id}`,
    method: 'delete'
  })
}

// 系统设置
export function getSystemSettings() {
  return request({
    url: '/system/settings',
    method: 'get'
  })
}

export function updateSystemSettings(data) {
  return request({
    url: '/system/settings',
    method: 'put',
    data
  })
}