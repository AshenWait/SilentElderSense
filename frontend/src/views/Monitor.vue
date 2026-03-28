<template>
  <div class="monitor">
    <!-- 控制面板 -->
    <el-card class="control-panel">
      <div class="panel-content">
        <div class="session-info">
          <span class="label">会话状态：</span>
          <el-tag :type="isConnected ? 'success' : 'info'">
            {{ isConnected ? '已连接' : '未连接' }}
          </el-tag>
          <span v-if="videoId" class="video-id">会话ID: {{ videoId }}</span>
        </div>
        <div class="actions">
          <!-- 摄像头选择 -->
          <el-select
            v-model="selectedCameraId"
            placeholder="选择摄像头"
            :disabled="isConnected"
            style="width: 200px"
            @change="onCameraSelect"
          >
            <el-option
              v-for="(camera, index) in cameraDevices"
              :key="camera.deviceId"
              :label="camera.label || `摄像头 ${index + 1}`"
              :value="camera.deviceId"
            />
          </el-select>
          <el-button
            :icon="RefreshRight"
            @click="loadCameraDevices"
            :disabled="isConnected"
            title="刷新摄像头列表"
          />
          <el-button
            type="danger"
            :icon="VideoPause"
            @click="stopSession"
            :disabled="!isConnected"
          >
            停止检测
          </el-button>
        </div>
      </div>
      <div v-if="isConnected" class="camera-info">
        <el-tag type="success">摄像头运行中</el-tag>
        <span class="fps-info">帧率: {{ currentFps }} FPS</span>
        <span class="duration-info">时长: {{ formatDuration(cameraDuration) }}</span>
        <span class="processed-info">已处理: {{ processedCount }} 帧</span>
        <span class="latency-info" :class="{ 'latency-high': latencyMs > 200 }">延迟: {{ latencyMs }}ms</span>
        <span v-if="skippedCount > 0" class="skipped-info">跳帧: {{ skippedCount }}</span>
      </div>
    </el-card>

    <!-- 监控区域 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="video-card">
          <template #header>
            <div class="card-header">
              <span>摄像头监控</span>
              <el-tag v-if="isConnected" type="success">检测中</el-tag>
            </div>
          </template>

          <div class="video-container">
            <!-- 占位提示 -->
            <div v-show="!isConnected" class="placeholder">
              <el-icon class="placeholder-icon"><VideoCamera /></el-icon>
              <p>选择摄像头开始检测</p>
            </div>

            <!-- 帧画布（与视频检测一致） -->
            <canvas
              ref="canvasRef"
              class="frame-canvas"
              v-show="isConnected"
            ></canvas>

            <!-- 叠加信息 -->
            <div v-if="isConnected" class="overlay-info">
              <div class="info-item">
                <span class="label">检测人数：</span>
                <span class="value">{{ detectionResult.persons?.length || 0 }}</span>
              </div>
              <div class="info-item">
                <span class="label">风险人数：</span>
                <span class="value">{{ riskyPersonCount }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="info-card">
          <template #header>
            <span>检测结果</span>
          </template>

          <div class="detection-info">
            <div v-if="!isConnected" class="no-data">
              <p>等待连接...</p>
            </div>
            <template v-else>
              <div class="section">
                <h4>风险状态</h4>
                <div v-if="detectionResult.persons?.length" class="person-list">
                  <div v-for="person in detectionResult.persons" :key="person.person_id" class="person-item">
                    <el-tag :type="getRiskTagType(person.risk_level)" size="small">
                      {{ getRiskLabel(person.risk_level, person.risk_reason) }}
                    </el-tag>
                    <span class="person-id">ID: {{ person.person_id }}</span>
                  </div>
                </div>
                <el-empty v-else description="暂无检测结果" :image-size="60" />
              </div>

              <div class="section" v-if="allEvents.length > 0">
                <h4>历史风险记录 ({{ allEvents.length }})</h4>
                <div class="event-list scrollable">
                  <div v-for="event in allEvents.slice().reverse()" :key="event.id" class="event-item small">
                    <el-tag :type="getRiskTagType(event.risk_level)" size="small">
                      {{ getEventTypeLabel(event.event_type) }} - {{ event.risk_level }}
                    </el-tag>
                    <span class="time">ID: {{ event.person_id }} | {{ event.duration?.toFixed(1) || 0 }}秒</span>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { VideoPause, VideoCamera, RefreshRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { createSession, closeSession, getCameraDevices, stopStream } from '@/api/monitor'
import { getEvents } from '@/api/events'
import { getRiskTagType, getRiskLabel, getEventTypeLabel } from '@/utils/risk'

// 摄像头
const cameraDevices = ref([])
const selectedCameraId = ref('')
const cameraStream = ref(null)
const currentFps = ref(0)
const cameraDuration = ref(0)
const processedCount = ref(0)
const latencyMs = ref(0)
const skippedCount = ref(0)

// 通用
const canvasRef = ref(null)
const videoId = ref('')
const isConnected = ref(false)
const allEvents = ref([])

const detectionResult = ref({
  persons: [],
})

// 计算属性
const riskyPersonCount = computed(() => {
  return (detectionResult.value.persons || []).filter(p => p.risk_level !== 'NORMAL').length
})

let ws = null
let sendFrameCanvas = null
let sendFrameCtx = null
let videoElement = null
let cameraStartTime = null
let fpsCounter = 0
let fpsInterval = null
let eventRefreshInterval = null  // 事件刷新定时器
let canSendFrame = true  // 控制发送节奏

// 获取事件列表
const fetchEvents = async () => {
  try {
    const res = await getEvents({ per_page: 20 })
    allEvents.value = res.events || []
  } catch (e) {
    console.error('获取事件列表失败:', e)
  }
}

const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 获取摄像头列表
const loadCameraDevices = async () => {
  try {
    ElMessage.info('正在请求摄像头权限...')
    const devices = await getCameraDevices()
    cameraDevices.value = devices

    if (devices.length > 0) {
      const deviceWithLabel = devices.find(d => d.label)
      selectedCameraId.value = deviceWithLabel ? deviceWithLabel.deviceId : devices[0].deviceId
      ElMessage.success(`找到 ${devices.length} 个摄像头设备`)
    } else {
      ElMessage.warning('未找到摄像头设备')
    }
  } catch (error) {
    console.error('获取摄像头设备失败:', error)
    if (error.name === 'NotAllowedError') {
      ElMessage.error('摄像头权限被拒绝，请在浏览器设置中允许访问摄像头')
    } else if (error.name === 'NotFoundError') {
      ElMessage.error('未找到摄像头设备，请确保摄像头已连接')
    } else {
      ElMessage.error('获取摄像头失败: ' + error.message)
    }
  }
}

// 选择摄像头后自动开始检测
const onCameraSelect = async (deviceId) => {
  if (!deviceId || isConnected.value) return
  await startCameraDetection()
}

// 摄像头检测
const startCameraDetection = async () => {
  if (!selectedCameraId.value) {
    ElMessage.warning('请先选择摄像头')
    return
  }

  try {
    // 获取摄像头流
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        deviceId: { exact: selectedCameraId.value },
        width: { ideal: 640 },
        height: { ideal: 480 }
      }
    })
    cameraStream.value = stream

    // 创建隐藏的 video 元素用于提取帧
    videoElement = document.createElement('video')
    videoElement.srcObject = stream
    videoElement.muted = true
    videoElement.playsInline = true

    await videoElement.play()

    // 创建检测会话
    const response = await createSession()
    videoId.value = response.video_id

    // 连接 WebSocket
    ws = new WebSocket(`ws://localhost:8000/ws/detect/${videoId.value}`)

    ws.onopen = () => {
      isConnected.value = true
      cameraStartTime = Date.now()
      processedCount.value = 0
      ElMessage.success('摄像头检测已启动')
      startCameraFrameSending()
      startFpsCounter()
      // 每秒刷新事件列表
      fetchEvents()
      eventRefreshInterval = setInterval(fetchEvents, 1000)
    }

    ws.onmessage = (event) => {
      // 收到响应，允许发送下一帧
      canSendFrame = true

      try {
        const data = JSON.parse(event.data)
        if (data.type === 'error') {
          ElMessage.error(data.message)
        } else if (data.type === 'frame') {
          // 与视频检测一致的渲染逻辑
          detectionResult.value = { persons: data.persons || [] }
          renderFrame(data)
          processedCount.value = data.frame_id || processedCount.value + 1
          latencyMs.value = data.latency_ms || 0
          skippedCount.value = data.skipped || 0
        }
      } catch (e) {
        console.error('解析检测结果失败:', e)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket 错误:', error)
      ElMessage.error('连接错误')
    }

    ws.onclose = () => {
      isConnected.value = false
      stopFpsCounter()
      // 停止事件刷新
      if (eventRefreshInterval) {
        clearInterval(eventRefreshInterval)
        eventRefreshInterval = null
      }
      // 最后刷新一次事件列表
      fetchEvents()
    }
  } catch (error) {
    console.error('启动摄像头失败:', error)
    ElMessage.error('启动摄像头失败: ' + error.message)
  }
}

