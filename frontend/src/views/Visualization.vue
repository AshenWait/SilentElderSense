<template>
  <div class="dashboard">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-gradient"></div>
      <div class="bg-grid"></div>
      <div class="bg-noise"></div>
    </div>

    <!-- 顶部导航 -->
    <header class="dashboard-header">
      <div class="header-left">
        <div class="logo-area">
          <div class="logo-icon">
            <svg viewBox="0 0 40 40" fill="none">
              <circle cx="20" cy="20" r="18" stroke="url(#logoGrad)" stroke-width="2"/>
              <circle cx="20" cy="20" r="6" fill="url(#logoGrad)"/>
              <path d="M20 8C13.373 8 8 13.373 8 20" stroke="url(#logoGrad)" stroke-width="2" stroke-linecap="round"/>
              <defs>
                <linearGradient id="logoGrad" x1="8" y1="8" x2="32" y2="32">
                  <stop stop-color="#fb923c"/>
                  <stop offset="1" stop-color="#f97316"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div class="logo-text">
            <h1 class="system-name">SilentElder<span class="accent">Sense</span></h1>
            <p class="system-desc">独居老人智能监护系统</p>
          </div>
        </div>
      </div>

      <div class="header-center">
        <div class="status-indicator">
          <span class="pulse-dot"></span>
          <span class="status-label">系统运行正常</span>
        </div>
      </div>

      <div class="header-right">
        <button class="action-btn" @click="goToMonitor">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 7l-7 5 7 5V7z"/>
            <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
          </svg>
          <span>视频上传</span>
        </button>
        <div class="datetime-display">
          <span class="time">{{ currentTime }}</span>
          <span class="date">{{ currentDate }}</span>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="dashboard-content">
      <!-- 左侧面板 -->
      <aside class="panel panel-left">
        <!-- 统计卡片组 -->
        <div class="stats-grid">
          <div class="stat-card" v-for="(stat, index) in statsData" :key="stat.label">
            <div class="stat-icon" :class="stat.type">
              <component :is="stat.icon" />
            </div>
            <div class="stat-info">
              <span class="stat-value" :class="{ 'animate-value': stat.animate }">
                {{ stat.value }}
              </span>
              <span class="stat-label">{{ stat.label }}</span>
            </div>
            <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'" v-if="stat.trend">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path :d="stat.trend > 0 ? 'M18 15l-6-6-6 6' : 'M6 9l6 6 6-6'"/>
              </svg>
              <span>{{ Math.abs(stat.trend) }}%</span>
            </div>
          </div>
        </div>

        <!-- 事件类型分布 -->
        <div class="card chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <span class="title-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>
                  <path d="M22 12A10 10 0 0 0 12 2v10z"/>
                </svg>
              </span>
              事件类型分布
            </h3>
          </div>
          <div class="card-body">
            <div ref="typeChartRef" class="chart"></div>
          </div>
        </div>

        <!-- 位置热力图 -->
        <div class="card chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <span class="title-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <line x1="3" y1="9" x2="21" y2="9"/>
                  <line x1="9" y1="21" x2="9" y2="9"/>
                </svg>
              </span>
              位置热力分布
            </h3>
          </div>
          <div class="card-body">
            <div ref="heatmapChartRef" class="chart"></div>
          </div>
        </div>
      </aside>

      <!-- 中间主区域 -->
      <section class="panel panel-center">
        <!-- 实时监控 -->
        <div class="card monitor-card">
          <div class="card-header">
            <h3 class="card-title">
              <span class="title-icon live">
                <span class="live-dot"></span>
              </span>
              实时监控
            </h3>
            <div class="monitor-status">
              <span class="status-badge online">
                <span class="badge-dot"></span>
                在线
              </span>
            </div>
          </div>
          <div class="card-body monitor-body">
            <div class="camera-view">
              <div class="camera-placeholder">
                <div class="placeholder-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M23 7l-7 5 7 5V7z"/>
                    <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                  </svg>
                </div>
                <p class="placeholder-title">摄像头实时画面</p>
                <p class="placeholder-subtitle">隐私保护模式已启用</p>
                <div class="privacy-badge">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                  </svg>
                  <span>隐私加密</span>
                </div>
              </div>
              <div class="camera-overlay">
                <div class="overlay-info">
                  <span class="camera-name">客厅摄像头</span>
                  <span class="camera-time">{{ currentTime }}</span>
                </div>
                <div class="overlay-badges">
                  <span class="badge badge-success">正常</span>
                </div>
              </div>
              <div class="scan-line"></div>
            </div>
          </div>
        </div>

        <!-- 最新事件 -->
        <div class="card events-card">
          <div class="card-header">
            <h3 class="card-title">
              <span class="title-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
              </span>
              最新事件
            </h3>
            <router-link to="/analysis" class="view-all">
              查看全部
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 18l6-6-6-6"/>
              </svg>
            </router-link>
          </div>
          <div class="card-body events-body">
            <TransitionGroup name="event-list" tag="div" class="events-list">
              <div
                v-for="event in recentEvents"
                :key="event.id"
                class="event-item"
                :class="`risk-${event.riskLevel}`"
              >
                <div class="event-icon" :class="`icon-${event.type}`">
                  <svg v-if="event.type === 'fall'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/>
                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                  <svg v-else-if="event.type === 'stillness'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                  </svg>
                </div>
                <div class="event-content">
                  <div class="event-header">
                    <span class="event-type">{{ event.typeName }}</span>
                    <span class="event-time">{{ formatTime(event.time) }}</span>
                  </div>
                  <div class="event-meta">
                    <span class="event-location">客厅区域</span>
                    <span class="event-duration" v-if="event.duration">持续 {{ event.duration }}</span>
                  </div>
                </div>
                <div class="event-risk">
                  <span class="risk-tag" :class="`tag-${event.riskLevel}`">
                    {{ getRiskLabel(event.riskLevel) }}
                  </span>
                </div>
              </div>
            </TransitionGroup>
            <div v-if="recentEvents.length === 0" class="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 12l2 2 4-4"/>
                <circle cx="12" cy="12" r="10"/>
              </svg>
              <p>暂无事件记录</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 右侧面板 -->
      <aside class="panel panel-right">
        <!-- 24小时趋势 -->
        <div class="card chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <span class="title-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
              </span>
              24小时风险趋势
            </h3>
          </div>
          <div class="card-body">
            <div ref="trendChartRef" class="chart"></div>
          </div>
        </div>

        <!-- 告警信息 -->
        <div class="card alerts-card">
          <div class="card-header">
            <h3 class="card-title">
              <span class="title-icon warning">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                  <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                </svg>
              </span>
              告警信息
            </h3>
            <span class="alert-count" v-if="alerts.length">{{ alerts.length }}</span>
          </div>
          <div class="card-body alerts-body">
            <div class="alerts-list">
              <TransitionGroup name="alert-list">
                <div
                  v-for="alert in alerts"
                  :key="alert.id"
                  class="alert-item"
                  :class="`alert-${alert.level}`"
                >
                  <div class="alert-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="10"/>
                      <line x1="12" y1="8" x2="12" y2="12"/>
                      <line x1="12" y1="16" x2="12.01" y2="16"/>
                    </svg>
                  </div>
                  <div class="alert-content">
                    <p class="alert-message">{{ alert.message }}</p>
                    <span class="alert-time">{{ formatTime(alert.time) }}</span>
                  </div>
                </div>
              </TransitionGroup>
            </div>
            <div v-if="alerts.length === 0" class="empty-state small">
              <p>暂无告警</p>
            </div>
          </div>
        </div>

        <!-- 系统状态 -->
        <div class="card status-card">
          <div class="card-header">
            <h3 class="card-title">
              <span class="title-icon success">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                  <line x1="8" y1="21" x2="16" y2="21"/>
                  <line x1="12" y1="17" x2="12" y2="21"/>
                </svg>
              </span>
              系统状态
            </h3>
          </div>
          <div class="card-body">
            <div class="status-list">
              <div class="status-item" v-for="service in systemServices" :key="service.name">
                <div class="status-info">
                  <span class="status-name">{{ service.name }}</span>
                  <span class="status-desc">{{ service.desc }}</span>
                </div>
                <div class="status-indicator" :class="service.status">
                  <span class="indicator-dot"></span>
                  <span class="indicator-text">{{ service.statusText }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed, h } from 'vue'
