<template>
  <div class="monitor">
    <!-- 摄像头选择器 -->
    <el-card class="camera-selector">
      <div class="selector-content">
        <span class="selector-label">选择摄像头：</span>
        <el-select v-model="selectedCamera" placeholder="请选择摄像头" style="width: 200px; margin-right: 20px;">
          <el-option
            v-for="camera in cameras"
            :key="camera.id"
            :label="camera.name"
            :value="camera.id"
          />
        </el-select>

        <el-button type="primary" :icon="VideoPlay" @click="startMonitoring">开始监控</el-button>
        <el-button type="danger" :icon="VideoPause" @click="stopMonitoring">停止监控</el-button>

        <el-checkbox v-model="privacyMode" style="margin-left: 20px;">
          隐私保护模式
        </el-checkbox>
      </div>
    </el-card>

    <!-- 监控画面 -->
    <el-row :gutter="20" class="monitor-row">
      <!-- 主监控画面 -->
      <el-col :span="16">
        <el-card class="main-monitor">
          <template #header>
            <div class="monitor-header">
              <span>{{ currentCameraName }}</span>
              <div class="monitor-status">
                <span class="status-dot" :class="{ online: isMonitoring, offline: !isMonitoring }"></span>
                <span class="status-text">{{ isMonitoring ? '监控中' : '已停止' }}</span>
              </div>
            </div>
          </template>

          <div class="monitor-content">
            <div v-if="!isMonitoring" class="monitor-placeholder">
              <el-icon class="placeholder-icon"><VideoCamera /></el-icon>
              <p>点击"开始监控"按钮启动实时监控</p>
            </div>

            <div v-else class="monitor-view">
              <div class="video-container">
                <div class="privacy-mask" v-if="privacyMode">
                  <div class="privacy-info">
                    <el-icon class="privacy-icon"><Lock /></el-icon>
                    <p>隐私保护模式</p>
                    <p>原始画面已匿名化处理</p>
                  </div>
                </div>
              </div>

              <div class="video-overlay">
                <div class="overlay-left">
                  <div class="overlay-item">
                    <span class="overlay-label">位置：</span>
                    <span class="overlay-value">{{ currentCameraName }}</span>
                  </div>
                  <div class="overlay-item">
                    <span class="overlay-label">时间：</span>
                    <span class="overlay-value">{{ currentTime }}</span>
                  </div>
                </div>
                <div class="overlay-right">
                  <el-tag :type="currentRiskLevel" size="large">
                    {{ currentRiskLabel }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 实时信息面板 -->
      <el-col :span="8">
        <el-card class="info-panel">
          <template #header>
            <span>实时信息</span>
          </template>

          <div class="info-content">
            <div class="info-section">
              <h4 class="info-title">检测状态</h4>
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">活动状态：</span>
                  <span class="info-value">{{ activityStatus }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">置信度：</span>
                  <span class="info-value">{{ (confidence * 100).toFixed(1) }}%</span>
                </div>
                <div class="info-item">
                  <span class="info-label">静止时长：</span>
                  <span class="info-value">{{ formatDuration(stillnessDuration) }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">活动次数：</span>
                  <span class="info-value">{{ activityCount }}</span>
                </div>
              </div>
            </div>

            <div class="info-section">
              <h4 class="info-title">风险指标</h4>
              <div class="risk-indicators">
                <div class="risk-indicator">
                  <div class="indicator-label">跌倒风险</div>
                  <el-progress
                    :percentage="fallRisk"
                    :color="getRiskColor(fallRisk)"
                    :stroke-width="8"
                  />
                </div>
                <div class="risk-indicator">
                  <div class="indicator-label">静止风险</div>
                  <el-progress
                    :percentage="stillnessRisk"
                    :color="getRiskColor(stillnessRisk)"
                    :stroke-width="8"
                  />
                </div>
                <div class="risk-indicator">
                  <div class="indicator-label">夜间异常</div>
                  <el-progress
                    :percentage="nightRisk"
                    :color="getRiskColor(nightRisk)"
                    :stroke-width="8"
                  />
                </div>
              </div>
            </div>

            <div class="info-section">
              <h4 class="info-title">最近检测</h4>
              <div class="recent-detections">
                <div
                  v-for="detection in recentDetections"
                  :key="detection.id"
                  class="detection-item"
                >
                  <el-tag :type="getDetectionTagType(detection.type)" size="small">
                    {{ detection.typeName }}
                  </el-tag>
                  <span class="detection-time">{{ detection.time }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 监控日志 -->
    <el-card class="log-card">
      <template #header>
        <div class="log-header">
          <span>监控日志</span>
          <el-button type="primary" :icon="Download" size="small">导出日志</el-button>
        </div>
      </template>

      <el-table :data="monitorLogs" stripe style="width: 100%" max-height="300">
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="camera" label="摄像头" width="120" />
        <el-table-column prop="event" label="事件" width="150" />
        <el-table-column prop="riskLevel" label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.riskLevel)" size="small">
              {{ getRiskLabel(row.riskLevel) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="置信度" width="100">
          <template #default="{ row }">
            {{ (row.confidence * 100).toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { VideoPlay, VideoPause, VideoCamera, Lock, Download } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const selectedCamera = ref(1)
const isMonitoring = ref(false)
const privacyMode = ref(true)

const cameras = ref([
  { id: 1, name: '客厅摄像头', location: '客厅' },
  { id: 2, name: '卧室摄像头', location: '卧室' },
  { id: 3, name: '卫生间摄像头', location: '卫生间' },
  { id: 4, name: '厨房摄像头', location: '厨房' }
])

const currentCameraName = computed(() => {
  const camera = cameras.value.find(c => c.id === selectedCamera.value)
  return camera ? camera.name : '未选择'
})

const activityStatus = ref('活动')
const confidence = ref(0.92)
const stillnessDuration = ref(0)
const activityCount = ref(23)

const fallRisk = ref(15)
const stillnessRisk = ref(35)
const nightRisk = ref(10)

const currentRiskLevel = computed(() => {
  const maxRisk = Math.max(fallRisk.value, stillnessRisk.value, nightRisk.value)
  if (maxRisk >= 70) return 'danger'
  if (maxRisk >= 40) return 'warning'
  return 'success'
})

const currentRiskLabel = computed(() => {
  const maxRisk = Math.max(fallRisk.value, stillnessRisk.value, nightRisk.value)
  if (maxRisk >= 70) return '高风险'
  if (maxRisk >= 40) return '中风险'
  return '正常'
})

const currentTime = ref('')

const recentDetections = ref([
  { id: 1, type: 'fall', typeName: '跌倒检测', time: '14:32:15' },
  { id: 2, type: 'stillness', typeName: '长时间静止', time: '12:15:30' },
  { id: 3, type: 'normal', typeName: '正常活动', time: '10:45:22' },
  { id: 4, type: 'normal', typeName: '正常活动', time: '09:30:18' }
])

const monitorLogs = ref([
  { time: '2026-03-22 14:32:15', camera: '客厅', event: '跌倒检测', riskLevel: 'high', confidence: 0.92, description: '检测到跌倒行为' },
  { time: '2026-03-22 12:15:30', camera: '卧室', event: '长时间静止', riskLevel: 'medium', confidence: 0.85, description: '静止超过30分钟' },
  { time: '2026-03-22 10:45:22', camera: '客厅', event: '正常活动', riskLevel: 'low', confidence: 0.95, description: '正常行走' },
  { time: '2026-03-22 09:30:18', camera: '厨房', event: '正常活动', riskLevel: 'low', confidence: 0.93, description: '正常活动' }
])

let timeInterval = null

const updateTime = () => {
  currentTime.value = dayjs().format('YYYY-MM-DD HH:mm:ss')
}

const formatDuration = (seconds) => {
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分${seconds % 60}秒`
  return `${Math.floor(seconds / 3600)}时${Math.floor((seconds % 3600) / 60)}分`
}

const getRiskColor = (risk) => {
  if (risk >= 70) return '#f56c6c'
  if (risk >= 40) return '#e6a23c'
  return '#67c23a'
}

const getRiskLabel = (level) => {
  const map = { high: '高风险', medium: '中风险', low: '低风险' }
  return map[level] || level
}

const getRiskTagType = (level) => {
  const map = { high: 'danger', medium: 'warning', low: 'info' }
  return map[level] || ''
}

const getDetectionTagType = (type) => {
  const map = { fall: 'danger', stillness: 'warning', normal: 'success' }
  return map[type] || ''
}

const startMonitoring = () => {
  isMonitoring.value = true
  console.log('开始监控', currentCameraName.value)
}

const stopMonitoring = () => {
  isMonitoring.value = false
  console.log('停止监控')
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.monitor {
  width: 100%;
}

.camera-selector {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.selector-content {
  display: flex;
  align-items: center;
}

.selector-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.monitor-row {
  margin-bottom: 20px;
}

.main-monitor {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: 500px;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.monitor-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-dot.online {
  background: #67c23a;
}

.status-dot.offline {
  background: #f56c6c;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 14px;
}

.monitor-content {
  height: calc(100% - 60px);
}

.monitor-placeholder {
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

.monitor-placeholder p {
  font-size: 16px;
}

.monitor-view {
  width: 100%;
  height: 100%;
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.privacy-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
}

.privacy-info {
  text-align: center;
  color: #fff;
}

.privacy-icon {
  font-size: 48px;
  margin-bottom: 15px;
  color: #67c23a;
}

.privacy-info p {
  margin: 8px 0;
  font-size: 16px;
}

.video-overlay {
  position: absolute;
  top: 15px;
  left: 15px;
  right: 15px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.overlay-left {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.overlay-item {
  background: rgba(0, 0, 0, 0.5);
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 13px;
  color: #fff;
}

.overlay-label {
  color: rgba(255, 255, 255, 0.7);
  margin-right: 5px;
}

.overlay-value {
  font-weight: 500;
}

.info-panel {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: 500px;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: 420px;
  overflow-y: auto;
}

.info-section {
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.info-section:last-child {
  border-bottom: none;
}

.info-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.risk-indicators {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.risk-indicator {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.indicator-label {
  font-size: 13px;
  color: #666;
}

.recent-detections {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detection-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.detection-time {
  font-size: 12px;
  color: #666;
}

.log-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}
</style>