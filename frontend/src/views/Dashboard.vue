<template>
  <div class="dashboard-page">
    <!-- 统计卡片 -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card" v-for="(stat, index) in statsCards" :key="stat.key">
          <div class="stat-icon" :class="stat.type">
            <component :is="stat.icon" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
          <div class="stat-trend" v-if="stat.trend" :class="stat.trend > 0 ? 'up' : 'down'">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path :d="stat.trend > 0 ? 'M18 15l-6-6-6 6' : 'M6 9l6 6 6-6'"/>
            </svg>
            <span>{{ Math.abs(stat.trend) }}%</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 图表区域 -->
    <section class="charts-section">
      <div class="charts-grid">
        <!-- 事件类型分布 -->
        <div class="chart-card">
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
            <div ref="typeChartRef" class="chart-container"></div>
          </div>
        </div>

        <!-- 风险等级分布 -->
        <div class="chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <span class="title-icon danger">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
              </span>
              风险等级分布
            </h3>
          </div>
          <div class="card-body">
            <div ref="riskChartRef" class="chart-container"></div>
          </div>
        </div>

        <!-- 处理状态 -->
        <div class="chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <span class="title-icon success">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
              </span>
              处理状态分布
            </h3>
          </div>
          <div class="card-body">
            <div ref="statusChartRef" class="chart-container"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 事件列表 -->
    <section class="events-section">
      <div class="events-card">
        <div class="card-header">
          <h3 class="card-title">
            <span class="title-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
            </span>
            异常事件列表
          </h3>
          <div class="filter-group">
            <select v-model="filterType" class="filter-select" @change="loadEvents">
              <option value="">全部类型</option>
              <option value="FALL">跌倒检测</option>
              <option value="STATIC">长时间静止</option>
              <option value="NIGHT_ACTIVITY">夜间异常活动</option>
            </select>
            <select v-model="filterStatus" class="filter-select" @change="loadEvents">
              <option value="">全部状态</option>
              <option value="pending">待处理</option>
              <option value="confirmed">已确认</option>
              <option value="false_alarm">误报</option>
            </select>
            <select v-model="filterRisk" class="filter-select" @change="loadEvents">
              <option value="">全部风险</option>
              <option value="HIGH">高风险</option>
              <option value="MEDIUM">中风险</option>
              <option value="LOW">低风险</option>
            </select>
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
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="event in eventsStore.events" :key="event.id" class="table-row">
                  <td class="cell-id">#{{ event.id }}</td>
                  <td>
                    <span class="type-badge" :class="getTypeClass(event.event_type)">
                      {{ event.typeName || getTypeLabel(event.event_type) }}
                    </span>
                  </td>
                  <td>
                    <span class="risk-badge" :class="getRiskClass(event.riskLevel)">
                      {{ getRiskLabel(event.riskLevel) }}
                    </span>
                  </td>
                  <td class="cell-time">{{ event.start_time }}</td>
                  <td>{{ formatDuration(event.duration) }}</td>
                  <td>
                    <span class="status-badge" :class="getStatusClass(event.status)">
                      <span class="status-dot"></span>
                      {{ getStatusLabel(event.status) }}
                    </span>
                  </td>
                  <td>
                    <div class="action-btns">
                      <button
                        v-if="event.status === 'pending'"
                        class="action-btn primary"
                        @click="handleEvent(event)"
                      >
                        处理
                      </button>
                      <button class="action-btn secondary" @click="viewDetails(event)">
                        详情
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="eventsStore.events.length === 0" class="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 12l2 2 4-4"/>
                <circle cx="12" cy="12" r="10"/>
              </svg>
              <p>暂无事件数据</p>
            </div>
          </div>
          <div class="pagination">
            <div class="pagination-info">
              共 <strong>{{ eventsStore.pagination.total }}</strong> 条记录
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

    <!-- 详情弹窗 -->
    <div v-if="detailDialogVisible" class="modal-overlay" @click.self="detailDialogVisible = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>事件详情</h3>
          <button class="modal-close" @click="detailDialogVisible = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body" v-if="selectedEvent">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">事件ID</span>
              <span class="detail-value">#{{ selectedEvent.id }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">事件类型</span>
              <span class="detail-value">{{ selectedEvent.typeName || getTypeLabel(selectedEvent.event_type) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">风险等级</span>
              <span class="risk-badge" :class="getRiskClass(selectedEvent.riskLevel)">
                {{ getRiskLabel(selectedEvent.riskLevel) }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">处理状态</span>
              <span class="status-badge" :class="getStatusClass(selectedEvent.status)">
                <span class="status-dot"></span>
                {{ getStatusLabel(selectedEvent.status) }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">开始时间</span>
              <span class="detail-value">{{ selectedEvent.start_time }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">结束时间</span>
              <span class="detail-value">{{ selectedEvent.end_time || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">持续时间</span>
              <span class="detail-value">{{ formatDuration(selectedEvent.duration) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">帧数</span>
              <span class="detail-value">{{ selectedEvent.frame_count || '-' }}</span>
            </div>
            <div class="detail-item full-width">
              <span class="detail-label">备注</span>
              <span class="detail-value">{{ selectedEvent.notes || '无' }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="detailDialogVisible = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, h } from 'vue'
import { useEventsStore } from '@/stores/events'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'

const eventsStore = useEventsStore()

const filterType = ref('')
const filterStatus = ref('')
const filterRisk = ref('')
const currentPage = ref(1)
const detailDialogVisible = ref(false)
const selectedEvent = ref(null)

const typeChartRef = ref(null)
const riskChartRef = ref(null)
const statusChartRef = ref(null)

let typeChart = null
let riskChart = null
let statusChart = null

const totalPages = computed(() => Math.ceil(eventsStore.pagination.total / 20) || 1)

// 统计卡片数据
const statsCards = computed(() => [
  {
    key: 'total',
    label: '总事件数',
    value: eventsStore.statistics.total,
    type: 'primary',
    trend: 5.2,
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M22 12h-4l-3 9L9 3l-3 9H2' })
    ])
  },
  {
    key: 'fall',
    label: '跌倒检测',
    value: eventsStore.statsFormatted.fall,
    type: 'danger',
    trend: -2.1,
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z' })
    ])
  },
  {
    key: 'stillness',
    label: '长时间静止',
    value: eventsStore.statsFormatted.stillness,
    type: 'warning',
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('circle', { cx: '12', cy: '12', r: '10' }),
      h('polyline', { points: '12 6 12 12 16 14' })
    ])
  },
  {
    key: 'pending',
    label: '待处理',
    value: eventsStore.statsFormatted.pending,
    type: 'info',
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9' }),
      h('path', { d: 'M13.73 21a2 2 0 0 1-3.46 0' })
    ])
  }
])

// 工具函数
const getTypeLabel = (type) => {
  const map = { FALL: '跌倒检测', STATIC: '长时间静止', STILLNESS: '长时间静止', NIGHT_ACTIVITY: '夜间异常活动' }
  return map[type] || type
}

const getTypeClass = (type) => {
  const map = { FALL: 'type-fall', STATIC: 'type-stillness', STILLNESS: 'type-stillness', NIGHT_ACTIVITY: 'type-night' }
  return map[type] || ''
}

const getRiskLabel = (level) => {
  const map = { HIGH: '高风险', MEDIUM: '中风险', LOW: '低风险' }
  return map[level] || level
}

const getRiskClass = (level) => {
  const map = { HIGH: 'risk-high', MEDIUM: 'risk-medium', LOW: 'risk-low' }
  return map[level] || ''
}

const getStatusLabel = (status) => {
  const map = { pending: '待处理', confirmed: '已确认', false_alarm: '误报' }
  return map[status] || status
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

// 数据加载
const loadEvents = async () => {
  const params = { page: currentPage.value, per_page: 20 }
  if (filterType.value) params.event_type = filterType.value
  if (filterStatus.value) params.status = filterStatus.value
  if (filterRisk.value) params.risk_level = filterRisk.value
  await eventsStore.fetchEvents(params)
  updateCharts()
}

const loadStats = async () => {
  await eventsStore.fetchStats({ days: 7 })
  updateCharts()
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadEvents()
}

const handleEvent = (event) => {
  ElMessageBox.prompt('请选择处理结果', '处理事件', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputType: 'select',
    inputOptions: { confirmed: '已确认', false_alarm: '误报' }
  }).then(async ({ value }) => {
    await eventsStore.updateEventStatus(event.id, { status: value })
    ElMessage.success('事件已处理')
    loadEvents()
    loadStats()
  }).catch(() => {})
}

const viewDetails = async (event) => {
  selectedEvent.value = event
  detailDialogVisible.value = true
  try {
    const detail = await eventsStore.fetchEventDetail(event.id)
    selectedEvent.value = detail
  } catch (error) {
    ElMessage.error('获取详情失败')
  }
}

// 图表配置
const chartTheme = {
  backgroundColor: 'transparent',
  textStyle: { color: 'rgba(255,255,255,0.6)' }
}

const initCharts = () => {
  typeChart = echarts.init(typeChartRef.value)
  riskChart = echarts.init(riskChartRef.value)
  statusChart = echarts.init(statusChartRef.value)
  updateCharts()
}

const updateCharts = () => {
  const stats = eventsStore.statistics

  if (typeChart) {
    typeChart.setOption({
      ...chartTheme,
      tooltip: { trigger: 'item', backgroundColor: 'rgba(26,26,36,0.95)', borderColor: 'rgba(255,255,255,0.1)', textStyle: { color: '#fff' } },
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        itemStyle: { borderRadius: 8, borderColor: 'rgba(26,26,36,0.8)', borderWidth: 3 },
        label: { show: true, color: 'rgba(255,255,255,0.7)', fontSize: 12 },
        data: [
          { value: stats.by_type?.FALL || 0, name: '跌倒检测', itemStyle: { color: '#f97316' } },
          { value: (stats.by_type?.STILLNESS || 0) + (stats.by_type?.STATIC || 0), name: '长时间静止', itemStyle: { color: '#eab308' } },
          { value: stats.by_type?.NIGHT_ACTIVITY || 0, name: '夜间异常', itemStyle: { color: '#3b82f6' } }
        ]
      }]
    })
  }

  if (riskChart) {
    riskChart.setOption({
      ...chartTheme,
      tooltip: { trigger: 'item', backgroundColor: 'rgba(26,26,36,0.95)', borderColor: 'rgba(255,255,255,0.1)', textStyle: { color: '#fff' } },
      series: [{
        type: 'pie',
        radius: ['50%', '75%'],
        itemStyle: { borderRadius: 8, borderColor: 'rgba(26,26,36,0.8)', borderWidth: 3 },
        label: { show: true, color: 'rgba(255,255,255,0.7)', fontSize: 12 },
        data: [
          { value: stats.by_risk?.HIGH || 0, name: '高风险', itemStyle: { color: '#ef4444' } },
          { value: stats.by_risk?.MEDIUM || 0, name: '中风险', itemStyle: { color: '#eab308' } },
          { value: stats.by_risk?.LOW || 0, name: '低风险', itemStyle: { color: '#3b82f6' } }
        ]
      }]
    })
  }

  if (statusChart) {
    statusChart.setOption({
      ...chartTheme,
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(26,26,36,0.95)', borderColor: 'rgba(255,255,255,0.1)', textStyle: { color: '#fff' } },
      grid: { top: 20, left: 50, right: 20, bottom: 30 },
      xAxis: { type: 'category', data: ['待处理', '已确认', '误报'], axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } }, axisLabel: { color: 'rgba(255,255,255,0.5)' } },
      yAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }, axisLabel: { color: 'rgba(255,255,255,0.5)' } },
      series: [{
        type: 'bar',
        barWidth: '50%',
        data: [
          { value: stats.by_status?.pending || 0, itemStyle: { color: '#eab308', borderRadius: [8, 8, 0, 0] } },
          { value: stats.by_status?.confirmed || 0, itemStyle: { color: '#10b981', borderRadius: [8, 8, 0, 0] } },
          { value: stats.by_status?.false_alarm || 0, itemStyle: { color: '#6b7280', borderRadius: [8, 8, 0, 0] } }
        ]
      }]
    })
  }
}

