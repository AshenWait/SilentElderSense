import request from './index'

// 创建检测会话
export function createSession() {
  return request({
    url: '/session/create',
    method: 'post'
  })
}

// 关闭检测会话
export function closeSession(videoId) {
  return request({
    url: `/session/close/${videoId}`,
    method: 'post'
  })
}

// 上传视频文件
export function uploadVideo(file) {
  const formData = new FormData()
  formData.append('video', file)

  return request({
    url: '/video/upload',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000  // 5分钟超时
  })
}

// WebSocket 实时检测（摄像头）
export function createDetectWebSocket(videoId) {
  return new WebSocket(`ws://localhost:8000/ws/detect/${videoId}`)
}

// WebSocket 视频处理
export function createVideoProcessWebSocket(videoId) {
  return new WebSocket(`ws://localhost:8000/ws/video/${videoId}`)
}
