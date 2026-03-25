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

// WebSocket 实时检测
// 使用方式：
// const ws = new WebSocket(`ws://localhost:8000/ws/detect/${videoId}`)
// ws.onopen = () => { ... }
// ws.onmessage = (event) => { const result = JSON.parse(event.data) }
// ws.send(frameData) // 发送 JPEG 字节流或 base64 编码
export function createDetectWebSocket(videoId) {
  return new WebSocket(`ws://localhost:8000/ws/detect/${videoId}`)
}
