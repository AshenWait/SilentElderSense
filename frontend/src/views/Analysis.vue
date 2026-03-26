<template>
  <div class="analysis-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-gradient"></div>
      <div class="bg-grid"></div>
    </div>

    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">数据分析</h1>
        <p class="page-subtitle">事件统计与趋势分析</p>
      </div>
      <div class="header-right">
        <div class="time-filter">
          <button
            v-for="range in timeRanges"
            :key="range.value"
            :class="['filter-btn', { active: timeRange === range.value }]"
            @click="handleTimeRangeChange(range.value)"
          >
            {{ range.label }}
          </button>
        </div>
        <el-date-picker
          v-if="timeRange === 'custom'"
          v-model="customDateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          @change="handleDateChange"
          class="date-picker"
        />
        <button class="export-btn" @click="handleExport">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          <span>导出报告</span>
        </button>
      </div>
    </header>

    <!-- 统计卡片 -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card" v-for="stat in summaryStats" :key="stat.label">
          <div class="stat-visual">
            <div class="stat-ring" :style="{ '--progress': stat.progress }">
              <svg viewBox="0 0 36 36">
                <path
                  class="ring-bg"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  class="ring-fill"
                  :style="{ stroke: stat.color }"
                  stroke-dasharray="100, 100"
                  :stroke-dashoffset="100 - stat.progress"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <div class="stat-icon" :style="{ background: stat.color + '20', color: stat.color }">
                <component :is="stat.icon" />
              </div>
            </div>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
            <div class="stat-trend" v-if="stat.trend" :class="stat.trend > 0 ? 'up' : 'down'">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path :d="stat.trend > 0 ? 'M18 15l-6-6-6 6' : 'M6 9l6 6 6-6'"/>
              </svg>
              <span>{{ Math.abs(stat.trend) }}% 较上期</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 图表区域 -->
    <section class="charts-section">
      <div class="charts-grid">
        <!-- 事件趋势 -->
        <div class="chart-card large">
          <div class="card-header">
            <div class="header-title">
              <span class="title-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
              </span>
              <h3>事件趋势分析</h3>
            </div>
            <div class="chart-legend">
              <span class="legend-item" v-for="item in eventTypes" :key="item.key">
                <span class="legend-dot" :style="{ background: item.color }"></span>
                {{ item.label }}
              </span>
            </div>
          </div>
          <div class="card-body">
            <div ref="trendChartRef" class="chart-container"></div>
          </div>
        </div>

        <!-- 风险等级分布 -->
        <div class="chart-card">
          <div class="card-header">
            <div class="header-title">
              <span class="title-icon danger">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
              </span>
              <h3>风险等级分布</h3>
            </div>
          </div>
          <div class="card-body">
            <div ref="riskChartRef" class="chart-container"></div>
          </div>
        </div>

        <!-- 事件类型分布 -->
        <div class="chart-card">
          <div class="card-header">
            <div class="header-title">
              <span class="title-icon primary">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>
                  <path d="M22 12A10 10 0 0 0 12 2v10z"/>
                </svg>
              </span>
              <h3>事件类型分布</h3>
            </div>
          </div>
          <div class="card-body">
            <div ref="typeChartRef" class="chart-container"></div>
          </div>
        </div>

        <!-- 处理状态 -->
        <div class="chart-card">
          <div class="card-header">
            <div class="header-title">
              <span class="title-icon success">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
              </span>
              <h3>处理状态分布</h3>
            </div>
          </div>
          <div class="card-body">
            <div ref="statusChartRef" class="chart-container"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 数据表格 -->
    <section class="table-section">
      <div class="table-card">
        <div class="card-header">
          <div class="header-title">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
            </span>
            <h3>详细统计数据</h3>
          </div>
          <div class="table-actions">
            <div class="search-box">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/>
                <path d="M21 21l-4.35-4.35"/>
              </svg>
              <input type="text" v-model="searchQuery" placeholder="搜索事件..." />
            </div>
          </div>
        </div>
        <div class="card-body">
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>事件类型</th>
                  <th>风险等级</th>
                  <th>发生时间</th>
                  <th>持续时间</th>
                  <th>状态</th>
                  <th>备注</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="event in filteredEvents" :key="event.id" class="table-row">
                  <td class="cell-id">#{{ event.id }}</td>
                  <td>
                    <div class="type-cell">
                      <span class="type-icon" :class="getTypeClass(event.event_type)">
                        <svg v-if="event.event_type === 'FALL'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                        </svg>
                        <svg v-else-if="event.event_type === 'STILLNESS'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <circle cx="12" cy="12" r="10"/>
                          <polyline points="12 6 12 12 16 14"/>
                        </svg>
                        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                        </svg>
                      </span>
                      <span>{{ getTypeLabel(event.event_type) }}</span>
                    </div>
                  </td>
                  <td>
                    <span class="risk-badge" :class="getRiskClass(event.risk_level)">
                      {{ getRiskLabel(event.risk_level) }}
                    </span>
                  </td>
                  <td class="cell-time">{{ formatDateTime(event.start_time) }}</td>
                  <td>{{ formatDuration(event.duration) }}</td>
                  <td>
                    <span class="status-badge" :class="getStatusClass(event.status)">
                      <span class="status-dot"></span>
                      {{ getStatusLabel(event.status) }}
                    </span>
                  </td>
                  <td class="cell-notes">{{ event.notes || '-' }}</td>
                </tr>
              </tbody>
            </table>
            <div v-if="filteredEvents.length === 0" class="empty-table">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 12l2 2 4-4"/>
                <circle cx="12" cy="12" r="10"/>
              </svg>
              <p>暂无数据</p>
            </div>
          </div>
          <div class="pagination">
            <div class="pagination-info">
              共 <strong>{{ total }}</strong> 条记录
            </div>
            <div class="pagination-controls">
              <button
                class="page-btn"
                :disabled="currentPage === 1"
                @click="handlePageChange(currentPage - 1)"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M15 18l-6-6 6-6"/>
                </svg>
              </button>
              <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
              <button
                class="page-btn"
                :disabled="currentPage >= totalPages"
                @click="handlePageChange(currentPage + 1)"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 18l6-6-6-6"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch, h } from 'vue'
