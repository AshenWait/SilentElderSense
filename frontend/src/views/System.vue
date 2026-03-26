<template>
  <div class="system-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-gradient"></div>
      <div class="bg-grid"></div>
    </div>

    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">系统设置</h1>
        <p class="page-subtitle">配置告警通知与系统参数</p>
      </div>
    </header>

    <!-- 标签页导航 -->
    <div class="tabs-wrapper">
      <div class="tabs-nav">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          :class="['tab-btn', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >
          <span class="tab-icon">
            <component :is="tab.icon" />
          </span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
        <div class="tab-indicator" :style="indicatorStyle"></div>
      </div>
    </div>

    <!-- 内容区域 -->
    <main class="page-content">
      <!-- 告警配置 -->
      <section v-show="activeTab === 'alert'" class="content-section">
        <div class="settings-grid">
          <!-- 紧急联系人 -->
          <div class="settings-card">
            <div class="card-header">
              <div class="header-icon contact">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              </div>
              <div class="header-text">
                <h3>紧急联系人</h3>
                <p>接收告警通知的紧急联系人信息</p>
              </div>
            </div>
            <div class="card-body">
              <div class="form-grid">
                <div class="form-group">
                  <label class="form-label">联系人姓名</label>
                  <input
                    v-model="alertConfig.emergency_contact"
                    type="text"
                    class="form-input"
                    placeholder="请输入联系人姓名"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">联系电话</label>
                  <input
                    v-model="alertConfig.emergency_phone"
                    type="tel"
                    class="form-input"
                    placeholder="请输入联系电话"
                  />
                </div>
                <div class="form-group full-width">
                  <label class="form-label">通知邮箱</label>
                  <input
                    v-model="alertConfig.email"
                    type="email"
                    class="form-input"
                    placeholder="请输入邮箱地址"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- 告警方式 -->
          <div class="settings-card">
            <div class="card-header">
              <div class="header-icon bell">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                  <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                </svg>
              </div>
              <div class="header-text">
                <h3>告警方式</h3>
                <p>配置不同风险等级的通知方式</p>
              </div>
            </div>
            <div class="card-body">
              <div class="alert-levels">
                <div class="alert-level high">
                  <div class="level-header">
                    <span class="level-badge">高风险</span>
                    <span class="level-desc">需要立即处理的紧急事件</span>
                  </div>
                  <div class="level-options">
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.high_alert_methods" value="sms" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">短信通知</span>
                    </label>
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.high_alert_methods" value="email" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">邮件通知</span>
                    </label>
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.high_alert_methods" value="app" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">APP推送</span>
                    </label>
                  </div>
                </div>

                <div class="alert-level medium">
                  <div class="level-header">
                    <span class="level-badge">中风险</span>
                    <span class="level-desc">需要关注的潜在问题</span>
                  </div>
                  <div class="level-options">
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.medium_alert_methods" value="sms" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">短信通知</span>
                    </label>
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.medium_alert_methods" value="email" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">邮件通知</span>
                    </label>
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.medium_alert_methods" value="app" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">APP推送</span>
                    </label>
                  </div>
                </div>

                <div class="alert-level low">
                  <div class="level-header">
                    <span class="level-badge">低风险</span>
                    <span class="level-desc">一般性提示信息</span>
                  </div>
                  <div class="level-options">
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.low_alert_methods" value="sms" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">短信通知</span>
                    </label>
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.low_alert_methods" value="email" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">邮件通知</span>
                    </label>
                    <label class="checkbox-item">
                      <input type="checkbox" v-model="alertConfig.low_alert_methods" value="app" />
                      <span class="checkbox-box"></span>
                      <span class="checkbox-label">APP推送</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 免打扰时段 -->
          <div class="settings-card">
            <div class="card-header">
              <div class="header-icon moon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                </svg>
              </div>
              <div class="header-text">
                <h3>免打扰时段</h3>
                <p>设置静默时段，减少打扰</p>
              </div>
            </div>
            <div class="card-body">
              <div class="quiet-hours">
                <div class="time-range">
                  <div class="time-input">
                    <label class="form-label">开始时间</label>
                    <input
                      v-model="quietHoursStart"
                      type="time"
                      class="form-input"
                    />
                  </div>
                  <span class="time-separator">至</span>
                  <div class="time-input">
                    <label class="form-label">结束时间</label>
                    <input
                      v-model="quietHoursEnd"
                      type="time"
                      class="form-input"
                    />
                  </div>
                </div>
                <div class="quiet-option">
                  <label class="toggle-item">
                    <input type="checkbox" v-model="alertConfig.bypass_quiet_hours" />
                    <span class="toggle-switch"></span>
                    <div class="toggle-text">
                      <span class="toggle-label">高风险免打扰</span>
                      <span class="toggle-desc">开启后，高风险事件在免打扰时段仍会通知</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 保存按钮 -->
        <div class="actions-bar">
          <button class="btn-secondary" @click="resetConfig">重置</button>
          <button class="btn-primary" :disabled="saving" @click="saveConfig">
            <svg v-if="saving" class="spinner" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.416" stroke-dashoffset="10"/>
            </svg>
            <span>{{ saving ? '保存中...' : '保存配置' }}</span>
          </button>
        </div>
      </section>

      <!-- 告警历史 -->
      <section v-show="activeTab === 'history'" class="content-section">
        <div class="table-card">
          <div class="card-header">
            <div class="header-text">
              <h3>告警历史记录</h3>
              <p>查看所有告警通知记录</p>
            </div>
            <button class="btn-refresh" @click="loadAlertHistory" :disabled="historyLoading">
              <svg :class="{ spinning: historyLoading }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 4v6h-6"/>
                <path d="M1 20v-6h6"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
              <span>刷新</span>
            </button>
          </div>
          <div class="card-body">
            <div class="table-wrapper">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>告警类型</th>
                    <th>风险等级</th>
                    <th>通知方式</th>
                    <th>状态</th>
                    <th>创建时间</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="alert in alertHistory" :key="alert.id" class="table-row">
                    <td class="cell-id">#{{ alert.id }}</td>
                    <td>
                      <span class="type-badge">{{ getEventTypeLabel(alert.event_type) }}</span>
                    </td>
                    <td>
                      <span class="risk-badge" :class="getRiskClass(alert.risk_level)">
                        {{ getRiskLabel(alert.risk_level) }}
                      </span>
                    </td>
                    <td class="cell-method">{{ alert.alert_method || '-' }}</td>
                    <td>
                      <span class="status-badge" :class="getStatusClass(alert.status)">
                        <span class="status-dot"></span>
                        {{ getStatusLabel(alert.status) }}
                      </span>
                    </td>
                    <td class="cell-time">{{ formatDateTime(alert.created_at) }}</td>
                    <td>
                      <div class="action-btns">
                        <button
                          v-if="alert.status !== 'acknowledged'"
                          class="action-btn confirm"
                          @click="acknowledgeAlert(alert.id)"
                        >
                          确认
                        </button>
                        <button
                          v-if="alert.status === 'failed'"
                          class="action-btn retry"
                          @click="resendAlert(alert.id)"
                        >
                          重发
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-if="alertHistory.length === 0" class="empty-table">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M9 12l2 2 4-4"/>
                  <circle cx="12" cy="12" r="10"/>
                </svg>
                <p>暂无告警记录</p>
              </div>
            </div>
            <div class="pagination">
              <div class="pagination-info">
                共 <strong>{{ historyTotal }}</strong> 条记录
              </div>
              <div class="pagination-controls">
                <button
                  class="page-btn"
                  :disabled="historyPage === 1"
                  @click="handleHistoryPageChange(historyPage - 1)"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M15 18l-6-6 6-6"/>
                  </svg>
                </button>
                <span class="page-info">{{ historyPage }} / {{ historyTotalPages }}</span>
                <button
                  class="page-btn"
                  :disabled="historyPage >= historyTotalPages"
                  @click="handleHistoryPageChange(historyPage + 1)"
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

      <!-- 告警统计 -->
      <section v-show="activeTab === 'stats'" class="content-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon total">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ alertStats.total }}</span>
              <span class="stat-label">总告警数</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon success">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ alertStats.sent_count }}</span>
              <span class="stat-label">已发送</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon danger">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
              </svg>
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ alertStats.failed_count }}</span>
              <span class="stat-label">发送失败</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon percent">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M16 8l-8 8"/>
                <circle cx="9" cy="9" r="1" fill="currentColor"/>
                <circle cx="15" cy="15" r="1" fill="currentColor"/>
              </svg>
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ successRate }}%</span>
              <span class="stat-label">成功率</span>
            </div>
          </div>
        </div>

        <!-- 图表区域 -->
        <div class="charts-row">
          <div class="chart-card">
            <div class="card-header">
              <h3>告警趋势</h3>
            </div>
            <div class="card-body">
              <div class="chart-placeholder">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
                <p>近7天告警趋势图</p>
              </div>
            </div>
          </div>
          <div class="chart-card">
            <div class="card-header">
              <h3>类型分布</h3>
            </div>
            <div class="card-body">
              <div class="chart-placeholder">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>
                  <path d="M22 12A10 10 0 0 0 12 2v10z"/>
                </svg>
                <p>告警类型分布图</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, h } from 'vue'
