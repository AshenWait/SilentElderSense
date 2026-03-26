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

// ========== 摄像头相关 API ==========

/**
 * 获取可用摄像头设备列表
 * @returns {Promise<MediaDeviceInfo[]>} 摄像头设备列表
 */
export async function getCameraDevices() {
  try {
    // 先请求权限，获取临时流
    const tempStream = await navigator.mediaDevices.getUserMedia({ video: true })

    // 立即关闭临时流
    tempStream.getTracks().forEach(track => track.stop())

    // 枚举设备（此时应该有标签）
    const devices = await navigator.mediaDevices.enumerateDevices()
    const videoDevices = devices.filter(device => device.kind === 'videoinput')

    console.log('找到摄像头设备:', videoDevices.length, videoDevices)
    return videoDevices
  } catch (error) {
    console.error('获取摄像头设备失败:', error)
    throw error
  }
}

/**
 * 获取摄像头媒体流
 * @param {Object} constraints - 媒体约束
 * @param {string} constraints.deviceId - 摄像头设备ID
 * @param {number} constraints.width - 视频宽度
 * @param {number} constraints.height - 视频高度
 * @returns {Promise<MediaStream>} 媒体流
 */
export async function getCameraStream(constraints = {}) {
  const finalConstraints = {
    video: {
      width: { ideal: constraints.width || 640 },
      height: { ideal: constraints.height || 480 },
      ...(constraints.deviceId ? { deviceId: { exact: constraints.deviceId } } : { facingMode: 'user' })
    }
  }

  try {
    return await navigator.mediaDevices.getUserMedia(finalConstraints)
  } catch (error) {
    console.error('获取摄像头流失败:', error)
    throw error
  }
}

/**
 * 停止媒体流
 * @param {MediaStream} stream - 媒体流
 */
export function stopStream(stream) {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
  }
}
