/**
 * WebSocket 实时视频流服务
 * 用于流式上传视频帧和接收实时检测结果
 */

class VideoWebSocket {
  constructor() {
    this.ws = null
    this.isConnected = false
    this.messageQueue = []
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 3000
    this.onFrameCallback = null
    this.onDetectionCallback = null
    this.onErrorCallback = null
    this.onConnectCallback = null
    this.onDisconnectCallback = null
  }

  /**
   * 连接 WebSocket
   * @param {string} url WebSocket 地址
   */
  connect(url) {
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
      // 处理消息队列
      this.processMessageQueue()
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
      // 自动重连
      this.attemptReconnect(url)
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
   * 发送视频帧
   * @param {string} frameData Base64 编码的图片数据
   * @param {number} timestamp 时间戳
   * @param {string} videoId 视频 ID
   */
  sendFrame(frameData, timestamp, videoId) {
    const message = {
      type: 'frame',
      data: {
        frame: frameData,
        timestamp: timestamp,
        videoId: videoId
      }
    }
    this.sendMessage(message)
  }

  /**
   * 开始视频流
   * @param {string} videoId 视频 ID
   * @param {object} options 配置选项
   */
  startVideoStream(videoId, options = {}) {
    const message = {
      type: 'start',
      data: {
        videoId: videoId,
        options: options
      }
    }
    this.sendMessage(message)
  }

  /**
   * 停止视频流
   * @param {string} videoId 视频 ID
   */
  stopVideoStream(videoId) {
    const message = {
      type: 'stop',
      data: {
        videoId: videoId
      }
    }
    this.sendMessage(message)
  }

  /**
   * 发送消息
   * @param {object} message 消息对象
   */
  sendMessage(message) {
    if (this.isConnected) {
      try {
        this.ws.send(JSON.stringify(message))
      } catch (error) {
        console.error('发送消息失败:', error)
      }
    } else {
      // 连接未建立时，将消息加入队列
      this.messageQueue.push(message)
    }
  }

  /**
   * 处理消息队列
   */
  processMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift()
      this.sendMessage(message)
    }
  }

  /**
   * 处理接收到的消息
   * @param {object} data 消息数据
   */
  handleMessage(data) {
    switch (data.type) {
      case 'frame':
        // 处理处理后的帧
        if (this.onFrameCallback) {
          this.onFrameCallback(data.data)
        }
        break
      case 'detection':
        // 处理检测结果
        if (this.onDetectionCallback) {
          this.onDetectionCallback(data.data)
        }
        break
      case 'error':
        console.error('服务器错误:', data.message)
        if (this.onErrorCallback) {
          this.onErrorCallback(new Error(data.message))
        }
        break
      default:
        console.warn('未知消息类型:', data.type)
    }
  }

  /**
   * 尝试重连
   * @param {string} url WebSocket 地址
   */
  attemptReconnect(url) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      setTimeout(() => {
        this.connect(url)
      }, this.reconnectDelay)
    } else {
      console.error('达到最大重连次数，停止重连')
    }
  }

  /**
   * 设置回调函数
   */
  onFrame(callback) {
    this.onFrameCallback = callback
  }

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