// FPS 计数
const startFpsCounter = () => {
  fpsCounter = 0
  fpsInterval = setInterval(() => {
    currentFps.value = fpsCounter
    fpsCounter = 0
    if (cameraStartTime) {
      cameraDuration.value = Math.floor((Date.now() - cameraStartTime) / 1000)
    }
  }, 1000)
}

const stopFpsCounter = () => {
  if (fpsInterval) {
    clearInterval(fpsInterval)
    fpsInterval = null
  }
  currentFps.value = 0
}

// 摄像头发送帧（收到响应后才发送下一帧，避免队列堆积）
const startCameraFrameSending = () => {
  sendFrameCanvas = document.createElement('canvas')
  sendFrameCanvas.width = 640
  sendFrameCanvas.height = 480
  sendFrameCtx = sendFrameCanvas.getContext('2d')

  const sendFrame = () => {
    if (!isConnected.value || !videoElement) {
      return
    }

    // 只有收到上一帧响应后才发送新帧
    if (!canSendFrame) {
      requestAnimationFrame(sendFrame)
      return
    }

    sendFrameCtx.drawImage(videoElement, 0, 0, sendFrameCanvas.width, sendFrameCanvas.height)

    sendFrameCanvas.toBlob((blob) => {
      if (blob && ws && ws.readyState === WebSocket.OPEN) {
        canSendFrame = false  // 等待响应
        blob.arrayBuffer().then(buffer => {
          ws.send(buffer)
          fpsCounter++
        })
      }
    }, 'image/jpeg', 0.8)

    requestAnimationFrame(sendFrame)
  }

  requestAnimationFrame(sendFrame)
}

