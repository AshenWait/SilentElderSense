<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card total">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><DataLine /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">总事件数</p>
              <p class="stat-value">{{ eventsStore.statistics.total }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card fall">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">跌倒检测</p>
              <p class="stat-value">{{ eventsStore.statsFormatted.fall }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card stillness">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Timer /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">长时间静止</p>
              <p class="stat-value">{{ eventsStore.statsFormatted.stillness }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card pending">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">待处理</p>
              <p class="stat-value">{{ eventsStore.statsFormatted.pending }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card class="type-card">
          <template #header>
            <div class="card-header">
              <span>事件类型分布</span>
            </div>
          </template>
          <div ref="typeChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="type-card">
          <template #header>
            <div class="card-header">
              <span>风险等级分布</span>
            </div>
          </template>
          <div ref="riskChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="type-card">
          <template #header>
            <div class="card-header">
              <span>处理状态分布</span>
            </div>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="events-card">
      <template #header>
        <div class="card-header">
          <span>异常事件列表</span>
          <div class="header-actions">
            <el-select v-model="filterType" placeholder="事件类型" clearable style="width: 150px; margin-right: 10px;" @change="loadEvents">
              <el-option label="全部" value="" />
              <el-option label="跌倒检测" value="FALL" />
              <el-option label="长时间静止" value="STILLNESS" />
              <el-option label="夜间异常活动" value="NIGHT_ACTIVITY" />
            </el-select>
            <el-select v-model="filterStatus" placeholder="处理状态" clearable style="width: 150px; margin-right: 10px;" @change="loadEvents">
              <el-option label="全部" value="" />
              <el-option label="待处理" value="pending" />
              <el-option label="已确认" value="confirmed" />
              <el-option label="误报" value="false_alarm" />
            </el-select>
            <el-select v-model="filterRisk" placeholder="风险等级" clearable style="width: 150px;" @change="loadEvents">
              <el-option label="全部" value="" />
              <el-option label="高风险" value="HIGH" />
              <el-option label="中风险" value="MEDIUM" />
              <el-option label="低风险" value="LOW" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table :data="eventsStore.events" stripe style="width: 100%" v-loading="eventsStore.loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="typeName" label="事件类型" width="120" />
        <el-table-column label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.riskLevel)" size="small">
              {{ getRiskLabel(row.riskLevel) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="发生时间" width="180" />
        <el-table-column prop="duration" label="持续时间" width="100">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="frame_count" label="帧数" width="80" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              type="primary"
              size="small"
              @click="handleEvent(row)"
            >
              处理
            </el-button>
            <el-button
              type="info"
              size="small"
              @click="viewDetails(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="20"
          :total="eventsStore.pagination.total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="detailDialogVisible" title="事件详情" width="600px">
      <div v-if="selectedEvent" class="event-detail" v-loading="detailLoading">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="事件ID">{{ selectedEvent.id }}</el-descriptions-item>
          <el-descriptions-item label="事件类型">{{ selectedEvent.typeName }}</el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag :type="getRiskTagType(selectedEvent.riskLevel)">
              {{ getRiskLabel(selectedEvent.riskLevel) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="持续时间">{{ formatDuration(selectedEvent.duration) }}</el-descriptions-item>
          <el-descriptions-item label="开始时间" :span="2">{{ selectedEvent.start_time }}</el-descriptions-item>
          <el-descriptions-item label="结束时间" :span="2">{{ selectedEvent.end_time }}</el-descriptions-item>
          <el-descriptions-item label="处理状态" :span="2">
            <el-tag :type="getStatusTagType(selectedEvent.status)">
              {{ getStatusLabel(selectedEvent.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ selectedEvent.notes || '无' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useEventsStore } from '@/stores/events'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { DataLine, Warning, Timer, Bell } from '@element-plus/icons-vue'
import { getEventDetail } from '@/api/events'

const eventsStore = useEventsStore()

const filterType = ref('')
const filterStatus = ref('')
const filterRisk = ref('')
const currentPage = ref(1)
const detailDialogVisible = ref(false)
const selectedEvent = ref(null)
const detailLoading = ref(false)

const typeChartRef = ref(null)
const riskChartRef = ref(null)
const statusChartRef = ref(null)

let typeChart = null
let riskChart = null
let statusChart = null

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

const loadEvents = async () => {
  const params = {
    page: currentPage.value,
    per_page: 20
  }
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
    inputOptions: {
      confirmed: '已确认',
      false_alarm: '误报'
    }
  }).then(async ({ value }) => {
    await eventsStore.updateEventStatus(event.id, { status: value })
    ElMessage.success('事件已处理')
    loadEvents()
    loadStats()
  }).catch(() => {})
}

const viewDetails = async (event) => {
  detailLoading.value = true
  detailDialogVisible.value = true
  
  try {
    const detail = await eventsStore.fetchEventDetail(event.id)
    selectedEvent.value = detail
  } catch (error) {
    ElMessage.error('获取事件详情失败')
    selectedEvent.value = event
  } finally {
    detailLoading.value = false
  }
}

const updateCharts = () => {
  const stats = eventsStore.statistics

  if (typeChart) {
    typeChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', left: 'left' },
      series: [{
        name: '事件类型',
        type: 'pie',
        radius: '60%',
        data: [
          { value: stats.by_type?.FALL || 0, name: '跌倒检测' },
          { value: stats.by_type?.STILLNESS || 0, name: '长时间静止' },
          { value: stats.by_type?.NIGHT_ACTIVITY || 0, name: '夜间异常活动' }
        ]
      }]
    })
  }

  if (riskChart) {
    riskChart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        name: '风险等级',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false, position: 'center' },
        emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold' } },
        labelLine: { show: false },
        data: [
          { value: stats.by_risk?.HIGH || 0, name: '高风险', itemStyle: { color: '#f56c6c' } },
          { value: stats.by_risk?.MEDIUM || 0, name: '中风险', itemStyle: { color: '#e6a23c' } },
          { value: stats.by_risk?.LOW || 0, name: '低风险', itemStyle: { color: '#909399' } }
        ]
      }]
    })
  }

  if (statusChart) {
    statusChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: ['待处理', '已确认', '误报'] },
      yAxis: { type: 'value' },
      series: [{
        name: '事件数量',
        type: 'bar',
        data: [
          { value: stats.by_status?.pending || 0, itemStyle: { color: '#e6a23c' } },
          { value: stats.by_status?.confirmed || 0, itemStyle: { color: '#67c23a' } },
          { value: stats.by_status?.false_alarm || 0, itemStyle: { color: '#909399' } }
        ],
        barWidth: '50%'
      }]
    })
  }
}

const initCharts = () => {
  typeChart = echarts.init(typeChartRef.value)
  riskChart = echarts.init(riskChartRef.value)
  statusChart = echarts.init(statusChartRef.value)
  updateCharts()
}

onMounted(async () => {
  await loadStats()
  await loadEvents()
  nextTick(() => {
    initCharts()
    window.addEventListener('resize', () => {
      typeChart?.resize()
      riskChart?.resize()
      statusChart?.resize()
    })
  })
})
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.stat-card.total .stat-icon { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-card.fall .stat-icon { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-card.stillness .stat-icon { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.stat-card.pending .stat-icon { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }

.stat-content {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}

.stat-icon .el-icon {
  font-size: 32px;
  color: #fff;
}

.stat-info { flex: 1; }
.stat-label { font-size: 14px; color: #666; margin: 0 0 8px 0; }
.stat-value { font-size: 28px; font-weight: 600; color: #333; margin: 0; }

.type-card {
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

.chart-container {
  width: 100%;
  height: 250px;
}

.events-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.header-actions {
  display: flex;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.event-detail {
  padding: 20px 0;
}
</style>
