<template>
  <div class="platform-dashboard">
    <!-- 隐私声明 -->
    <div class="privacy-notice">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2L2 7l10 5 10-5-10-5z"/>
        <path d="M2 17l10 5 10-5"/>
        <path d="M2 12l10 5 10-5"/>
      </svg>
      <span>平台统计数据已采用差分隐私技术处理，数值与原始数据可能存在轻微差异，但不影响总体趋势判断。</span>
    </div>

    <!-- 组织信息 -->
    <section class="org-section" v-if="orgInfo">
      <div class="org-card">
        <div class="org-header">
          <h3>{{ orgInfo.name }}</h3>
        </div>
        <p class="org-desc" v-if="orgInfo.description">{{ orgInfo.description }}</p>
        <div class="org-meta">
          <span>社区组: {{ platformStore.communities.length }} 个</span>
          <span>覆盖用户: {{ stats.member_count || 0 }} 人</span>
        </div>
      </div>
    </section>

    <!-- 统计卡片 -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card" v-for="card in statsCards" :key="card.key">
          <div class="stat-icon" :class="card.type">
            <span>{{ card.icon }}</span>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ card.value }}</span>
            <span class="stat-label">{{ card.label }}</span>
          </div>
          <div class="stat-trend" v-if="card.trend" :class="card.trend > 0 ? 'up' : 'down'">
            <span>{{ Math.abs(card.trend) }}%</span>
          </div>
        </div>
      </div>
    </section>

    <!-- 图表 -->
    <section class="charts-section">
      <div class="charts-grid">
        <div class="chart-card">
          <div class="card-header">
            <h3 class="card-title">事件类型分布</h3>
          </div>
          <div class="card-body">
            <div ref="typeChartRef" class="chart-container"></div>
          </div>
        </div>
        <div class="chart-card">
          <div class="card-header">
            <h3 class="card-title">风险等级分布</h3>
          </div>
          <div class="card-body">
            <div ref="riskChartRef" class="chart-container"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- 每日趋势 -->
    <section class="trend-section">
      <div class="chart-card">
        <div class="card-header">
          <h3 class="card-title">每日事件趋势</h3>
          <div class="filter-group">
            <select v-model="trendDays" @change="loadDailyTrend" class="filter-select">
              <option :value="7">近 7 天</option>
              <option :value="14">近 14 天</option>
              <option :value="30">近 30 天</option>
            </select>
          </div>
        </div>
        <div class="card-body">
          <div ref="trendChartRef" class="chart-container"></div>
        </div>
      </div>
    </section>

    <!-- 社区组列表 -->
    <section class="communities-section">
      <div class="chart-card">
        <div class="card-header">
          <h3 class="card-title">社区组概览</h3>
        </div>
        <div class="card-body">
          <div class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>社区组名称</th>
                  <th>地址</th>
                  <th>覆盖用户</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in platformStore.communities" :key="c.id" class="table-row">
                  <td>{{ c.name }}</td>
                  <td>{{ c.address || '-' }}</td>
                  <td>{{ c.member_count }} 人</td>
                  <td>
                    <span class="status-badge" :class="c.status === 'active' ? 'confirmed' : 'pending'">
                      <span class="status-dot"></span>
                      {{ c.status === 'active' ? '运营中' : '已停用' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="platformStore.communities.length === 0" class="empty-state">
              <p>暂无社区组数据</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import {
  getMyProfile, getPlatformStats, getPlatformDailyTrend,
} from '@/api/platform'
import { usePlatformStore } from '@/stores/platform'
import * as echarts from 'echarts'

const platformStore = usePlatformStore()

const orgInfo = ref(null)
const stats = ref({ total: 0, by_type: {}, by_risk: {}, by_status: {}, trends: {}, member_count: 0 })
const trendDays = ref(7)

const typeChartRef = ref(null)
const riskChartRef = ref(null)
const trendChartRef = ref(null)

const typeLabels = { FALLEN: '跌倒检测', STILLNESS: '长时间静止', NIGHT_ABNORMAL: '夜间异常' }
const riskLabels = { HIGH: '高风险', MEDIUM: '中风险', LOW: '低风险' }
const riskColors = { HIGH: '#ef4444', MEDIUM: '#f59e0b', LOW: '#22c55e' }

const statsCards = computed(() => {
  const s = stats.value
  const t = s.trends || {}
  return [
    { key: 'total', label: '事件总数', value: s.display?.total ?? s.total, type: 'primary', icon: '📊', trend: t.total },
    { key: 'high', label: '高风险', value: s.display?.by_risk?.HIGH ?? s.by_risk?.HIGH ?? 0, type: 'danger', icon: '🔴' },
    { key: 'medium', label: '中风险', value: s.display?.by_risk?.MEDIUM ?? s.by_risk?.MEDIUM ?? 0, type: 'warning', icon: '🟡' },
    { key: 'members', label: '覆盖用户', value: s.member_count || 0, type: 'info', icon: '👥' },
  ]
})

async function loadOrg() {
  try {
    const res = await getMyProfile()
    orgInfo.value = {
      name: res.org_name || res.username,
      description: res.org_description || null,
    }
  } catch (e) { console.error(e) }
}

async function loadStats() {
  try {
    stats.value = await getPlatformStats(trendDays.value, platformStore.selectedGroupId)
    await nextTick()
    renderCharts()
  } catch (e) { console.error(e) }
}

async function loadDailyTrend() {
  try {
    const res = await getPlatformDailyTrend(trendDays.value, platformStore.selectedGroupId)
    renderTrendChart(res)
  } catch (e) { console.error(e) }
}

function renderCharts() {
  const s = stats.value
  if (typeChartRef.value) {
    const chart = echarts.init(typeChartRef.value)
    const typeData = Object.entries(s.by_type || {}).map(([k, v]) => ({
      name: typeLabels[k] || k, value: s.display?.by_type?.[k] ?? v
    }))
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie', radius: ['40%', '70%'],
        data: typeData.length ? typeData : [{ name: '暂无数据', value: 0 }],
        label: { color: '#aaa' },
        itemStyle: { borderColor: '#1a1a24', borderWidth: 2 },
      }]
    })
  }
  if (riskChartRef.value) {
    const chart = echarts.init(riskChartRef.value)
    const categories = Object.keys(riskLabels)
    const values = categories.map(k => s.display?.by_risk?.[k] ?? s.by_risk?.[k] ?? 0)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: categories.map(k => riskLabels[k]), axisLabel: { color: '#aaa' } },
      yAxis: { type: 'value', axisLabel: { color: '#aaa' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
      series: [{
        type: 'bar', data: categories.map((k, i) => ({ value: values[i], itemStyle: { color: riskColors[k] } })),
        barWidth: 40,
      }]
    })
  }
}

