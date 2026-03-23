import request from './index'

// 获取事件列表
export function getEvents(params) {
  return request({
    url: '/events',
    method: 'get',
    params
  })
}

// 获取事件详情
export function getEventDetail(id) {
  return request({
    url: `/events/${id}`,
    method: 'get'
  })
}

// 更新事件状态
export function updateEventStatus(id, data) {
  return request({
    url: `/events/${id}/status`,
    method: 'put',
    data
  })
}

// 获取事件统计
export function getEventStatistics(params) {
  return request({
    url: '/events/statistics',
    method: 'get',
    params
  })
}

// 获取事件趋势
export function getEventTrend(params) {
  return request({
    url: '/events/trend',
    method: 'get',
    params
  })
}

// 获取位置分布
export function getLocationDistribution(params) {
  return request({
    url: '/events/location-distribution',
    method: 'get',
    params
  })
}

// 导出事件报告
export function exportEventReport(params) {
  return request({
    url: '/events/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}