import * as echarts from 'echarts'
import { useRouter } from 'vue-router'
import { getEvents, getEventStats } from '@/api/events'
import { getAlertHistory, getAlertStats } from '@/api/alerts'

const router = useRouter()

// 时间显示
const currentTime = ref('')
const currentDate = ref('')

// 统计数据
const totalEvents = ref(0)
const highRiskEvents = ref(0)
const todayEvents = ref(0)
const accuracy = ref(94.5)

// 图表引用
const typeChartRef = ref(null)
const heatmapChartRef = ref(null)
const trendChartRef = ref(null)

let typeChart = null
let heatmapChart = null
let trendChart = null
let timeInterval = null

// 事件数据
const recentEvents = ref([])
const alerts = ref([])

// 统计数据
const eventStats = ref({
  by_type: {},
  by_risk: {},
  by_status: {}
})

// 统计卡片数据
const statsData = computed(() => [
  {
    label: '总事件数',
    value: totalEvents.value,
    type: 'primary',
    trend: 5.2,
    animate: true,
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M22 12h-4l-3 9L9 3l-3 9H2' })
    ])
  },
  {
    label: '高风险',
    value: highRiskEvents.value,
    type: 'danger',
    trend: -2.1,
    animate: true,
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z' }),
      h('line', { x1: '12', y1: '9', x2: '12', y2: '13' }),
      h('line', { x1: '12', y1: '17', x2: '12.01', y2: '17' })
    ])
  },
  {
    label: '今日事件',
    value: todayEvents.value,
    type: 'info',
    animate: true,
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('rect', { x: '3', y: '4', width: '18', height: '18', rx: '2', ry: '2' }),
      h('line', { x1: '16', y1: '2', x2: '16', y2: '6' }),
      h('line', { x1: '8', y1: '2', x2: '8', y2: '6' }),
      h('line', { x1: '3', y1: '10', x2: '21', y2: '10' })
    ])
  },
  {
    label: '识别准确率',
    value: `${accuracy.value}%`,
    type: 'success',
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M22 11.08V12a10 10 0 1 1-5.93-9.14' }),
      h('polyline', { points: '22 4 12 14.01 9 11.01' })
    ])
  }
])

