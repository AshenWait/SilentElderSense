import request from './index'

// 获取告警配置
export function getAlertConfig() {
  return request({
    url: '/alerts/config',
    method: 'get'
  })
}

// 更新告警配置
export function updateAlertConfig(data) {
  return request({
    url: '/alerts/config',
    method: 'put',
    data
  })
}

// 获取告警历史
export function getAlertHistory(params) {
  return request({
    url: '/alerts/history',
    method: 'get',
    params
  })
}

// 手动触发告警
export function triggerAlert(data) {
  return request({
    url: '/alerts/trigger',
    method: 'post',
    data
  })
}

// 重发告警
export function resendAlert(alertId) {
  return request({
    url: `/alerts/${alertId}/send`,
    method: 'post'
  })
}

// 确认告警
export function acknowledgeAlert(alertId) {
  return request({
    url: `/alerts/${alertId}/acknowledge`,
    method: 'post'
  })
}

// 获取告警统计
export function getAlertStats(params) {
  return request({
    url: '/alerts/stats',
    method: 'get',
    params
  })
}