function renderTrendChart(data) {
  if (!trendChartRef.value || !data) return
  const chart = echarts.init(trendChartRef.value)
  const types = data.by_type || {}
  const series = Object.entries(types).map(([type, values]) => ({
    name: typeLabels[type] || type,
    type: 'line',
    smooth: true,
    data: values,
    lineStyle: { width: 2 },
  }))
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { textStyle: { color: '#aaa' }, top: 0 },
    grid: { top: 40, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: data.dates || [], axisLabel: { color: '#aaa' } },
    yAxis: { type: 'value', axisLabel: { color: '#aaa' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
    series,
  })
}

watch(() => platformStore.selectedGroupId, () => {
  loadStats()
  loadDailyTrend()
})

onMounted(() => {
  loadOrg()
  loadStats()
  loadDailyTrend()
})
</script>

<style scoped>
.platform-dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.privacy-notice {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  color: #93c5fd;
  font-size: 13px;
  margin-bottom: 24px;
}

.privacy-notice svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.org-section { margin-bottom: 24px; }

.org-card {
  padding: 20px 24px;
  background: rgba(26, 26, 36, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
}

.org-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.org-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: #f0f0f5;
  margin: 0;
}

.org-status {
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.org-status.active { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.org-status.suspended { background: rgba(239, 68, 68, 0.15); color: #f87171; }

.org-desc { color: #888; font-size: 14px; margin: 4px 0 12px; }

.org-meta {
  display: flex;
  gap: 24px;
  color: #aaa;
  font-size: 13px;
}

.stats-section { margin-bottom: 24px; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  padding: 20px;
  background: rgba(26, 26, 36, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-icon.primary { background: rgba(249, 115, 22, 0.15); }
.stat-icon.danger { background: rgba(239, 68, 68, 0.15); }
.stat-icon.warning { background: rgba(245, 158, 11, 0.15); }
.stat-icon.info { background: rgba(59, 130, 246, 0.15); }

.stat-content { display: flex; flex-direction: column; }
.stat-value { font-size: 24px; font-weight: 700; color: #f0f0f5; }
.stat-label { font-size: 13px; color: #888; }

.stat-trend {
  margin-left: auto;
  font-size: 13px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 8px;
}
.stat-trend.up { color: #f87171; background: rgba(239, 68, 68, 0.1); }
.stat-trend.down { color: #4ade80; background: rgba(34, 197, 94, 0.1); }

.charts-section { margin-bottom: 24px; }

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart-card {
  background: rgba(26, 26, 36, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  overflow: hidden;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #f0f0f5;
  margin: 0;
}

.card-body { padding: 16px; }

.chart-container { height: 280px; }

.filter-group { display: flex; gap: 8px; }

.filter-select {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #ccc;
  font-size: 13px;
  outline: none;
}

.trend-section { margin-bottom: 24px; }

.communities-section { margin-bottom: 24px; }

.table-wrapper { overflow-x: auto; }

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  font-size: 12px;
  color: #888;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.data-table td {
  padding: 12px 16px;
  font-size: 14px;
  color: #ddd;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 12px;
}

.status-badge.confirmed { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.status-badge.pending { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

@media (max-width: 768px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .charts-grid { grid-template-columns: 1fr; }
}
</style>