import {
  getAlertConfig,
  updateAlertConfig,
  getAlertHistory,
  acknowledgeAlert as ackAlert,
  resendAlert as resendAlertApi,
  getAlertStats
} from '@/api/alerts'
import { ElMessage } from 'element-plus'

// 标签页配置
const tabs = [
  {
    key: 'alert',
    label: '告警配置',
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9' }),
      h('path', { d: 'M13.73 21a2 2 0 0 1-3.46 0' })
    ])
  },
  {
    key: 'history',
    label: '告警历史',
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('circle', { cx: '12', cy: '12', r: '10' }),
      h('polyline', { points: '12 6 12 12 16 14' })
    ])
  },
  {
    key: 'stats',
    label: '告警统计',
    icon: h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('line', { x1: '18', y1: '20', x2: '18', y2: '10' }),
      h('line', { x1: '12', y1: '20', x2: '12', y2: '4' }),
      h('line', { x1: '6', y1: '20', x2: '6', y2: '14' })
    ])
  }
]

const activeTab = ref('alert')
const saving = ref(false)
const historyLoading = ref(false)

// 指示器样式
const indicatorStyle = computed(() => {
  const index = tabs.findIndex(t => t.key === activeTab.value)
  return {
    transform: `translateX(${index * 100}%)`
  }
})

