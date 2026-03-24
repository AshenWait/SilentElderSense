<template>
  <div class="analysis">
    <el-card class="filter-card">
      <div class="filter-content">
        <el-radio-group v-model="timeRange" size="large" @change="handleTimeRangeChange">
          <el-radio-button label="today">今日</el-radio-button>
          <el-radio-button label="week">本周</el-radio-button>
          <el-radio-button label="month">本月</el-radio-button>
          <el-radio-button label="custom">自定义</el-radio-button>
        </el-radio-group>

        <el-date-picker
          v-if="timeRange === 'custom'"
          v-model="customDateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="margin-left: 20px;"
          @change="handleDateChange"
        />
      </div>
    </el-card>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>事件趋势分析</span>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>风险等级分布</span>
            </div>
          </template>
          <div ref="riskChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>事件类型分布</span>
            </div>
          </template>
          <div ref="typeChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>处理状态分布</span>
            </div>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>详细统计数据</span>
          <el-button type="primary" :icon="Download" size="small">导出报告</el-button>
        </div>
      </template>

      <el-table :data="eventsData" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="事件类型" width="120">
          <template #default="{ row }">
            {{ getTypeLabel(row.event_type) }}
          </template>
        </el-table-column>
        <el-table-column label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.risk_level)" size="small">
              {{ getRiskLabel(row.risk_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="发生时间" width="180" />
        <el-table-column prop="duration" label="持续时间" width="100">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" show-overflow-tooltip />
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { Download } from '@element-plus/icons-vue'
import { getEvents, getEventStats } from '@/api/events'

const timeRange = ref('week')
const customDateRange = ref(null)
const loading = ref(false)

const trendChartRef = ref(null)
const riskChartRef = ref(null)
const typeChartRef = ref(null)
const statusChartRef = ref(null)

let trendChart = null
let riskChart = null
let typeChart = null
let statusChart = null

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

const getTypeLabel = (type) => {
  const map = { FALL: '跌倒检测', STILLNESS: '长时间静止', NIGHT_ACTIVITY: '夜间异常活动' }
  return map[type] || type
}

const getRiskLabel = (level) => {
  const map = { HIGH: '高风险', MEDIUM: '中风险', LOW: '低风险' }
  return map[level] || level
}

const getRiskTagType = (level) => {
  const map = { HIGH: 'danger', MEDIUM: 'warning', LOW: 'info' }
  return map[level] || ''
}

const getStatusLabel = (status) => {
  const map = { pending: '待处理', confirmed: '已确认', false_alarm: '误报' }
  return map[status] || status
}

const getStatusTagType = (status) => {
  const map = { pending: 'warning', confirmed: 'success', false_alarm: 'info' }
  return map[status] || ''
}

const formatDuration = (seconds) => {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds.toFixed(1)}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分${(seconds % 60).toFixed(0)}秒`
  return `${Math.floor(seconds / 3600)}时${Math.floor((seconds % 3600) / 60)}分`
}

const getDaysByRange = () => {
  switch (timeRange.value) {
    case 'today': return 1
    case 'week': return 7
    case 'month': return 30
    default: return 7
  }
}

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

const updateCharts = () => {
  updateTrendChart()
  updateRiskChart()
  updateTypeChart()
  updateStatusChart()
}

const updateTrendChart = () => {
  if (!trendChart) return
  const s = stats.value
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['跌倒检测', '长时间静止', '夜间异常活动'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['统计周期'] },
    yAxis: { type: 'value', name: '事件数量' },
    series: [
      { name: '跌倒检测', type: 'bar', data: [s.by_type?.FALL || 0], itemStyle: { color: '#f56c6c' } },
      { name: '长时间静止', type: 'bar', data: [s.by_type?.STILLNESS || 0], itemStyle: { color: '#e6a23c' } },
      { name: '夜间异常活动', type: 'bar', data: [s.by_type?.NIGHT_ACTIVITY || 0], itemStyle: { color: '#409eff' } }
    ]
  })
}

const updateRiskChart = () => {
  if (!riskChart) return
  const s = stats.value
  riskChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      name: '风险等级',
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: s.by_risk?.HIGH || 0, name: '高风险', itemStyle: { color: '#f56c6c' } },
        { value: s.by_risk?.MEDIUM || 0, name: '中风险', itemStyle: { color: '#e6a23c' } },
        { value: s.by_risk?.LOW || 0, name: '低风险', itemStyle: { color: '#909399' } }
      ],
      label: { show: true, formatter: '{b}: {c} ({d}%)' }
    }]
  })
}

const updateTypeChart = () => {
  if (!typeChart) return
  const s = stats.value
  typeChart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      name: '事件类型',
      type: 'pie',
      radius: '60%',
      data: [
        { value: s.by_type?.FALL || 0, name: '跌倒检测', itemStyle: { color: '#f56c6c' } },
        { value: s.by_type?.STILLNESS || 0, name: '长时间静止', itemStyle: { color: '#e6a23c' } },
        { value: s.by_type?.NIGHT_ACTIVITY || 0, name: '夜间异常活动', itemStyle: { color: '#409eff' } }
      ],
      label: { show: true, formatter: '{b}\n{c} ({d}%)' }
    }]
  })
}

const updateStatusChart = () => {
  if (!statusChart) return
  const s = stats.value
  statusChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['待处理', '已确认', '误报'] },
    yAxis: { type: 'value' },
    series: [{
      name: '事件数量',
      type: 'bar',
      data: [
        { value: s.by_status?.pending || 0, itemStyle: { color: '#e6a23c' } },
        { value: s.by_status?.confirmed || 0, itemStyle: { color: '#67c23a' } },
        { value: s.by_status?.false_alarm || 0, itemStyle: { color: '#909399' } }
      ],
      barWidth: '50%'
    }]
  })
}

const initCharts = () => {
  trendChart = echarts.init(trendChartRef.value)
  riskChart = echarts.init(riskChartRef.value)
  typeChart = echarts.init(typeChartRef.value)
  statusChart = echarts.init(statusChartRef.value)
  updateCharts()
}

const handleResize = () => {
  trendChart?.resize()
  riskChart?.resize()
  typeChart?.resize()
  statusChart?.resize()
}

const handleTimeRangeChange = () => {
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

onMounted(async () => {
  await loadData()
  nextTick(() => {
    initCharts()
    window.addEventListener('resize', handleResize)
  })
})

watch(timeRange, () => {
  loadData()
})
</script>

<style scoped>
.analysis {
  width: 100%;
}

.filter-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.filter-content {
  display: flex;
  align-items: center;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.chart-container {
  width: 100%;
  height: 320px;
}

.data-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
