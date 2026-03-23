<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
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
        <el-card class="stat-card today">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">今日事件</p>
              <p class="stat-value">{{ eventsStore.statistics.today }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card pending">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">待处理</p>
              <p class="stat-value">{{ eventsStore.statistics.pending }}</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card accuracy">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">识别准确率</p>
              <p class="stat-value">{{ eventsStore.statistics.accuracy }}%</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 事件类型统计 -->
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

    <!-- 事件列表 -->
    <el-card class="events-card">
      <template #header>
        <div class="card-header">
          <span>异常事件列表</span>
          <div class="header-actions">
            <el-select v-model="filterType" placeholder="事件类型" clearable style="width: 150px; margin-right: 10px;">
              <el-option label="全部" value="" />
              <el-option label="跌倒检测" value="fall" />
              <el-option label="长时间静止" value="stillness" />
              <el-option label="夜间异常活动" value="night_activity" />
            </el-select>
            <el-select v-model="filterStatus" placeholder="处理状态" clearable style="width: 150px; margin-right: 10px;">
              <el-option label="全部" value="" />
              <el-option label="待处理" value="pending" />
              <el-option label="已处理" value="handled" />
            </el-select>
            <el-select v-model="filterRisk" placeholder="风险等级" clearable style="width: 150px;">
              <el-option label="全部" value="" />
              <el-option label="高风险" value="high" />
              <el-option label="中风险" value="medium" />
              <el-option label="低风险" value="low" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table :data="filteredEvents" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="typeName" label="事件类型" width="120" />
        <el-table-column label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.riskLevel)" size="small">
              {{ getRiskLabel(row.riskLevel) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="time" label="发生时间" width="180" />
        <el-table-column prop="location" label="位置" width="100" />
        <el-table-column prop="duration" label="持续时间" width="100">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="置信度" width="100">
          <template #default="{ row }">
            {{ (row.confidence * 100).toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'handled' ? 'success' : 'warning'" size="small">
              {{ row.status === 'handled' ? '已处理' : '待处理' }}
            </el-tag>
          </template>
        </el-table-column>
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
    </el-card>

    <!-- 事件详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="事件详情" width="600px">
      <div v-if="selectedEvent" class="event-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="事件ID">{{ selectedEvent.id }}</el-descriptions-item>
          <el-descriptions-item label="事件类型">{{ selectedEvent.typeName }}</el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag :type="getRiskTagType(selectedEvent.riskLevel)">
              {{ getRiskLabel(selectedEvent.riskLevel) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="置信度">{{ (selectedEvent.confidence * 100).toFixed(1) }}%</el-descriptions-item>
          <el-descriptions-item label="发生时间" :span="2">{{ selectedEvent.time }}</el-descriptions-item>
          <el-descriptions-item label="发生位置">{{ selectedEvent.location }}</el-descriptions-item>
          <el-descriptions-item label="持续时间">{{ formatDuration(selectedEvent.duration) }}</el-descriptions-item>
          <el-descriptions-item label="处理状态" :span="2">
            <el-tag :type="selectedEvent.status === 'handled' ? 'success' : 'warning'">
              {{ selectedEvent.status === 'handled' ? '已处理' : '待处理' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="事件描述" :span="2">{{ selectedEvent.description }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useEventsStore } from '@/stores/events'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { DataLine, Calendar, Warning, TrendCharts } from '@element-plus/icons-vue'

const eventsStore = useEventsStore()

const filterType = ref('')
const filterStatus = ref('')
const filterRisk = ref('')
const detailDialogVisible = ref(false)
const selectedEvent = ref(null)

const typeChartRef = ref(null)
const riskChartRef = ref(null)
const statusChartRef = ref(null)

let typeChart = null
let riskChart = null
let statusChart = null

const filteredEvents = computed(() => {
  return eventsStore.events.filter(event => {
    if (filterType.value && event.type !== filterType.value) return false
    if (filterStatus.value && event.status !== filterStatus.value) return false
    if (filterRisk.value && event.riskLevel !== filterRisk.value) return false
    return true
  })
})

const getRiskLabel = (level) => {
  const map = {
    high: '高风险',
    medium: '中风险',
    low: '低风险'
  }
  return map[level] || level
}

const getRiskTagType = (level) => {
  const map = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return map[level] || ''
}

const formatDuration = (seconds) => {
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分${seconds % 60}秒`
  return `${Math.floor(seconds / 3600)}时${Math.floor((seconds % 3600) / 60)}分`
}

const handleEvent = (event) => {
  ElMessageBox.confirm(`确定要处理该${event.typeName}事件吗？`, '确认处理', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    eventsStore.updateEventStatus(event.id, 'handled')
    ElMessage.success('事件已处理')
  }).catch(() => {})
}

const viewDetails = (event) => {
  selectedEvent.value = event
  detailDialogVisible.value = true
}

const initCharts = () => {
  // 事件类型分布图
  typeChart = echarts.init(typeChartRef.value)
  typeChart.setOption({
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '事件类型',
        type: 'pie',
        radius: '60%',
        data: [
          { value: eventsStore.statistics.fall, name: '跌倒检测' },
          { value: eventsStore.statistics.stillness, name: '长时间静止' },
          { value: eventsStore.statistics.nightActivity, name: '夜间异常活动' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  })

  // 风险等级分布图
  riskChart = echarts.init(riskChartRef.value)
  riskChart.setOption({
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        name: '风险等级',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 12, name: '高风险', itemStyle: { color: '#f56c6c' } },
          { value: 45, name: '中风险', itemStyle: { color: '#e6a23c' } },
          { value: 99, name: '低风险', itemStyle: { color: '#909399' } }
        ]
      }
    ]
  })

  // 处理状态分布图
  statusChart = echarts.init(statusChartRef.value)
  statusChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['已处理', '待处理']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '事件数量',
        type: 'bar',
        data: [
          { value: eventsStore.statistics.handled, itemStyle: { color: '#67c23a' } },
          { value: eventsStore.statistics.pending, itemStyle: { color: '#e6a23c' } }
        ],
        barWidth: '50%'
      }
    ]
  })
}

onMounted(() => {
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

.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.today .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card.pending .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card.accuracy .stat-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

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

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px 0;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

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

.event-detail {
  padding: 20px 0;
}
</style>