import * as echarts from 'echarts'
import { getEvents, getEventStats } from '@/api/events'

// 时间范围选项
const timeRanges = [
  { label: '今日', value: 'today' },
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '自定义', value: 'custom' }
]

const timeRange = ref('week')
const customDateRange = ref(null)
const loading = ref(false)
const searchQuery = ref('')

// 图表引用
const trendChartRef = ref(null)
const riskChartRef = ref(null)
const typeChartRef = ref(null)
const statusChartRef = ref(null)

let trendChart = null
let riskChart = null
let typeChart = null
let statusChart = null

// 数据
const eventsData = ref([])
const stats = ref({
  total: 0,
  by_type: {},
  by_risk: {},
  by_status: {}
})

const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const totalPages = computed(() => Math.ceil(total.value / pageSize.value) || 1)

// 事件类型配置
const eventTypes = [
  { key: 'FALL', label: '跌倒检测', color: '#f97316' },
  { key: 'STILLNESS', label: '长时间静止', color: '#eab308' },
  { key: 'NIGHT_ACTIVITY', label: '夜间异常活动', color: '#3b82f6' }
]

// 统计卡片数据
const summaryStats = computed(() => [
  {
    label: '总事件数',
    value: stats.value.total,
    progress: Math.min((stats.value.total / 100) * 100, 100),
    trend: 5.2,
    color: '#f97316',
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M22 12h-4l-3 9L9 3l-3 9H2' })
    ])
  },
  {
    label: '高风险事件',
    value: stats.value.by_risk?.HIGH || 0,
    progress: stats.value.total > 0 ? ((stats.value.by_risk?.HIGH || 0) / stats.value.total) * 100 : 0,
    trend: -2.1,
    color: '#ef4444',
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z' })
    ])
  },
  {
    label: '待处理',
    value: stats.value.by_status?.pending || 0,
    progress: stats.value.total > 0 ? ((stats.value.by_status?.pending || 0) / stats.value.total) * 100 : 0,
    color: '#eab308',
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('circle', { cx: '12', cy: '12', r: '10' }),
      h('polyline', { points: '12 6 12 12 16 14' })
    ])
  },
  {
    label: '已确认',
    value: stats.value.by_status?.confirmed || 0,
    progress: stats.value.total > 0 ? ((stats.value.by_status?.confirmed || 0) / stats.value.total) * 100 : 0,
    trend: 8.5,
    color: '#10b981',
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M22 11.08V12a10 10 0 1 1-5.93-9.14' }),
      h('polyline', { points: '22 4 12 14.01 9 11.01' })
    ])
  }
])

// 过滤后的事件数据
const filteredEvents = computed(() => {
  if (!searchQuery.value) return eventsData.value
  const query = searchQuery.value.toLowerCase()
  return eventsData.value.filter(event =>
    getTypeLabel(event.event_type).toLowerCase().includes(query) ||
    getRiskLabel(event.risk_level).toLowerCase().includes(query) ||
    (event.notes && event.notes.toLowerCase().includes(query))
  )
})

