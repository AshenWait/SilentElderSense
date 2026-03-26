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
          <!-- 模式切换 -->
          <el-radio-group v-model="monitorMode" @change="handleModeChange" :disabled="isConnected">
            <el-radio-button value="video">视频文件</el-radio-button>
            <el-radio-button value="camera">摄像头</el-radio-button>
          </el-radio-group>

          <!-- 视频文件模式 -->
          <template v-if="monitorMode === 'video'">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :show-file-list="false"
              accept="video/*"
              :on-change="handleVideoSelect"
            >
              <el-button type="primary" :icon="Upload">
                选择视频
              </el-button>
            </el-upload>
          </template>

          <!-- 摄像头模式 -->
          <template v-if="monitorMode === 'camera'">
            <el-select
              v-model="selectedCameraId"
              placeholder="选择摄像头"
              :disabled="isConnected"
              style="width: 200px"
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
          </template>

          <el-button
            v-if="monitorMode === 'video' && selectedVideo"
            type="success"
            :icon="VideoPlay"
            @click="startSession"
            :disabled="isConnected"
          >
            开始检测
          </el-button>
          <el-button
            v-if="monitorMode === 'camera'"
            type="success"
            :icon="VideoPlay"
            @click="startCameraDetection"
            :disabled="isConnected || !selectedCameraId"
          >
            开始检测
          </el-button>
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
      <div v-if="monitorMode === 'video' && selectedVideo" class="video-info">
        <el-tag>视频: {{ selectedVideo.name }}</el-tag>
        <span class="video-size">大小: {{ formatFileSize(selectedVideo.size) }}</span>
      </div>
      <div v-if="monitorMode === 'camera' && isConnected" class="camera-info">
        <el-tag type="success">摄像头运行中</el-tag>
        <span class="fps-info">帧率: {{ currentFps }} FPS</span>
        <span class="duration-info">时长: {{ formatDuration(cameraDuration) }}</span>
      </div>
    </el-card>

    <!-- 进度条（视频模式） -->
    <el-card v-if="monitorMode === 'video' && isConnected && videoProgress > 0" class="progress-card">
      <el-progress
        :percentage="videoProgress"
        :format="progressFormat"
        :stroke-width="20"
        :color="progressColor"
      />
      <div class="progress-info">
        <span>已处理: {{ processedFrames }} 帧</span>
        <span>检测事件: {{ totalEvents }} 个</span>
      </div>
    </el-card>

    <!-- 监控区域 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="video-card">
          <template #header>
            <div class="card-header">
              <span>{{ monitorMode === 'video' ? '实时监控' : '摄像头监控' }}</span>
              <el-tag v-if="isConnected" type="success">检测中</el-tag>
            </div>
          </template>

          <div class="video-container">
            <div v-if="!isConnected && !previewUrl && !cameraStream" class="placeholder">
              <el-icon class="placeholder-icon"><VideoCamera /></el-icon>
              <p>{{ monitorMode === 'video' ? '选择视频文件开始检测' : '选择摄像头开始检测' }}</p>
            </div>
            <div v-else class="detection-view">
              <video
                ref="videoRef"
                :src="monitorMode === 'video' ? previewUrl : ''"
                :srcObject="monitorMode === 'camera' ? cameraStream : null"
                class="video-player"
                autoplay
                muted
                playsinline
                @loadedmetadata="onVideoLoaded"
              ></video>
              <canvas ref="canvasRef" class="overlay-canvas"></canvas>
              <div class="overlay-info">
                <div class="info-item">
                  <span class="label">检测人数：</span>
                  <span class="value">{{ detectionResult.persons?.length || 0 }}</span>
                </div>
                <div class="info-item">
                  <span class="label">事件数：</span>
                  <span class="value">{{ detectionResult.events?.length || 0 }}</span>
                </div>
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
                <h4>检测到的人员</h4>
                <div v-if="detectionResult.persons?.length" class="person-list">
                  <div v-for="person in detectionResult.persons" :key="person.person_id" class="person-item">
                    <el-tag :type="getPersonTagType(person.class_name)" size="small">
                      {{ getPersonLabel(person.class_name) }}
                    </el-tag>
                    <span class="confidence">置信度: {{ (person.confidence * 100).toFixed(1) }}%</span>
                  </div>
                </div>
                <el-empty v-else description="暂无检测结果" :image-size="60" />
              </div>

              <div class="section">
                <h4>检测事件</h4>
                <div v-if="detectionResult.events?.length" class="event-list">
                  <div v-for="(event, index) in detectionResult.events" :key="index" class="event-item">
                    <el-tag :type="getEventTagType(event.risk_level)" size="small">
                      {{ getEventLabel(event.event_type) }}
                    </el-tag>
                    <span class="duration">持续: {{ event.duration?.toFixed(1) }}秒</span>
                  </div>
                </div>
                <el-empty v-else description="暂无事件" :image-size="60" />
              </div>

              <div class="section" v-if="allEvents.length > 0">
                <h4>历史事件 ({{ allEvents.length }})</h4>
                <div class="event-list scrollable">
                  <div v-for="(event, index) in allEvents.slice(-10).reverse()" :key="index" class="event-item small">
                    <el-tag :type="getEventTagType(event.risk_level)" size="small">
                      {{ getEventLabel(event.event_type) }}
                    </el-tag>
                    <span class="time">{{ event.duration?.toFixed(1) }}s</span>
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
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { VideoPlay, VideoPause, VideoCamera, Upload, RefreshRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { createSession, closeSession, getCameraDevices, stopStream } from '@/api/monitor'

// 模式
const monitorMode = ref('video')

// 视频文件模式
const selectedVideo = ref(null)
const previewUrl = ref('')
const videoProgress = ref(0)
const processedFrames = ref(0)
const uploadRef = ref(null)

// 摄像头模式
const cameraDevices = ref([])
const selectedCameraId = ref('')
const cameraStream = ref(null)
const currentFps = ref(0)
const cameraDuration = ref(0)

// 通用
const videoRef = ref(null)
const canvasRef = ref(null)
const videoId = ref('')
const isConnected = ref(false)
const totalEvents = ref(0)
const allEvents = ref([])

const detectionResult = ref({
  detected: false,
  persons: [],
  events: []
})

let ws = null
let frameInterval = null
let videoCanvas = null
let videoCtx = null
let cameraStartTime = null
let fpsCounter = 0
let fpsInterval = null

// 标签映射
const getPersonTagType = (className) => {
  const map = { 'normal': 'success', 'fall': 'danger', 'stillness': 'warning', 'falling': 'warning', 'fallen': 'danger' }
  return map[className] || 'info'
}

const getPersonLabel = (className) => {
  const map = { 'normal': '正常', 'fall': '跌倒', 'stillness': '静止', 'falling': '跌倒中', 'fallen': '已跌倒' }
  return map[className] || className
}

const getEventTagType = (riskLevel) => {
  const map = { 'HIGH': 'danger', 'MEDIUM': 'warning', 'LOW': 'info' }
  return map[riskLevel] || 'info'
}

const getEventLabel = (eventType) => {
  const map = { 'FALL': '跌倒检测', 'STILLNESS': '长时间静止', 'NIGHT_ACTIVITY': '夜间异常', 'STATIC': '长时间静止' }
  return map[eventType] || eventType
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const progressFormat = (percentage) => percentage === 100 ? '完成' : `${percentage}%`

const progressColor = (percentage) => {
  if (percentage < 30) return '#909399'
  if (percentage < 70) return '#e6a23c'
  return '#67c23a'
}

// 模式切换
const handleModeChange = async (mode) => {
  if (isConnected.value) {
    stopSession()
  }
  selectedVideo.value = null
  previewUrl.value = ''
  videoProgress.value = 0
  processedFrames.value = 0
  cameraDuration.value = 0

  // 切换到摄像头模式时加载设备列表
  if (mode === 'camera') {
    await loadCameraDevices()
  }
}

// 视频文件选择
const handleVideoSelect = (file) => {
  if (!file || !file.raw) {
    ElMessage.error('文件选择失败')
    return
  }
  selectedVideo.value = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
  videoProgress.value = 0
  processedFrames.value = 0
  totalEvents.value = 0
  allEvents.value = []
}

const onVideoLoaded = () => {
  // 视频加载完成
}

// 获取摄像头列表
const loadCameraDevices = async () => {
  try {
    ElMessage.info('正在请求摄像头权限...')
    const devices = await getCameraDevices()
    cameraDevices.value = devices

    if (devices.length > 0) {
      // 默认选择第一个有标签的设备
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

// 视频文件检测
const startSession = async () => {
  if (!selectedVideo.value) {
    ElMessage.warning('请先选择视频文件')
    return
  }

  try {
    const response = await createSession()
    videoId.value = response.video_id

    // 连接 WebSocket
    ws = new WebSocket(`ws://localhost:8000/ws/detect/${videoId.value}`)

    ws.onopen = () => {
      isConnected.value = true
      ElMessage.success('会话创建成功，开始检测')
      startVideoProcessing()
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.error) {
          ElMessage.error(data.error)
        } else {
          detectionResult.value = data
          if (data.events?.length) {
            totalEvents.value += data.events.length
            allEvents.value.push(...data.events)
          }
          renderFrame(data)
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
      stopVideoProcessing()
    }
  } catch (error) {
    ElMessage.error('创建会话失败: ' + error.message)
  }
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
    videoRef.value.srcObject = stream

    // 等待视频加载
    await new Promise(resolve => {
      videoRef.value.onloadedmetadata = resolve
    })
    await videoRef.value.play()

    // 创建检测会话
    const response = await createSession()
    videoId.value = response.video_id

    // 连接 WebSocket
    ws = new WebSocket(`ws://localhost:8000/ws/detect/${videoId.value}`)

    ws.onopen = () => {
      isConnected.value = true
      cameraStartTime = Date.now()
      ElMessage.success('摄像头检测已启动')
      startCameraFrameSending()
      startFpsCounter()
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.error) {
          ElMessage.error(data.error)
        } else {
          detectionResult.value = data
          if (data.events?.length) {
            totalEvents.value += data.events.length
            allEvents.value.push(...data.events)
          }
          renderFrame(data)
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
    }
  } catch (error) {
    console.error('启动摄像头失败:', error)
    ElMessage.error('启动摄像头失败: ' + error.message)
  }
}

// 开始 FPS 计数
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

// 停止 FPS 计数
const stopFpsCounter = () => {
  if (fpsInterval) {
    clearInterval(fpsInterval)
    fpsInterval = null
  }
  currentFps.value = 0
}

// 摄像头发送帧
const startCameraFrameSending = () => {
  if (!videoRef.value) return

  // 创建离屏 canvas 用于提取帧
  videoCanvas = document.createElement('canvas')
  videoCanvas.width = 640
  videoCanvas.height = 480
  videoCtx = videoCanvas.getContext('2d')

  const sendFrame = () => {
    if (!isConnected.value || monitorMode.value !== 'camera') {
      return
    }

    // 提取帧数据
    videoCtx.drawImage(videoRef.value, 0, 0, videoCanvas.width, videoCanvas.height)

    // 转换为 JPEG 并发送
    videoCanvas.toBlob((blob) => {
      if (blob && ws && ws.readyState === WebSocket.OPEN) {
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

// 视频文件处理
const startVideoProcessing = () => {
  if (!videoRef.value) return

  const video = videoRef.value
  video.currentTime = 0
  video.playbackRate = 1.0

  // 创建离屏 canvas 用于提取帧
  videoCanvas = document.createElement('canvas')
  videoCanvas.width = 640
  videoCanvas.height = 480
  videoCtx = videoCanvas.getContext('2d')

  video.play().catch(e => console.error('视频播放失败:', e))

  // 逐帧提取并发送
  let lastTime = 0
  const fps = 10 // 每秒发送 10 帧

  const processFrame = () => {
    if (!isConnected.value || video.ended) {
      if (video.ended) {
        videoProgress.value = 100
        ElMessage.success('视频处理完成')
      }
      return
    }

    const currentTime = video.currentTime
    if (currentTime - lastTime >= 1 / fps) {
      lastTime = currentTime

      // 更新进度
      videoProgress.value = Math.round((video.currentTime / video.duration) * 100)
      processedFrames.value++

      // 提取帧数据
      videoCtx.drawImage(video, 0, 0, videoCanvas.width, videoCanvas.height)

      // 转换为 JPEG 并发送
      videoCanvas.toBlob((blob) => {
        if (blob && ws && ws.readyState === WebSocket.OPEN) {
          blob.arrayBuffer().then(buffer => {
            ws.send(buffer)
          })
        }
      }, 'image/jpeg', 0.8)
    }

    requestAnimationFrame(processFrame)
  }

  requestAnimationFrame(processFrame)
}

// 停止处理
const stopVideoProcessing = () => {
  if (videoRef.value && monitorMode.value === 'video') {
    videoRef.value.pause()
  }
  videoCanvas = null
  videoCtx = null

  // 停止摄像头流
  if (cameraStream.value) {
    stopStream(cameraStream.value)
    cameraStream.value = null
  }

  cameraStartTime = null
  stopFpsCounter()
}

// 停止会话
const stopSession = async () => {
  stopVideoProcessing()

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
  detectionResult.value = { detected: false, persons: [], events: [] }
}

// 渲染检测框
const renderFrame = (data) => {
  if (!canvasRef.value || !data.persons?.length) return

  const ctx = canvasRef.value.getContext('2d')
  const width = canvasRef.value.width
  const height = canvasRef.value.height

  // 清空画布
  ctx.clearRect(0, 0, width, height)

  // 绘制检测框
  data.persons.forEach(person => {
    const [x1, y1, x2, y2] = person.box || [0, 0, 100, 100]
    // 缩放到 canvas 尺寸
    const scaleX = width / 640
    const scaleY = height / 480

    const color = person.class_name === 'fall' || person.class_name === 'fallen' ? '#f56c6c' :
                  person.class_name === 'stillness' || person.class_name === 'falling' ? '#e6a23c' : '#67c23a'

    ctx.strokeStyle = color
    ctx.lineWidth = 2
    ctx.strokeRect(x1 * scaleX, y1 * scaleY, (x2 - x1) * scaleX, (y2 - y1) * scaleY)

    ctx.fillStyle = color
    ctx.font = '14px Arial'
    ctx.fillText(`${getPersonLabel(person.class_name)} ${(person.confidence * 100).toFixed(0)}%`,
                 x1 * scaleX, y1 * scaleY - 5)
  })
}

onMounted(() => {
  if (canvasRef.value) {
    canvasRef.value.width = 640
    canvasRef.value.height = 480
  }
  // 不在页面加载时请求摄像头权限，等用户切换到摄像头模式时再请求
})

onUnmounted(() => {
  stopSession()
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
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

.video-info, .camera-info {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 12px;
}

.video-size, .fps-info, .duration-info {
  color: #999;
  font-size: 12px;
}

.progress-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.progress-info {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  color: #666;
  font-size: 14px;
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

.detection-view {
  width: 100%;
  height: 100%;
  position: relative;
}

.video-player {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.overlay-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
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

.confidence, .duration, .time {
  font-size: 12px;
  color: #666;
}
</style>
