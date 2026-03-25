<template>
  <div class="video-stream-uploader">
    <!-- 上传控制区 -->
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span>流式视频上传</span>
          <el-tag :type="connectionStatusType" size="small">
            {{ connectionStatusText }}
          </el-tag>
        </div>
      </template>

      <div class="upload-controls">
        <el-upload
          ref="uploadRef"
          class="video-uploader"
          :auto-upload="false"
          :show-file-list="false"
          accept="video/*"
          :on-change="handleFileChange"
        >
          <el-button type="primary" :icon="VideoCamera">
            选择视频文件
          </el-button>
        </el-upload>

        <el-button
          type="success"
          :icon="VideoPlay"
          :disabled="!selectedFile || isProcessing"
          @click="startStreaming"
        >
          开始上传
        </el-button>

        <el-button
          type="danger"
          :icon="VideoPause"
          :disabled="!isProcessing"
          @click="stopStreaming"
        >
          停止上传
        </el-button>

        <el-progress
          v-if="isProcessing"
          :percentage="uploadProgress"
          :status="uploadProgress === 100 ? 'success' : undefined"
          class="upload-progress"
        />
      </div>

      <div v-if="selectedFile" class="file-info">
        <span>文件: {{ selectedFile.name }}</span>
        <span>大小: {{ formatFileSize(selectedFile.size) }}</span>
      </div>
    </el-card>

    <!-- 视频预览区 -->
    <el-row :gutter="20" class="preview-row">
      <!-- 原始视频 -->
      <el-col :span="12">
        <el-card class="preview-card">
          <template #header>
            <span>原始视频</span>
          </template>
          <div class="video-container">
            <video
              ref="originalVideoRef"
              class="video-element"
              :src="originalVideoUrl"
              controls
              muted
              @timeupdate="handleTimeUpdate"
            ></video>
          </div>
        </el-card>
      </el-col>

      <!-- 处理后的视频 -->
      <el-col :span="12">
        <el-card class="preview-card">
          <template #header>
            <span>处理后视频</span>
          </template>
          <div class="video-container">
            <canvas
              ref="processedCanvasRef"
              class="canvas-element"
              width="640"
              height="480"
            ></canvas>
            <div v-if="!isProcessing" class="placeholder">
              <el-icon class="placeholder-icon"><VideoCamera /></el-icon>
              <p>等待视频上传</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时检测结果 -->
    <el-card class="detection-card">
      <template #header>
        <span>实时检测结果</span>
      </template>
      <div class="detection-results">
        <div v-if="detectionResults.length === 0" class="no-results">
          暂无检测结果
        </div>
        <div v-else class="results-list">
          <div
            v-for="(result, index) in detectionResults"
            :key="index"
            class="result-item"
            :class="`result-${result.riskLevel}`"
          >
            <div class="result-header">
              <el-tag :type="getRiskTagType(result.riskLevel)" size="small">
                {{ result.typeName }}
              </el-tag>
              <span class="result-time">{{ result.timestamp }}</span>
            </div>
            <div class="result-details">
              <span>置信度: {{ (result.confidence * 100).toFixed(1) }}%</span>
              <span v-if="result.description">描述: {{ result.description }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { VideoCamera, VideoPlay, VideoPause } from '@element-plus/icons-vue'
import { videoWebSocket } from '@/utils/websocket'

const uploadRef = ref(null)
const originalVideoRef = ref(null)
const processedCanvasRef = ref(null)

const selectedFile = ref(null)
const originalVideoUrl = ref('')
const isProcessing = ref(false)
const uploadProgress = ref(0)
const connectionStatus = ref('disconnected')

const detectionResults = ref([])
const videoId = ref('')
let frameInterval = null
let canvasContext = null

// WebSocket 连接状态
const connectionStatusType = computed(() => {
  const map = {
    connected: 'success',
    connecting: 'warning',
    disconnected: 'info',
    error: 'danger'
  }
  return map[connectionStatus.value] || 'info'
})

const connectionStatusText = computed(() => {
  const map = {
    connected: '已连接',
    connecting: '连接中...',
    disconnected: '未连接',
    error: '连接错误'
  }
  return map[connectionStatus.value] || '未知'
})

// 初始化 WebSocket
onMounted(() => {
  canvasContext = processedCanvasRef.value?.getContext('2d')
  setupWebSocketCallbacks()
})

onUnmounted(() => {
  stopStreaming()
  videoWebSocket.disconnect()
})

// 设置 WebSocket 回调
const setupWebSocketCallbacks = () => {
  videoWebSocket.onConnect(() => {
    connectionStatus.value = 'connected'
    console.log('WebSocket 已连接')
  })

  videoWebSocket.onDisconnect(() => {
    connectionStatus.value = 'disconnected'
    console.log('WebSocket 已断开')
  })

  videoWebSocket.onError((error) => {
    connectionStatus.value = 'error'
    console.error('WebSocket 错误:', error)
  })

  videoWebSocket.onFrame((data) => {
    displayProcessedFrame(data.frame)
  })

  videoWebSocket.onDetection((data) => {
    handleDetectionResult(data)
  })
}

// 处理文件选择
const handleFileChange = (file) => {
  selectedFile.value = file.raw
  originalVideoUrl.value = URL.createObjectURL(file.raw)
  detectionResults.value = []
  uploadProgress.value = 0
}

// 开始流式上传
const startStreaming = () => {
  if (!selectedFile.value) return

  // 连接 WebSocket
  const wsUrl = 'ws://localhost:8000/ws/video'
  videoWebSocket.connect(wsUrl)

  connectionStatus.value = 'connecting'
  isProcessing.value = true

  // 生成视频 ID
  videoId.value = `video_${Date.now()}`

  // 等待连接建立后开始发送帧
  const checkConnection = setInterval(() => {
    if (videoWebSocket.isReady()) {
      clearInterval(checkConnection)
      videoWebSocket.startVideoStream(videoId.value, {
        fps: 30,
        enableBlur: true
      })
      startFrameSending()
    }
  }, 100)
}

// 停止流式上传
const stopStreaming = () => {
  isProcessing.value = false
  uploadProgress.value = 0

  if (frameInterval) {
    clearInterval(frameInterval)
    frameInterval = null
  }

  if (videoId.value) {
    videoWebSocket.stopVideoStream(videoId.value)
  }

  if (originalVideoRef.value) {
    originalVideoRef.value.pause()
  }
}

// 开始发送帧
const startFrameSending = () => {
  const video = originalVideoRef.value
  if (!video) return

  video.currentTime = 0
  video.play()

  frameInterval = setInterval(() => {
    if (!isProcessing.value || video.ended) {
      stopStreaming()
      return
    }

    // 捕获当前帧
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth || 640
    canvas.height = video.videoHeight || 480
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    // 转换为 Base64
    const frameData = canvas.toDataURL('image/jpeg', 0.8)

    // 发送到后端
    videoWebSocket.sendFrame(frameData, video.currentTime, videoId.value)

    // 更新进度
    uploadProgress.value = (video.currentTime / video.duration) * 100
  }, 1000 / 30) // 30 FPS
}

// 显示处理后的帧
const displayProcessedFrame = (frameData) => {
  if (!canvasContext || !processedCanvasRef.value) return

  const img = new Image()
  img.onload = () => {
    canvasContext.clearRect(0, 0, processedCanvasRef.value.width, processedCanvasRef.value.height)
    canvasContext.drawImage(img, 0, 0, processedCanvasRef.value.width, processedCanvasRef.value.height)
  }
  img.src = frameData
}

// 处理检测结果
const handleDetectionResult = (data) => {
  const result = {
    typeName: getTypeName(data.type),
    type: data.type,
    riskLevel: data.riskLevel || 'low',
    confidence: data.confidence || 0,
    timestamp: formatTimestamp(data.timestamp),
    description: data.description || ''
  }

  detectionResults.value.unshift(result)

  // 只保留最近 20 条结果
  if (detectionResults.value.length > 20) {
    detectionResults.value = detectionResults.value.slice(0, 20)
  }
}

// 处理视频时间更新
const handleTimeUpdate = () => {
  // 可以在这里添加额外的时间更新逻辑
}

// 工具函数
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN')
}

const getTypeName = (type) => {
  const map = {
    fall: '跌倒检测',
    stillness: '长时间静止',
    normal: '正常活动',
    night_activity: '夜间异常活动'
  }
  return map[type] || type
}

const getRiskTagType = (level) => {
  const map = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return map[level] || 'info'
}
</script>

<style scoped>
.video-stream-uploader {
  width: 100%;
}

.upload-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.upload-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.upload-progress {
  width: 300px;
}

.file-info {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #666;
}

.preview-row {
  margin-bottom: 20px;
}

.preview-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: 400px;
}

.video-container {
  height: 320px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-element,
.canvas-element {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: rgba(255, 255, 255, 0.5);
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.detection-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.detection-results {
  max-height: 400px;
  overflow-y: auto;
}

.no-results {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  border-left: 3px solid;
}

.result-high {
  border-left-color: #f56c6c;
}

.result-medium {
  border-left-color: #e6a23c;
}

.result-low {
  border-left-color: #67c23a;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.result-time {
  font-size: 12px;
  color: #666;
}

.result-details {
  display: flex;
  gap: 15px;
  font-size: 13px;
  color: #666;
}
</style>