// 告警配置
const alertConfig = ref({
  emergency_contact: '',
  emergency_phone: '',
  email: '',
  high_alert_methods: ['sms', 'email', 'app'],
  medium_alert_methods: ['email', 'app'],
  low_alert_methods: ['app'],
  quiet_hours_start: '22:00',
  quiet_hours_end: '07:00',
  bypass_quiet_hours: true
})

const quietHoursStart = ref('22:00')
const quietHoursEnd = ref('07:00')

// 告警历史
const alertHistory = ref([])
const historyPage = ref(1)
const historyTotal = ref(0)
const historyPageSize = 20

const historyTotalPages = computed(() => Math.ceil(historyTotal.value / historyPageSize) || 1)

// 告警统计
const alertStats = ref({
  total: 0,
  sent_count: 0,
  failed_count: 0
})

const successRate = computed(() => {
  if (alertStats.value.total === 0) return 0
  return ((alertStats.value.sent_count / alertStats.value.total) * 100).toFixed(1)
})

// 工具函数
const getEventTypeLabel = (type) => {
  const map = { FALL: '跌倒检测', STILLNESS: '长时间静止', NIGHT_ACTIVITY: '夜间异常' }
  return map[type] || type
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
  const map = { pending: '待发送', sent: '已发送', failed: '失败', acknowledged: '已确认' }
  return map[status] || status
}

