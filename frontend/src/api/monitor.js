import request from './index'

// 获取摄像头列表
export function getCameras() {
  return request({
    url: '/monitor/cameras',
    method: 'get'
  })
}

// 获取摄像头详情
export function getCameraDetail(id) {
  return request({
    url: `/monitor/cameras/${id}`,
    method: 'get'
  })
}

// 启动监控
export function startMonitoring(cameraId) {
  return request({
    url: '/monitor/start',
    method: 'post',
    data: { cameraId }
  })
}

// 停止监控
export function stopMonitoring(cameraId) {
  return request({
    url: '/monitor/stop',
    method: 'post',
    data: { cameraId }
  })
}

// 获取实时状态
export function getRealTimeStatus(cameraId) {
  return request({
    url: '/monitor/status',
    method: 'get',
    params: { cameraId }
  })
}

// 获取监控日志
export function getMonitorLogs(params) {
  return request({
    url: '/monitor/logs',
    method: 'get',
    params
  })
}

// 获取实时检测结果
export function getRealTimeDetection(cameraId) {
  return request({
    url: '/monitor/detection',
    method: 'get',
    params: { cameraId }
  })
}