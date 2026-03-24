<template>
  <div class="visualization">
    <div class="header">
      <div class="header-left">
        <h1 class="title">独居老人异常行为识别与应急响应系统</h1>
        <p class="subtitle">Privacy-Powered Elderly Care Anomaly Detection System</p>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="VideoCamera" @click="goToMonitor" class="upload-btn">
          视频流上传
        </el-button>
        <div class="current-time">{{ currentTime }}</div>
        <div class="current-date">{{ currentDate }}</div>
      </div>
    </div>

    <div class="main-content">
      <div class="left-panel">
        <div class="panel-card">
          <h3 class="panel-title">实时统计</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ totalEvents }}</div>
              <div class="stat-label">总事件数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value high-risk">{{ highRiskEvents }}</div>
              <div class="stat-label">高风险</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ todayEvents }}</div>
              <div class="stat-label">今日事件</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ accuracy }}%</div>
              <div class="stat-label">准确率</div>
            </div>
          </div>
        </div>

        <div class="panel-card">
          <h3 class="panel-title">事件类型分布</h3>
          <div ref="typeChartRef" class="chart-container"></div>
        </div>

        <div class="panel-card">
          <h3 class="panel-title">位置热力分布</h3>
          <div ref="heatmapChartRef" class="chart-container"></div>
        </div>
      </div>

      <div class="center-panel">
        <div class="monitor-card">
          <div class="monitor-header">
            <h3 class="monitor-title">实时监控</h3>
            <div class="monitor-status">
              <span class="status-dot online"></span>
              <span class="status-text">在线</span>
            </div>
          </div>
          <div class="monitor-content">
            <div class="camera-view">
              <div class="camera-placeholder">
                <el-icon class="camera-icon"><VideoCamera /></el-icon>
                <p>摄像头实时画面</p>
                <p class="privacy-note">隐私保护模式已启用</p>
              </div>
              <div class="camera-overlay">
                <div class="overlay-info">
                  <span>客厅摄像头</span>
                  <span>{{ currentTime }}</span>
                </div>
                <div class="overlay-status">
                  <el-tag type="success" size="small">正常</el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="events-card">
          <h3 class="panel-title">最新事件</h3>
          <div class="events-list">
            <div
              v-for="event in recentEvents"
              :key="event.id"
              class="event-item"
              :class="`event-${event.riskLevel}`"
            >
              <div class="event-icon">
                <el-icon v-if="event.type === 'fall'"><Warning /></el-icon>
                <el-icon v-else-if="event.type === 'stillness'"><Clock /></el-icon>
                <el-icon v-else><Moon /></el-icon>
              </div>
              <div class="event-info">
                <div class="event-title">{{ event.typeName }}</div>
                <div class="event-time">{{ event.time }}</div>
              </div>
              <div class="event-risk">
                <el-tag :type="getRiskTagType(event.riskLevel)" size="small">
                  {{ getRiskLabel(event.riskLevel) }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="panel-card">
          <h3 class="panel-title">24小时风险趋势</h3>
          <div ref="trendChartRef" class="chart-container"></div>
        </div>

        <div class="panel-card alert-card">
          <h3 class="panel-title">告警信息</h3>
          <div class="alert-list">
            <div v-for="alert in alerts" :key="alert.id" class="alert-item" :class="`alert-${alert.level}`">
              <div class="alert-icon">
                <el-icon><Bell /></el-icon>
              </div>
              <div class="alert-content">
                <div class="alert-message">{{ alert.message }}</div>
                <div class="alert-time">{{ alert.time }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel-card">
          <h3 class="panel-title">系统状态</h3>
          <div class="system-status">
            <div class="status-item">
              <span class="status-label">识别引擎</span>
              <span class="status-value success">运行中</span>
            </div>
            <div class="status-item">
              <span class="status-label">数据采集</span>
              <span class="status-value success">运行中</span>
            </div>
            <div class="status-item">
              <span class="status-label">告警服务</span>
              <span class="status-value success">运行中</span>
            </div>
            <div class="status-item">
              <span class="status-label">存储服务</span>
              <span class="status-value success">运行中</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { VideoCamera, Warning, Clock, Moon, Bell } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { getEvents, getEventStats } from '@/api/events'
import { getAlertHistory, getAlertStats } from '@/api/alerts'

const router = useRouter()

const goToMonitor = () => {
  router.push('/monitor')
}

const currentTime = ref('')
const currentDate = ref('')

const totalEvents = ref(0)
const highRiskEvents = ref(0)
const todayEvents = ref(0)
const accuracy = ref(94.5)

const typeChartRef = ref(null)
const heatmapChartRef = ref(null)
const trendChartRef = ref(null)

let typeChart = null
let heatmapChart = null
let trendChart = null

const recentEvents = ref([])
const alerts = ref([])

const eventStats = ref({
  by_type: {},
  by_risk: {},
  by_status: {}
})

const alertStats = ref({
  total: 0,
  sent_count: 0,
  failed_count: 0
})

const getRiskLabel = (level) => {
  const map = { HIGH: '高风险', high: '高风险', MEDIUM: '中风险', medium: '中风险', LOW: '低风险', low: '低风险' }
  return map[level] || level
}

const getRiskTagType = (level) => {
  const map = { HIGH: 'danger', high: 'danger', MEDIUM: 'warning', medium: 'warning', LOW: 'info', low: 'info' }
  return map[level] || ''
}

const getTypeLabel = (type) => {
  const map = { FALL: '跌倒检测', STILLNESS: '长时间静止', NIGHT_ACTIVITY: '夜间异常活动' }
  return map[type] || type
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN')
  currentDate.value = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    weekday: 'long'
  })
}

