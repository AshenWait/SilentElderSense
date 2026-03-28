import request from './index'

// 获取检测配置
export function getDetectConfig() {
  return request({
    url: '/detect/config',
    method: 'get'
  })
}

// 更新检测配置（需要管理员权限）
export function updateDetectConfig(data) {
  return request({
    url: '/detect/config',
    method: 'put',
    data
  })
}