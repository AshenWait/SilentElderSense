<template>
  <div class="analysis">
    <!-- 时间选择器 -->
    <el-card class="filter-card">
      <div class="filter-content">
        <el-radio-group v-model="timeRange" size="large">
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
        />
      </div>
    </el-card>

    <!-- 统计图表 -->
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
              <span>时段分布分析</span>
            </div>
          </template>
          <div ref="timeDistributionChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>位置分布统计</span>
            </div>
          </template>
          <div ref="locationChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>置信度分布</span>
            </div>
          </template>
          <div ref="confidenceChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>处理效率分析</span>
            </div>
          </template>
          <div ref="efficiencyChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细数据表格 -->
    <el-card class="data-card">
      <template #header>
        <div class="card-header">
          <span>详细统计数据</span>
          <el-button type="primary" :icon="Download" size="small">导出报告</el-button>
        </div>
      </template>

      <el-table :data="analysisData" stripe style="width: 100%">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="total" label="总事件数" width="100" />
        <el-table-column prop="fall" label="跌倒检测" width="100" />
        <el-table-column prop="stillness" label="长时间静止" width="120" />
        <el-table-column prop="nightActivity" label="夜间异常" width="120" />
        <el-table-column prop="avgConfidence" label="平均置信度" width="120">
          <template #default="{ row }">
            {{ (row.avgConfidence * 100).toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column prop="handledCount" label="已处理" width="100" />
        <el-table-column prop="avgResponseTime" label="平均响应时间(分钟)" width="150" />
        <el-table-column prop="falseAlarmRate" label="误报率" width="100">
          <template #default="{ row }">
            {{ (row.falseAlarmRate * 100).toFixed(1) }}%
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { Download } from '@element-plus/icons-vue'

const timeRange = ref('week')
const customDateRange = ref(null)

const trendChartRef = ref(null)
const timeDistributionChartRef = ref(null)
const locationChartRef = ref(null)
const confidenceChartRef = ref(null)
const efficiencyChartRef = ref(null)

let trendChart = null
let timeDistributionChart = null
let locationChart = null
let confidenceChart = null
let efficiencyChart = null

// 模拟分析数据
const analysisData = ref([
  { date: '2026-03-16', total: 22, fall: 5, stillness: 10, nightActivity: 7, avgConfidence: 0.91, handledCount: 21, avgResponseTime: 8.5, falseAlarmRate: 0.05 },
  { date: '2026-03-17', total: 19, fall: 4, stillness: 8, nightActivity: 7, avgConfidence: 0.89, handledCount: 18, avgResponseTime: 7.2, falseAlarmRate: 0.06 },
  { date: '2026-03-18', total: 25, fall: 6, stillness: 11, nightActivity: 8, avgConfidence: 0.92, handledCount: 24, avgResponseTime: 6.8, falseAlarmRate: 0.04 },
  { date: '2026-03-19', total: 18, fall: 3, stillness: 9, nightActivity: 6, avgConfidence: 0.90, handledCount: 17, avgResponseTime: 9.1, falseAlarmRate: 0.07 },
  { date: '2026-03-20', total: 21, fall: 5, stillness: 10, nightActivity: 6, avgConfidence: 0.93, handledCount: 20, avgResponseTime: 7.5, falseAlarmRate: 0.05 },
  { date: '2026-03-21', total: 20, fall: 4, stillness: 9, nightActivity: 7, avgConfidence: 0.91, handledCount: 19, avgResponseTime: 8.2, falseAlarmRate: 0.06 },
  { date: '2026-03-22', total: 16, fall: 3, stillness: 7, nightActivity: 6, avgConfidence: 0.92, handledCount: 15, avgResponseTime: 7.8, falseAlarmRate: 0.05 }
])

const initTrendChart = () => {
  trendChart = echarts.init(trendChartRef.value)
  const dates = analysisData.value.map(item => item.date.slice(5))

  trendChart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['跌倒检测', '长时间静止', '夜间异常活动']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value',
      name: '事件数量'
    },
    series: [
      {
        name: '跌倒检测',
        type: 'line',
        smooth: true,
        data: analysisData.value.map(item => item.fall),
        itemStyle: { color: '#f56c6c' }
      },
      {
        name: '长时间静止',
        type: 'line',
        smooth: true,
        data: analysisData.value.map(item => item.stillness),
        itemStyle: { color: '#e6a23c' }
      },
      {
        name: '夜间异常活动',
        type: 'line',
        smooth: true,
        data: analysisData.value.map(item => item.nightActivity),
        itemStyle: { color: '#409eff' }
      }
    ]
  })
}