// 系统服务状态
const systemServices = ref([
  { name: '识别引擎', desc: 'AI行为识别服务', status: 'online', statusText: '运行中' },
  { name: '数据采集', desc: '视频流采集服务', status: 'online', statusText: '运行中' },
  { name: '告警服务', desc: '消息推送服务', status: 'online', statusText: '运行中' },
  { name: '存储服务', desc: '数据存储服务', status: 'online', statusText: '运行中' }
])

// 工具函数
const getRiskLabel = (level) => {
  const map = { HIGH: '高风险', high: '高风险', MEDIUM: '中风险', medium: '中风险', LOW: '低风险', low: '低风险' }
  return map[level] || level
}

const getTypeLabel = (type) => {
  const map = { FALL: '跌倒检测', STILLNESS: '长时间静止', NIGHT_ACTIVITY: '夜间异常活动' }
  return map[type] || type
}

const formatTime = (time) => {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
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

const goToMonitor = () => {
  router.push('/monitor')
}

// 加载数据
const loadData = async () => {
  try {
    const [eventsRes, statsRes, alertsRes] = await Promise.all([
      getEvents({ per_page: 5 }),
      getEventStats({ days: 7 }),
      getAlertHistory({ per_page: 5 })
    ])

    recentEvents.value = (eventsRes.events || []).map(e => ({
      id: e.id,
      type: (e.event_type || '').toLowerCase(),
      typeName: getTypeLabel(e.event_type),
      time: e.start_time || e.created_at,
      riskLevel: (e.risk_level || '').toLowerCase(),
      duration: e.duration ? `${Math.floor(e.duration / 60)}分` : null
    }))

    eventStats.value = statsRes
    totalEvents.value = statsRes.total || 0
    highRiskEvents.value = statsRes.by_risk?.HIGH || 0
    todayEvents.value = statsRes.by_status?.pending || 0

    alerts.value = (alertsRes.alerts || []).map(a => ({
      id: a.id,
      level: (a.risk_level || '').toLowerCase(),
      message: getTypeLabel(a.event_type) + '告警',
      time: a.created_at
    }))

    updateCharts()
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

// 图表配置
const chartTheme = {
  backgroundColor: 'transparent',
  textStyle: { color: 'rgba(255,255,255,0.6)' }
}

const initTypeChart = () => {
  if (!typeChartRef.value) return
  typeChart = echarts.init(typeChartRef.value)
  updateTypeChart()
}

const updateTypeChart = () => {
  if (!typeChart) return
  const stats = eventStats.value
  typeChart.setOption({
    ...chartTheme,
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(26,26,36,0.95)',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#fff' }
    },
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      center: ['50%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 8,
        borderColor: 'rgba(26,26,36,0.8)',
        borderWidth: 3
      },
      label: {
        show: true,
        color: 'rgba(255,255,255,0.7)',
        fontSize: 11,
        formatter: '{b}\n{d}%'
      },
      labelLine: {
        show: true,
        lineStyle: { color: 'rgba(255,255,255,0.3)' }
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 20,
          shadowColor: 'rgba(0,0,0,0.5)'
        }
      },
      data: [
        { value: stats.by_type?.FALL || 0, name: '跌倒检测', itemStyle: { color: '#f97316' } },
        { value: stats.by_type?.STILLNESS || 0, name: '长时间静止', itemStyle: { color: '#eab308' } },
        { value: stats.by_type?.NIGHT_ACTIVITY || 0, name: '夜间异常', itemStyle: { color: '#3b82f6' } }
      ]
    }]
  })
}

