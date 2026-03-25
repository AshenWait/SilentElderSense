/**
 * WebSocket 实时视频流服务
 * 用于流式上传视频帧和接收实时检测结果
 *
 * 后端 WebSocket 接口: ws://localhost:8000/ws/detect/<video_id>
 * 发送: JPEG 字节流或 base64 编码字符串
 * 接收: JSON 检测结果
 */

class VideoWebSocket {
  constructor() {
    this.ws = null
    this.videoId = null
    this.isConnected = false
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 3000
    this.onDetectionCallback = null
    this.onErrorCallback = null
    this.onConnectCallback = null
    this.onDisconnectCallback = null
  }

  /**
   * 连接 WebSocket
   * @param {string} videoId 视频会话ID
   */
  connect(videoId) {
    this.videoId = videoId
    const url = `ws://localhost:8000/ws/detect/${videoId}`

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket 已经连接')
      return
    }

    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log('WebSocket 连接成功')
      this.isConnected = true
      this.reconnectAttempts = 0
      if (this.onConnectCallback) {
        this.onConnectCallback()
      }
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.handleMessage(data)
      } catch (error) {
        console.error('解析 WebSocket 消息失败:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket 错误:', error)
      if (this.onErrorCallback) {
        this.onErrorCallback(error)
      }
    }

    this.ws.onclose = () => {
      console.log('WebSocket 连接关闭')
      this.isConnected = false
      if (this.onDisconnectCallback) {
        this.onDisconnectCallback()
      }
    }
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
      this.isConnected = false
    }
  }

  /**
   * 发送视频帧 (JPEG 字节流)
   * @param {Blob|ArrayBuffer} frameData JPEG 格式的图片数据
   */
  sendFrame(frameData) {
    if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(frameData)
    } else {
      console.warn('WebSocket 未连接，无法发送帧数据')
    }
  }

  /**
   * 发送 Base64 编码的视频帧
   * @param {string} base64Data Base64 编码的图片数据
   */
  sendBase64Frame(base64Data) {
    if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(base64Data)
    } else {
      console.warn('WebSocket 未连接，无法发送帧数据')
    }
  }

  /**
   * 处理接收到的消息
   * @param {object} data 消息数据
   *
   * 后端返回格式:
   * {
   *   "detected": true,
   *   "persons": [{ "person_id": 0, "class_name": "normal", "confidence": 0.95, "box": [x1, y1, x2, y2] }],
   *   "events": [{ "person_id": 0, "event_type": "FALL", "risk_level": "HIGH", "duration": 1.5 }]
   * }
   */
  handleMessage(data) {
    if (data.error) {
      console.error('服务器错误:', data.error)
      if (this.onErrorCallback) {
        this.onErrorCallback(new Error(data.error))
      }
      return
    }

    // 检测结果
    if (this.onDetectionCallback) {
      this.onDetectionCallback(data)
    }
  }

  /**
   * 设置回调函数
   */
  onDetection(callback) {
    this.onDetectionCallback = callback
  }

  onError(callback) {
    this.onErrorCallback = callback
  }

  onConnect(callback) {
    this.onConnectCallback = callback
  }

  onDisconnect(callback) {
    this.onDisconnectCallback = callback
  }

  /**
   * 检查连接状态
   */
  isReady() {
    return this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

// 创建单例
export const videoWebSocket = new VideoWebSocket()

export default VideoWebSocket