const getStatusClass = (status) => {
  const map = { pending: 'status-pending', sent: 'status-sent', failed: 'status-failed', acknowledged: 'status-confirmed' }
  return map[status] || ''
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  const date = new Date(datetime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 加载配置
const loadConfig = async () => {
  try {
    const config = await getAlertConfig()
    if (config) {
      alertConfig.value = {
        ...alertConfig.value,
        ...config,
        high_alert_methods: config.high_alert_methods?.split(',') || ['sms', 'email', 'app'],
        medium_alert_methods: config.medium_alert_methods?.split(',') || ['email', 'app'],
        low_alert_methods: config.low_alert_methods?.split(',') || ['app']
      }
      quietHoursStart.value = config.quiet_hours_start || '22:00'
      quietHoursEnd.value = config.quiet_hours_end || '07:00'
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

// 保存配置
const saveConfig = async () => {
  saving.value = true
  try {
    await updateAlertConfig({
      ...alertConfig.value,
      quiet_hours_start: quietHoursStart.value || alertConfig.value.quiet_hours_start,
      quiet_hours_end: quietHoursEnd.value || alertConfig.value.quiet_hours_end
    })
    ElMessage({
      message: '配置保存成功',
      type: 'success'
    })
  } catch (error) {
    ElMessage({
      message: '保存失败: ' + error.message,
      type: 'error'
    })
  } finally {
    saving.value = false
  }
}

// 重置配置
const resetConfig = () => {
  loadConfig()
}

// 加载告警历史
const loadAlertHistory = async () => {
  historyLoading.value = true
  try {
    const response = await getAlertHistory({ page: historyPage.value, per_page: historyPageSize })
    alertHistory.value = response.alerts || []
    historyTotal.value = response.total || 0
  } catch (error) {
    console.error('加载告警历史失败:', error)
  } finally {
    historyLoading.value = false
  }
}

const handleHistoryPageChange = (page) => {
  historyPage.value = page
  loadAlertHistory()
}

// 确认告警
const acknowledgeAlert = async (alertId) => {
  try {
    await ackAlert(alertId)
    ElMessage({
      message: '告警已确认',
      type: 'success'
    })
    loadAlertHistory()
  } catch (error) {
    ElMessage({
      message: '确认失败',
      type: 'error'
    })
  }
}

// 重发告警
const resendAlert = async (alertId) => {
  try {
    await resendAlertApi(alertId)
    ElMessage({
      message: '告警已重发',
      type: 'success'
    })
    loadAlertHistory()
  } catch (error) {
    ElMessage({
      message: '重发失败',
      type: 'error'
    })
  }
}

// 加载统计
const loadStats = async () => {
  try {
    const stats = await getAlertStats({ days: 7 })
    alertStats.value = stats
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

onMounted(() => {
  loadConfig()
  loadAlertHistory()
  loadStats()
})
</script>

<style scoped>
/* ============================================
   系统设置页面 - 温暖科技感设计
   ============================================ */

.system-page {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0d0d12 100%);
  color: var(--neutral-700);
  position: relative;
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
  padding: 32px 40px 24px;
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

/* 标签页导航 */
.tabs-wrapper {
  position: relative;
  z-index: 1;
  padding: 0 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.tabs-nav {
  display: flex;
  position: relative;
  gap: 8px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 24px;
  background: transparent;
  border: none;
  color: var(--neutral-400);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  position: relative;
  transition: color var(--transition-base);
}

.tab-btn:hover {
  color: var(--neutral-600);
}

.tab-btn.active {
  color: var(--primary-400);
}

.tab-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-icon svg {
  width: 100%;
  height: 100%;
}

.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  width: calc(33.333% - 6px);
  height: 2px;
  background: linear-gradient(90deg, var(--primary-400), var(--primary-500));
  border-radius: 2px 2px 0 0;
  transition: transform var(--transition-base);
  margin-left: 8px;
}

/* 内容区域 */
.page-content {
  position: relative;
  z-index: 1;
  padding: 24px 40px 40px;
}

.content-section {
  animation: fadeIn 0.3s ease-out;
}

/* 设置卡片网格 */
.settings-grid {
  display: grid;
  gap: 24px;
}

.settings-card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.settings-card .card-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.header-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
  flex-shrink: 0;
}

.header-icon svg {
  width: 24px;
  height: 24px;
}

.header-icon.contact {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.header-icon.bell {
  background: rgba(249, 115, 22, 0.15);
  color: var(--primary-400);
}

.header-icon.moon {
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
}

.header-text h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--neutral-800);
  margin: 0 0 4px 0;
}

.header-text p {
  font-size: 14px;
  color: var(--neutral-400);
  margin: 0;
}

.settings-card .card-body {
  padding: 24px;
}

/* 表单 */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: span 2;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--neutral-500);
}

.form-input {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  color: var(--neutral-700);
  font-size: 14px;
  transition: all var(--transition-base);
}

.form-input:hover {
  border-color: rgba(255, 255, 255, 0.2);
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15);
}

.form-input::placeholder {
  color: var(--neutral-400);
}

/* 告警等级 */
.alert-levels {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.alert-level {
  padding: 20px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-lg);
  border-left: 3px solid;
}

.alert-level.high {
  border-left-color: var(--danger-400);
}

.alert-level.medium {
  border-left-color: var(--warning-400);
}

.alert-level.low {
  border-left-color: var(--info-400);
}

.level-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.level-badge {
  display: inline-flex;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
}

.alert-level.high .level-badge {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

.alert-level.medium .level-badge {
  background: rgba(234, 179, 8, 0.15);
  color: var(--warning-400);
}

.alert-level.low .level-badge {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.level-desc {
  font-size: 13px;
  color: var(--neutral-400);
}

.level-options {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

/* 复选框 */
.checkbox-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.checkbox-item input {
  display: none;
}

.checkbox-box {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-sm);
  position: relative;
  transition: all var(--transition-base);
}

.checkbox-item input:checked + .checkbox-box {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  border-color: var(--primary-500);
}

.checkbox-item input:checked + .checkbox-box::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 6px;
  width: 5px;
  height: 9px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-label {
  font-size: 14px;
  color: var(--neutral-600);
}

/* 免打扰 */
.quiet-hours {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.time-range {
  display: flex;
  align-items: flex-end;
  gap: 16px;
}

.time-input {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.time-separator {
  padding-bottom: 12px;
  color: var(--neutral-400);
  font-size: 14px;
}

.quiet-option {
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

/* 开关 */
.toggle-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  cursor: pointer;
}

.toggle-item input {
  display: none;
}

.toggle-switch {
  width: 48px;
  height: 26px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 13px;
  position: relative;
  flex-shrink: 0;
  transition: background var(--transition-base);
}

.toggle-switch::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform var(--transition-base);
}

.toggle-item input:checked + .toggle-switch {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
}

.toggle-item input:checked + .toggle-switch::after {
  transform: translateX(22px);
}

.toggle-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.toggle-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--neutral-700);
}

.toggle-desc {
  font-size: 12px;
  color: var(--neutral-400);
}

/* 操作栏 */
.actions-bar {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: var(--radius-lg);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
  border: none;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(249, 115, 22, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--neutral-600);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.spinner {
  width: 18px;
  height: 18px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 表格卡片 */
.table-card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.table-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.table-card .card-body {
  padding: 0;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  color: var(--neutral-600);
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-refresh svg {
  width: 16px;
  height: 16px;
}

.btn-refresh svg.spinning {
  animation: spin 1s linear infinite;
}

/* 表格 */
.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 16px 24px;
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
  padding: 16px 24px;
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
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
  color: var(--neutral-600);
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

.cell-method {
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

.status-badge.status-sent {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-400);
}

.status-badge.status-sent .status-dot {
  background: var(--success-400);
}

.status-badge.status-failed {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

.status-badge.status-failed .status-dot {
  background: var(--danger-400);
}

.status-badge.status-confirmed {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.status-badge.status-confirmed .status-dot {
  background: var(--info-400);
}

.cell-time {
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--neutral-500);
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

.action-btn.confirm {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-400);
}

.action-btn.confirm:hover {
  background: rgba(16, 185, 129, 0.25);
}

.action-btn.retry {
  background: rgba(234, 179, 8, 0.15);
  color: var(--warning-400);
}

.action-btn.retry:hover {
  background: rgba(234, 179, 8, 0.25);
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

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
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
  transform: translateY(-2px);
}

.stat-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-lg);
}

.stat-icon svg {
  width: 28px;
  height: 28px;
}

.stat-icon.total {
  background: rgba(249, 115, 22, 0.15);
  color: var(--primary-400);
}

.stat-icon.success {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success-400);
}

.stat-icon.danger {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger-400);
}

.stat-icon.percent {
  background: rgba(59, 130, 246, 0.15);
  color: var(--info-400);
}

.stat-content {
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

/* 图表区域 */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.chart-card {
  background: rgba(26, 26, 36, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.chart-card .card-header {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.chart-card .card-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--neutral-700);
  margin: 0;
}

.chart-card .card-body {
  padding: 24px;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--neutral-400);
  border: 2px dashed rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
}

.chart-placeholder svg {
  width: 48px;
  height: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .page-header,
  .tabs-wrapper,
  .page-content {
    padding-left: 24px;
    padding-right: 24px;
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-group.full-width {
    grid-column: span 1;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .level-options {
    flex-direction: column;
    gap: 12px;
  }

  .time-range {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