const initHeatmapChart = () => {
  if (!heatmapChartRef.value) return
  heatmapChart = echarts.init(heatmapChartRef.value)
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const data = []
  for (let i = 0; i < 7; i++) {
    for (let j = 0; j < 24; j++) {
      data.push([j, i, Math.floor(Math.random() * 10)])
    }
  }

  heatmapChart.setOption({
    ...chartTheme,
    tooltip: {
      position: 'top',
      backgroundColor: 'rgba(26,26,36,0.95)',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#fff' }
    },
    grid: {
      top: 10,
      left: 50,
      right: 10,
      bottom: 30
    },
    xAxis: {
      type: 'category',
      data: hours,
      splitArea: { show: false },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: 'rgba(255,255,255,0.4)', fontSize: 10, interval: 5 }
    },
    yAxis: {
      type: 'category',
      data: days,
      splitArea: { show: false },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: 'rgba(255,255,255,0.6)', fontSize: 11 }
    },
    visualMap: {
      min: 0,
      max: 10,
      show: false,
      inRange: {
        color: ['#1e3a5f', '#2563eb', '#f97316', '#ef4444']
      }
    },
    series: [{
      type: 'heatmap',
      data: data,
      label: { show: false },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  })
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)

  trendChart.setOption({
    ...chartTheme,
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(26,26,36,0.95)',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#fff' }
    },
    grid: {
      top: 20,
      left: 40,
      right: 20,
      bottom: 30
    },
    xAxis: {
      type: 'category',
      data: hours,
      boundaryGap: false,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: 'rgba(255,255,255,0.4)', fontSize: 10, interval: 3 }
    },
    yAxis: {
      type: 'value',
      name: '风险指数',
      nameTextStyle: { color: 'rgba(255,255,255,0.4)', fontSize: 10 },
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      axisLabel: { color: 'rgba(255,255,255,0.4)', fontSize: 10 }
    },
    series: [{
      name: '风险指数',
      type: 'line',
      smooth: true,
      symbol: 'none',
      data: [2, 1, 1, 2, 3, 2, 4, 5, 6, 5, 4, 3, 4, 5, 7, 8, 6, 5, 4, 3, 2, 2, 1, 1],
      lineStyle: {
        width: 3,
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#3b82f6' },
          { offset: 0.5, color: '#f97316' },
          { offset: 1, color: '#ef4444' }
        ])
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(249, 115, 22, 0.3)' },
          { offset: 1, color: 'rgba(249, 115, 22, 0)' }
        ])
      }
    }]
  })
}

const updateCharts = () => {
  updateTypeChart()
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

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
  window.removeEventListener('resize', handleResize)
  typeChart?.dispose()
  heatmapChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped>
/* ============================================
   可视化大屏 - 温暖科技感设计
   ============================================ */

.dashboard {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0d0d12 100%);
  color: var(--neutral-700);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(249, 115, 22, 0.15) 0%, transparent 50%),
              radial-gradient(ellipse 60% 40% at 100% 100%, rgba(16, 185, 129, 0.1) 0%, transparent 50%);
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 50px 50px;
}