// 工具函数
const getTypeLabel = (type) => {
  const map = { FALL: '跌倒检测', STILLNESS: '长时间静止', NIGHT_ACTIVITY: '夜间异常活动' }
  return map[type] || type
}

const getRiskLabel = (level) => {
  const map = { HIGH: '高风险', MEDIUM: '中风险', LOW: '低风险' }
  return map[level] || level
}

const getStatusLabel = (status) => {
  const map = { pending: '待处理', confirmed: '已确认', false_alarm: '误报' }
  return map[status] || status
}

const getTypeClass = (type) => {
  const map = { FALL: 'type-fall', STILLNESS: 'type-stillness', NIGHT_ACTIVITY: 'type-night' }
  return map[type] || ''
}

const getRiskClass = (level) => {
  const map = { HIGH: 'risk-high', MEDIUM: 'risk-medium', LOW: 'risk-low' }
  return map[level] || ''
}

const getStatusClass = (status) => {
  const map = { pending: 'status-pending', confirmed: 'status-confirmed', false_alarm: 'status-false' }
  return map[status] || ''
}

const formatDuration = (seconds) => {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds.toFixed(1)}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分${(seconds % 60).toFixed(0)}秒`
  return `${Math.floor(seconds / 3600)}时${Math.floor((seconds % 3600) / 60)}分`
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  const date = new Date(datetime)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getDaysByRange = () => {
  switch (timeRange.value) {
    case 'today': return 1
    case 'week': return 7
    case 'month': return 30
    default: return 7
  }
}

// 数据加载
const loadData = async () => {
  loading.value = true
  try {
    const days = getDaysByRange()
    const [eventsRes, statsRes] = await Promise.all([
      getEvents({ page: currentPage.value, per_page: pageSize.value }),
      getEventStats({ days })
    ])

    eventsData.value = eventsRes.events || []
    total.value = eventsRes.total || 0
    stats.value = statsRes

    updateCharts()
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 图表初始化
const chartTheme = {
  backgroundColor: 'transparent',
  textStyle: { color: 'rgba(255,255,255,0.6)' }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  updateTrendChart()
}

const updateTrendChart = () => {
  if (!trendChart) return
  const s = stats.value

  trendChart.setOption({
    ...chartTheme,
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(26,26,36,0.95)',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#fff' }
    },
    legend: {
      data: ['跌倒检测', '长时间静止', '夜间异常活动'],
      textStyle: { color: 'rgba(255,255,255,0.6)' },
      top: 0,
      right: 0
    },
    grid: {
      top: 40,
      left: 50,
      right: 20,
      bottom: 30
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: 'rgba(255,255,255,0.5)' }
    },
    yAxis: {
      type: 'value',
      name: '事件数量',
      nameTextStyle: { color: 'rgba(255,255,255,0.4)' },
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      axisLabel: { color: 'rgba(255,255,255,0.5)' }
    },
    series: [
      {
        name: '跌倒检测',
        type: 'line',
        smooth: true,
        data: [s.by_type?.FALL ? Math.floor(s.by_type.FALL / 7) : 2, 3, 2, 4, 3, 2, 1],
        lineStyle: { width: 3, color: '#f97316' },
        itemStyle: { color: '#f97316' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(249, 115, 22, 0.3)' },
            { offset: 1, color: 'rgba(249, 115, 22, 0)' }
          ])
        }
      },
      {
        name: '长时间静止',
        type: 'line',
        smooth: true,
        data: [s.by_type?.STILLNESS ? Math.floor(s.by_type.STILLNESS / 7) : 3, 4, 3, 2, 4, 3, 2],
        lineStyle: { width: 3, color: '#eab308' },
        itemStyle: { color: '#eab308' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(234, 179, 8, 0.3)' },
            { offset: 1, color: 'rgba(234, 179, 8, 0)' }
          ])
        }
      },
      {
        name: '夜间异常活动',
        type: 'line',
        smooth: true,
        data: [s.by_type?.NIGHT_ACTIVITY ? Math.floor(s.by_type.NIGHT_ACTIVITY / 7) : 1, 2, 1, 2, 1, 2, 1],
        lineStyle: { width: 3, color: '#3b82f6' },
        itemStyle: { color: '#3b82f6' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0)' }
          ])
        }
      }
    ]
  })
}

const initRiskChart = () => {
  if (!riskChartRef.value) return
  riskChart = echarts.init(riskChartRef.value)
  updateRiskChart()
}

const updateRiskChart = () => {
  if (!riskChart) return
  const s = stats.value

  riskChart.setOption({
    ...chartTheme,
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(26,26,36,0.95)',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#fff' }
    },
    series: [{
      type: 'pie',
      radius: ['50%', '75%'],
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
        fontSize: 12,
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
        { value: s.by_risk?.HIGH || 0, name: '高风险', itemStyle: { color: '#ef4444' } },
        { value: s.by_risk?.MEDIUM || 0, name: '中风险', itemStyle: { color: '#eab308' } },
        { value: s.by_risk?.LOW || 0, name: '低风险', itemStyle: { color: '#3b82f6' } }
      ]
    }]
  })
}

const initTypeChart = () => {
  if (!typeChartRef.value) return
  typeChart = echarts.init(typeChartRef.value)
  updateTypeChart()
}

const updateTypeChart = () => {
  if (!typeChart) return
  const s = stats.value

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
      radius: ['40%', '70%'],
      center: ['50%', '50%'],
      roseType: 'radius',
      itemStyle: {
        borderRadius: 8,
        borderColor: 'rgba(26,26,36,0.8)',
        borderWidth: 2
      },
      label: {
        show: true,
        color: 'rgba(255,255,255,0.7)',
        fontSize: 11
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 20,
          shadowColor: 'rgba(0,0,0,0.5)'
        }
      },
      data: [
        { value: s.by_type?.FALL || 0, name: '跌倒检测', itemStyle: { color: '#f97316' } },
        { value: s.by_type?.STILLNESS || 0, name: '长时间静止', itemStyle: { color: '#eab308' } },
        { value: s.by_type?.NIGHT_ACTIVITY || 0, name: '夜间异常', itemStyle: { color: '#3b82f6' } }
      ]
    }]
  })
}

const initStatusChart = () => {
  if (!statusChartRef.value) return
  statusChart = echarts.init(statusChartRef.value)
  updateStatusChart()
}

const updateStatusChart = () => {
  if (!statusChart) return
  const s = stats.value

  statusChart.setOption({
    ...chartTheme,
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(26,26,36,0.95)',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#fff' },
      axisPointer: { type: 'shadow' }
    },
    grid: {
      top: 20,
      left: 50,
      right: 20,
      bottom: 30
    },
    xAxis: {
      type: 'category',
      data: ['待处理', '已确认', '误报'],
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: 'rgba(255,255,255,0.5)' }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      axisLabel: { color: 'rgba(255,255,255,0.5)' }
    },
    series: [{
      type: 'bar',
      barWidth: '50%',
      data: [
        { value: s.by_status?.pending || 0, itemStyle: { color: '#eab308', borderRadius: [8, 8, 0, 0] } },
        { value: s.by_status?.confirmed || 0, itemStyle: { color: '#10b981', borderRadius: [8, 8, 0, 0] } },
        { value: s.by_status?.false_alarm || 0, itemStyle: { color: '#6b7280', borderRadius: [8, 8, 0, 0] } }
      ]
    }]
  })
}

const updateCharts = () => {
  updateTrendChart()
  updateRiskChart()
  updateTypeChart()
  updateStatusChart()
}

const handleResize = () => {
  trendChart?.resize()
  riskChart?.resize()
  typeChart?.resize()
  statusChart?.resize()
}

const handleTimeRangeChange = (range) => {
  timeRange.value = range
  currentPage.value = 1
  loadData()
}

const handleDateChange = () => {
  currentPage.value = 1
  loadData()
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadData()
}

const handleExport = () => {
  // 导出功能
  console.log('Export report')
}

onMounted(async () => {
  await loadData()
  nextTick(() => {
    initTrendChart()
    initRiskChart()
    initTypeChart()
    initStatusChart()
    window.addEventListener('resize', handleResize)
  })
})

watch(timeRange, () => {
  loadData()
})
</script>

<style scoped>
/* ============================================
   数据分析页面 - 温暖科技感设计
   ============================================ */

.analysis-page {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0d0d12 100%);
  color: var(--neutral-700);
  position: relative;
  overflow-x: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 60% 40% at 0% 0%, rgba(249, 115, 22, 0.08) 0%, transparent 50%),
              radial-gradient(ellipse 50% 30% at 100% 100%, rgba(16, 185, 129, 0.05) 0%, transparent 50%);
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
  background-size: 60px 60px;
}

/* 页面头部 */
.page-header {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  background: rgba(26, 26, 36, 0.4);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 700;
  color: var(--neutral-800);
  margin: 0;
}

.page-subtitle {
  font-size: 14px;
  color: var(--neutral-400);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.time-filter {
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-lg);
  padding: 4px;
}

.filter-btn {
  padding: 10px 20px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--neutral-400);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
}

.filter-btn:hover {
  color: var(--neutral-600);
}

.filter-btn.active {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
}

.date-picker {
  width: 280px;
}

.date-picker :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
  color: var(--neutral-600);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
}

.export-btn svg {
  width: 18px;
  height: 18px;
}

.export-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

/* 统计卡片 */
.stats-section {
  position: relative;
  z-index: 1;
  padding: 24px 32px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all var(--transition-base);
}

.stat-card:hover {
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}

.stat-visual {
  position: relative;
}

.stat-ring {
  position: relative;
  width: 72px;
  height: 72px;
}

.stat-ring svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.05);
  stroke-width: 3;
}

.ring-fill {
  fill: none;
  stroke-width: 3;
  stroke-linecap: round;
  transition: stroke-dashoffset 1s ease-out;
}

.stat-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon svg {
  width: 18px;
  height: 18px;
}

.stat-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  color: var(--neutral-800);
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--neutral-400);
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
  margin-top: 4px;
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

/* 图表区域 */
.charts-section {
  position: relative;
  z-index: 1;
  padding: 0 32px 24px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: auto auto;
  gap: 20px;
}

.chart-card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chart-card.large {
  grid-column: span 2;
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(249, 115, 22, 0.15);
  border-radius: var(--radius-md);
  color: var(--primary-400);
}

.title-icon svg {
  width: 18px;
  height: 18px;
}

.title-icon.danger {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

.title-icon.success {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-400);
}

.title-icon.primary {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.header-title h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--neutral-700);
  margin: 0;
}

.chart-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--neutral-400);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.card-body {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chart-container {
  width: 100%;
  flex: 1;
  min-height: 280px;
}

.chart-card:not(.large) .chart-container {
  min-height: 220px;
}

/* 表格区域 */
.table-section {
  position: relative;
  z-index: 1;
  padding: 0 32px 32px;
}

.table-card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.table-actions {
  display: flex;
  gap: 12px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
}

.search-box:focus-within {
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15);
}

.search-box svg {
  width: 18px;
  height: 18px;
  color: var(--neutral-400);
}

.search-box input {
  background: transparent;
  border: none;
  outline: none;
  color: var(--neutral-700);
  font-size: 14px;
  width: 200px;
}

.search-box input::placeholder {
  color: var(--neutral-400);
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 16px 20px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: var(--neutral-400);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.data-table td {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.table-row {
  transition: background var(--transition-base);
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.02);
}

.cell-id {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--neutral-400);
}

.type-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.type-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
}

.type-icon svg {
  width: 16px;
  height: 16px;
}

.type-icon.type-fall {
  background: rgba(249, 115, 22, 0.15);
  color: var(--primary-400);
}

.type-icon.type-stillness {
  background: rgba(234, 179, 8, 0.15);
  color: var(--warning-400);
}

.type-icon.type-night {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.risk-badge {
  display: inline-flex;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
}

.risk-badge.risk-high {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

.risk-badge.risk-medium {
  background: rgba(234, 179, 8, 0.15);
  color: var(--warning-400);
}

.risk-badge.risk-low {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.cell-time {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--neutral-500);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-badge.status-pending {
  background: rgba(234, 179, 8, 0.15);
  color: var(--warning-400);
}

.status-badge.status-pending .status-dot {
  background: var(--warning-400);
}

.status-badge.status-confirmed {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-400);
}

.status-badge.status-confirmed .status-dot {
  background: var(--success-400);
}

.status-badge.status-false {
  background: rgba(107, 114, 128, 0.15);
  color: var(--neutral-400);
}

.status-badge.status-false .status-dot {
  background: var(--neutral-400);
}

.cell-notes {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  color: var(--neutral-400);
}

.empty-table {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: var(--neutral-400);
}

.empty-table svg {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.pagination-info {
  font-size: 14px;
  color: var(--neutral-400);
}

.pagination-info strong {
  color: var(--neutral-600);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  color: var(--neutral-500);
  cursor: pointer;
  transition: all var(--transition-base);
}

.page-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-btn svg {
  width: 18px;
  height: 18px;
}

.page-info {
  font-size: 14px;
  color: var(--neutral-500);
}

/* 响应式 */
@media (max-width: 1400px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-card.large {
    grid-column: span 2;
  }
}

@media (max-width: 1024px) {
  .page-header {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }

  .header-right {
    width: 100%;
    flex-wrap: wrap;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .chart-card.large {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .time-filter {
    flex-wrap: wrap;
  }
}
</style>