const initTimeDistributionChart = () => {
  timeDistributionChart = echarts.init(timeDistributionChartRef.value)

  timeDistributionChart.setOption({
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
      data: ['0-6时', '6-12时', '12-18时', '18-24时']
    },
    yAxis: {
      type: 'value',
      name: '事件数量'
    },
    series: [
      {
        name: '事件数量',
        type: 'bar',
        data: [
          { value: 28, itemStyle: { color: '#5470c6' } },
          { value: 45, itemStyle: { color: '#91cc75' } },
          { value: 52, itemStyle: { color: '#fac858' } },
          { value: 31, itemStyle: { color: '#ee6666' } }
        ],
        barWidth: '60%'
      }
    ]
  })
}

const initLocationChart = () => {
  locationChart = echarts.init(locationChartRef.value)

  locationChart.setOption({
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        name: '位置分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c} ({d}%)'
        },
        data: [
          { value: 45, name: '客厅', itemStyle: { color: '#5470c6' } },
          { value: 32, name: '卧室', itemStyle: { color: '#91cc75' } },
          { value: 28, name: '卫生间', itemStyle: { color: '#fac858' } },
          { value: 23, name: '厨房', itemStyle: { color: '#ee6666' } },
          { value: 18, name: '走廊', itemStyle: { color: '#73c0de' } },
          { value: 10, name: '书房', itemStyle: { color: '#3ba272' } }
        ]
      }
    ]
  })
}

const initConfidenceChart = () => {
  confidenceChart = echarts.init(confidenceChartRef.value)

  confidenceChart.setOption({
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
      data: ['0-0.6', '0.6-0.7', '0.7-0.8', '0.8-0.9', '0.9-1.0']
    },
    yAxis: {
      type: 'value',
      name: '事件数量'
    },
    series: [
      {
        name: '事件数量',
        type: 'bar',
        data: [3, 8, 25, 58, 62],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        barWidth: '50%'
      }
    ]
  })
}

const initEfficiencyChart = () => {
  efficiencyChart = echarts.init(efficiencyChartRef.value)

  efficiencyChart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['平均响应时间', '处理完成率']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: analysisData.value.map(item => item.date.slice(5))
    },
    yAxis: [
      {
        type: 'value',
        name: '响应时间(分钟)',
        position: 'left'
      },
      {
        type: 'value',
        name: '完成率(%)',
        position: 'right',
        max: 100
      }
    ],
    series: [
      {
        name: '平均响应时间',
        type: 'bar',
        data: analysisData.value.map(item => item.avgResponseTime),
        itemStyle: { color: '#f56c6c' }
      },
      {
        name: '处理完成率',
        type: 'line',
        yAxisIndex: 1,
        data: analysisData.value.map(item => (item.handledCount / item.total * 100).toFixed(1)),
        itemStyle: { color: '#67c23a' }
      }
    ]
  })
}

const initCharts = () => {
  initTrendChart()
  initTimeDistributionChart()
  initLocationChart()
  initConfidenceChart()
  initEfficiencyChart()
}

const handleResize = () => {
  trendChart?.resize()
  timeDistributionChart?.resize()
  locationChart?.resize()
  confidenceChart?.resize()
  efficiencyChart?.resize()
}

onMounted(() => {
  nextTick(() => {
    initCharts()
    window.addEventListener('resize', handleResize)
  })
})

watch(timeRange, () => {
  // 这里可以根据时间范围重新加载数据
  console.log('Time range changed:', timeRange.value)
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
</style>