.bg-noise {
  position: absolute;
  inset: 0;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
}

/* 顶部导航 */
.dashboard-header {
  height: 72px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  animation: pulse 3s ease-in-out infinite;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.system-name {
  font-family: var(--font-display);
  font-size: 20px;
  font-weight: 700;
  color: var(--neutral-800);
  line-height: 1.2;
}

.system-name .accent {
  font-weight: 300;
  background: linear-gradient(135deg, var(--primary-400) 0%, var(--primary-500) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.system-desc {
  font-size: 12px;
  color: var(--neutral-400);
  letter-spacing: 0.05em;
}

.header-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--radius-full);
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: var(--success-400);
  border-radius: 50%;
  animation: pulseDot 2s ease-in-out infinite;
}

@keyframes pulseDot {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

.status-label {
  font-size: 13px;
  color: var(--success-400);
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  border: none;
  border-radius: var(--radius-lg);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(249, 115, 22, 0.4);
}

.datetime-display {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.datetime-display .time {
  font-family: var(--font-mono);
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary-400) 0%, var(--primary-500) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.datetime-display .date {
  font-size: 12px;
  color: var(--neutral-400);
  margin-top: 4px;
}

/* 主内容区 */
.dashboard-content {
  flex: 1;
  display: grid;
  grid-template-columns: 280px 1fr 280px;
  gap: 20px;
  padding: 20px;
  position: relative;
  z-index: 1;
  overflow: hidden;
}

/* 面板通用样式 */
.panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-lg);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all var(--transition-base);
}

.stat-card:hover {
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  background: rgba(249, 115, 22, 0.15);
  color: var(--primary-400);
}

.stat-icon svg {
  width: 20px;
  height: 20px;
}

.stat-icon.danger {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

.stat-icon.success {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-400);
}

.stat-icon.info {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  color: var(--neutral-800);
  line-height: 1;
}

.stat-value.animate-value {
  animation: countUp 0.5s ease-out;
}

@keyframes countUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-label {
  font-size: 12px;
  color: var(--neutral-400);
  margin-top: 4px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.stat-trend svg {
  width: 14px;
  height: 14px;
}

.stat-trend.up {
  color: var(--success-400);
}

.stat-trend.down {
  color: var(--danger-400);
}

/* 卡片通用样式 */
.card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 600;
  color: var(--neutral-700);
  margin: 0;
}

.title-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-400);
}

.title-icon svg {
  width: 18px;
  height: 18px;
}

.title-icon.live {
  background: var(--danger-500);
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
}

.live-dot {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
}

.title-icon.success {
  color: var(--success-400);
}

.title-icon.warning {
  color: var(--warning-400);
}

.card-body {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 图表卡片 */
.chart-card {
  flex: 1;
  min-height: 200px;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 180px;
}

/* 监控卡片 */
.monitor-card {
  flex: 1.2;
}

.monitor-body {
  padding: 0;
}

.camera-view {
  width: 100%;
  height: 100%;
  min-height: 300px;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.4) 0%, rgba(0, 0, 0, 0.2) 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.camera-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: var(--neutral-400);
}

.placeholder-icon {
  width: 64px;
  height: 64px;
  opacity: 0.5;
}

.placeholder-icon svg {
  width: 100%;
  height: 100%;
}

.placeholder-title {
  font-size: 16px;
  font-weight: 500;
}

.placeholder-subtitle {
  font-size: 13px;
  color: var(--neutral-400);
}

.privacy-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: var(--radius-full);
  color: var(--success-400);
  font-size: 12px;
  font-weight: 500;
}

.privacy-badge svg {
  width: 14px;
  height: 14px;
}

.camera-overlay {
  position: absolute;
  top: 16px;
  left: 16px;
  right: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.overlay-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-md);
}

.camera-name {
  font-size: 13px;
  font-weight: 500;
  color: white;
}

.camera-time {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--neutral-400);
}

.overlay-badges {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 6px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
}

.badge-success {
  background: rgba(16, 185, 129, 0.2);
  color: var(--success-400);
}

.scan-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary-400), transparent);
  animation: scanLine 3s linear infinite;
}