const handleResize = () => {
  typeChart?.resize()
  riskChart?.resize()
  statusChart?.resize()
}

onMounted(async () => {
  await loadStats()
  await loadEvents()
  nextTick(() => {
    initCharts()
    window.addEventListener('resize', handleResize)
  })
})
</script>

<style scoped>
/* ============================================
   事件看板页面 - 温暖科技感设计
   ============================================ */

.dashboard-page {
  width: 100%;
  min-height: 100%;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 24px;
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
  gap: 16px;
  transition: all var(--transition-base);
}

.stat-card:hover {
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}

.stat-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  flex-shrink: 0;
}

.stat-icon svg {
  width: 28px;
  height: 28px;
}

.stat-icon.primary {
  background: rgba(249, 115, 22, 0.15);
  color: var(--primary-400);
}

.stat-icon.danger {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

.stat-icon.warning {
  background: rgba(234, 179, 8, 0.15);
  color: var(--warning-400);
}

.stat-icon.info {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.stat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
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
  margin-top: 4px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: var(--radius-full);
}

.stat-trend svg {
  width: 14px;
  height: 14px;
}

.stat-trend.up {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-400);
}

.stat-trend.down {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

/* 图表区域 */
.charts-section {
  margin-bottom: 24px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.chart-card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  font-weight: 600;
  color: var(--neutral-700);
  margin: 0;
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

.card-body {
  padding: 20px;
}

.chart-container {
  width: 100%;
  height: 250px;
}

/* 事件列表 */
.events-card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.filter-group {
  display: flex;
  gap: 12px;
}

.filter-select {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  color: var(--neutral-600);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-base);
}

.filter-select:hover {
  border-color: rgba(255, 255, 255, 0.2);
}

.filter-select:focus {
  outline: none;
  border-color: var(--primary-500);
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 14px 20px;
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

.type-badge {
  display: inline-flex;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
}

.type-badge.type-fall {
  background: rgba(249, 115, 22, 0.15);
  color: var(--primary-400);
}

.type-badge.type-stillness {
  background: rgba(234, 179, 8, 0.15);
  color: var(--warning-400);
}

.type-badge.type-night {
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

.action-btns {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 14px;
  border-radius: var(--radius-md);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
  border: none;
}

.action-btn.primary {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  color: white;
}

.action-btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.3);
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--neutral-500);
}

.action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--neutral-700);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: var(--neutral-400);
}

.empty-state svg {
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

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: rgba(26, 26, 36, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-xl);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--neutral-800);
  margin: 0;
}

.modal-close {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: var(--radius-md);
  color: var(--neutral-400);
  cursor: pointer;
  transition: all var(--transition-base);
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--neutral-700);
}

.modal-close svg {
  width: 18px;
  height: 18px;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item.full-width {
  grid-column: span 2;
}

.detail-label {
  font-size: 12px;
  color: var(--neutral-400);
}

.detail-value {
  font-size: 14px;
  color: var(--neutral-700);
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-secondary {
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  color: var(--neutral-600);
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* 响应式 */
@media (max-width: 1400px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .filter-group {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .detail-item.full-width {
    grid-column: span 1;
  }
}
</style>