// 渲染帧（与 VideoDetect.vue 一致）
const renderFrame = (data) => {
  if (!data.image || !canvasRef.value) return

  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')

  // 解码 hex 为 bytes
  const hex = data.image
  const bytes = new Uint8Array(hex.length / 2)
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substr(i, 2), 16)
  }

  // 创建图像并显示（检测框已在后端绘制）
  const blob = new Blob([bytes], { type: 'image/jpeg' })
  const img = new Image()
  img.onload = () => {
    canvas.width = img.width
    canvas.height = img.height
    ctx.drawImage(img, 0, 0)
    URL.revokeObjectURL(img.src)
  }
  img.onerror = (e) => {
    console.error('[渲染] 图片加载失败:', e)
  }
  img.src = URL.createObjectURL(blob)
}

// 停止会话
const stopSession = async () => {
  // 停止摄像头流
  if (cameraStream.value) {
    stopStream(cameraStream.value)
    cameraStream.value = null
  }

  if (videoElement) {
    videoElement.srcObject = null
    videoElement = null
  }

  sendFrameCanvas = null
  sendFrameCtx = null
  cameraStartTime = null
  stopFpsCounter()

  if (ws) {
    ws.close()
    ws = null
  }

  if (videoId.value) {
    try {
      await closeSession(videoId.value)
      ElMessage.success('会话已关闭')
    } catch (error) {
      console.error('关闭会话失败:', error)
    }
  }

  videoId.value = ''
  isConnected.value = false
  detectionResult.value = { persons: [] }
  processedCount.value = 0
  latencyMs.value = 0
  skippedCount.value = 0
}

onMounted(() => {
  if (canvasRef.value) {
    canvasRef.value.width = 640
    canvasRef.value.height = 480
  }
  loadCameraDevices()
})

onUnmounted(() => {
  stopSession()
})
</script>

<style scoped>
.monitor {
  width: 100%;
}

.control-panel {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.panel-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.session-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.session-info .label {
  font-weight: 500;
  color: #666;
}

.video-id {
  color: #999;
  font-size: 12px;
}

.actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.camera-info {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 12px;
}

.fps-info, .duration-info, .processed-info, .latency-info, .skipped-info {
  color: #999;
  font-size: 12px;
}

.latency-info.latency-high {
  color: #f56c6c;
  font-weight: 500;
}

.skipped-info {
  color: #e6a23c;
}

.video-card, .info-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.video-container {
  width: 100%;
  height: 400px;
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
}

.placeholder-icon {
  font-size: 64px;
  margin-bottom: 15px;
}

.frame-canvas {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

.overlay-info {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.6);
  padding: 10px;
  border-radius: 6px;
}

.overlay-info .info-item {
  color: #fff;
  font-size: 14px;
  margin-bottom: 5px;
}

.overlay-info .info-item:last-child {
  margin-bottom: 0;
}

.detection-info {
  max-height: 400px;
  overflow-y: auto;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.section {
  margin-bottom: 20px;
}

.section h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #333;
}

.person-list, .event-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.event-list.scrollable {
  max-height: 150px;
  overflow-y: auto;
}

.person-item, .event-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.event-item.small {
  padding: 4px 8px;
  font-size: 12px;
}

.person-id, .time {
  font-size: 12px;
  color: #666;
}
</style>