@keyframes scanLine {
  0% {
    top: 0;
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    top: 100%;
    opacity: 0;
  }
}

/* 事件卡片 */
.events-card {
  flex: 0.8;
  max-height: 320px;
}

.view-all {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--primary-400);
  text-decoration: none;
  transition: color var(--transition-base);
}

.view-all svg {
  width: 14px;
  height: 14px;
  transition: transform var(--transition-base);
}

.view-all:hover {
  color: var(--primary-300);
}

.view-all:hover svg {
  transform: translateX(2px);
}

.events-body {
  overflow: hidden;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  max-height: 200px;
}

.events-list::-webkit-scrollbar {
  width: 4px;
}

.events-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.event-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-md);
  border-left: 3px solid;
  transition: all var(--transition-base);
}

.event-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.event-item.risk-high {
  border-left-color: var(--danger-400);
}

.event-item.risk-medium {
  border-left-color: var(--warning-400);
}

.event-item.risk-low {
  border-left-color: var(--info-400);
}

.event-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.event-icon svg {
  width: 20px;
  height: 20px;
}

.event-icon.icon-fall {
  color: var(--danger-400);
}

.event-icon.icon-stillness {
  color: var(--warning-400);
}

.event-icon.icon-night_activity {
  color: var(--info-400);
}

.event-content {
  flex: 1;
  min-width: 0;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.event-type {
  font-size: 14px;
  font-weight: 500;
  color: var(--neutral-700);
}

.event-time {
  font-size: 12px;
  color: var(--neutral-400);
  font-family: var(--font-mono);
}

.event-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--neutral-400);
}

.risk-tag {
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
}

.risk-tag.tag-high {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

.risk-tag.tag-medium {
  background: rgba(245, 158, 11, 0.15);
  color: var(--warning-400);
}

.risk-tag.tag-low {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--neutral-400);
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-state.small {
  padding: 20px;
}

.empty-state.small svg {
  width: 32px;
  height: 32px;
}

/* 告警卡片 */
.alerts-card {
  flex: 1;
}

.alert-count {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 8px;
  background: var(--danger-500);
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.alerts-body {
  overflow: hidden;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 180px;
  overflow-y: auto;
}

.alerts-list::-webkit-scrollbar {
  width: 4px;
}

.alerts-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-md);
  border-left: 3px solid;
  transition: all var(--transition-base);
}

.alert-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.alert-item.alert-high {
  border-left-color: var(--danger-400);
}

.alert-item.alert-medium {
  border-left-color: var(--warning-400);
}

.alert-item.alert-low {
  border-left-color: var(--info-400);
}

.alert-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  color: var(--warning-400);
  flex-shrink: 0;
}

.alert-icon svg {
  width: 16px;
  height: 16px;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-message {
  font-size: 13px;
  font-weight: 500;
  color: var(--neutral-700);
  margin-bottom: 2px;
}

.alert-time {
  font-size: 11px;
  color: var(--neutral-400);
}

/* 状态卡片 */
.status-card {
  flex: 0.8;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-md);
  transition: background var(--transition-base);
}

.status-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.status-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.status-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--neutral-700);
}

.status-desc {
  font-size: 12px;
  color: var(--neutral-400);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulseDot 2s ease-in-out infinite;
}

.status-indicator.online .indicator-dot {
  background: var(--success-400);
}

.indicator-text {
  font-size: 12px;
  font-weight: 500;
}

.status-indicator.online .indicator-text {
  color: var(--success-400);
}

/* 列表过渡动画 */
.event-list-enter-active,
.event-list-leave-active {
  transition: all var(--transition-slow);
}

.event-list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.event-list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.alert-list-enter-active,
.alert-list-leave-active {
  transition: all var(--transition-slow);
}

.alert-list-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.alert-list-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .dashboard-content {
    grid-template-columns: 240px 1fr 240px;
    gap: 16px;
    padding: 16px;
  }
}

@media (max-width: 1200px) {
  .dashboard-content {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
  }

  .panel {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .stats-grid {
    width: 100%;
  }

  .chart-card {
    flex: 1;
    min-width: 300px;
  }

  .monitor-card {
    flex: 1;
    min-width: 100%;
    min-height: 400px;
  }

  .events-card {
    flex: 1;
    min-width: 300px;
  }
}
</style>