const loadData = async () => {
  try {
    const [eventsRes, statsRes, alertsRes, alertStatsRes] = await Promise.all([
      getEvents({ per_page: 5 }),
      getEventStats({ days: 7 }),
      getAlertHistory({ per_page: 5 }),
      getAlertStats({ days: 7 })
    ])

    recentEvents.value = (eventsRes.events || []).map(e => ({
      id: e.id,
      type: (e.event_type || '').toLowerCase(),
      typeName: getTypeLabel(e.event_type),
      time: e.start_time || e.created_at,
      riskLevel: (e.risk_level || '').toLowerCase()
    }))

    eventStats.value = statsRes
    totalEvents.value = statsRes.total || 0
    highRiskEvents.value = statsRes.by_risk?.HIGH || 0

    alerts.value = (alertsRes.alerts || []).map(a => ({
      id: a.id,
      level: (a.risk_level || '').toLowerCase(),
      message: getTypeLabel(a.event_type) + '告警',
      time: a.created_at
    }))

    alertStats.value = alertStatsRes
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const initTypeChart = () => {
  typeChart = echarts.init(typeChartRef.value)
  const stats = eventStats.value
  typeChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: stats.by_type?.FALL || 0, name: '跌倒检测', itemStyle: { color: '#f56c6c' } },
        { value: stats.by_type?.STILLNESS || 0, name: '长时间静止', itemStyle: { color: '#e6a23c' } },
        { value: stats.by_type?.NIGHT_ACTIVITY || 0, name: '夜间异常', itemStyle: { color: '#409eff' } }
      ],
      label: {
        show: true,
        formatter: '{b}\n{c} ({d}%)'
      }
    }]
  })
}

const initHeatmapChart = () => {
  heatmapChart = echarts.init(heatmapChartRef.value)
  heatmapChart.setOption({
    tooltip: { position: 'top' },
    grid: { height: '50%', top: '10%' },
    xAxis: {
      type: 'category',
      data: ['客厅', '卧室', '卫生间', '厨房', '走廊', '书房'],
      splitArea: { show: true }
    },
    yAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      splitArea: { show: true }
    },
    visualMap: {
      min: 0,
      max: 10,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      inRange: { color: ['#50a3ba', '#eac736', '#d94e5d'] }
    },
    series: [{
      type: 'heatmap',
      data: [
        [0, 0, 5], [1, 0, 8], [2, 0, 3], [3, 0, 6], [4, 0, 2], [5, 0, 4],
        [0, 1, 6], [1, 1, 7], [2, 1, 4], [3, 1, 5], [4, 1, 3], [5, 1, 2],
        [0, 2, 4], [1, 2, 9], [2, 2, 5], [3, 2, 7], [4, 2, 1], [5, 2, 3],
        [0, 3, 7], [1, 3, 6], [2, 3, 6], [3, 3, 4], [4, 3, 4], [5, 3, 5],
        [0, 4, 5], [1, 4, 8], [2, 4, 7], [3, 4, 6], [4, 4, 2], [5, 4, 3],
        [0, 5, 3], [1, 5, 5], [2, 5, 4], [3, 5, 5], [4, 5, 3], [5, 5, 2],
        [0, 6, 4], [1, 6, 6], [2, 6, 3], [3, 6, 4], [4, 6, 2], [5, 6, 3]
      ],
      label: { show: false },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
    }]
  })
}

const initTrendChart = () => {
  trendChart = echarts.init(trendChartRef.value)
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: hours,
      axisLabel: { interval: 3 }
    },
    yAxis: {
      type: 'value',
      name: '风险指数'
    },
    series: [{
      name: '风险指数',
      type: 'line',
      smooth: true,
      data: [2, 1, 1, 2, 3, 2, 4, 5, 6, 5, 4, 3, 4, 5, 7, 8, 6, 5, 4, 3, 2, 2, 1, 1],
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
          { offset: 1, color: 'rgba(245, 108, 108, 0.05)' }
        ])
      },
      itemStyle: { color: '#f56c6c' }
    }]
  })
}

const handleResize = () => {
  typeChart?.resize()
  heatmapChart?.resize()
  trendChart?.resize()
}

onMounted(async () => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)

  await loadData()

  nextTick(() => {
    initTypeChart()
    initHeatmapChart()
    initTrendChart()
    window.addEventListener('resize', handleResize)
  })
})

let timeInterval = null

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.visualization {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.header {
  height: 80px;
  padding: 0 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.3);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-left {
  flex: 1;
}

.title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 5px 0;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.header-right {
  text-align: right;
  display: flex;
  align-items: center;
  gap: 20px;
}

.upload-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-weight: 500;
}

.current-time {
  font-size: 32px;
  font-weight: 700;
  color: #667eea;
}

.current-date {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 5px;
}

.main-content {
  flex: 1;
  display: grid;
  grid-template-columns: 25% 50% 25%;
  gap: 20px;
  padding: 20px;
  overflow: hidden;
}

.left-panel,
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 15px 0;
  color: #fff;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 5px;
}

.stat-value.high-risk {
  color: #f56c6c;
}

.stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.chart-container {
  width: 100%;
  height: 200px;
}

.center-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.monitor-card {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.monitor-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.monitor-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-dot.online {
  background: #67c23a;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 12px;
  color: #67c23a;
}

.monitor-content {
  height: calc(100% - 60px);
  padding: 20px;
}

.camera-view {
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.camera-placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.4);
}

.camera-icon {
  font-size: 64px;
  margin-bottom: 15px;
}

.camera-placeholder p {
  margin: 5px 0;
  font-size: 14px;
}

.privacy-note {
  font-size: 12px;
  color: #67c23a;
  margin-top: 10px;
}

.camera-overlay {
  position: absolute;
  top: 10px;
  left: 10px;
  right: 10px;
  display: flex;
  justify-content: space-between;
}

.overlay-info {
  background: rgba(0, 0, 0, 0.5);
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  color: #fff;
}

.events-card {
  height: 300px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 220px;
  overflow-y: auto;
}

.event-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border-left: 3px solid;
}

.event-high {
  border-left-color: #f56c6c;
}

.event-medium {
  border-left-color: #e6a23c;
}

.event-low {
  border-left-color: #409eff;
}

.event-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  margin-right: 12px;
}

.event-info {
  flex: 1;
}

.event-title {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  margin-bottom: 4px;
}

.event-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.alert-card {
  flex: 1;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 200px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border-left: 3px solid;
}

.alert-high {
  border-left-color: #f56c6c;
}

.alert-medium {
  border-left-color: #e6a23c;
}

.alert-low {
  border-left-color: #409eff;
}

.alert-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  margin-right: 12px;
}

.alert-content {
  flex: 1;
}

.alert-message {
  font-size: 13px;
  font-weight: 500;
  color: #fff;
  margin-bottom: 4px;
}

.alert-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.system-status {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
}

.status-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.status-value {
  font-size: 13px;
  font-weight: 500;
}

.status-value.success {
  color: #67c23a;
}

.events-list::-webkit-scrollbar,
.alert-list::-webkit-scrollbar {
  width: 6px;
}

.events-list::-webkit-scrollbar-track,
.alert-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 3px;
}

.events-list::-webkit-scrollbar-thumb,
.alert-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}
</style>
