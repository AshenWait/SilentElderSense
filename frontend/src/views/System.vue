<template>
  <div class="system">
    <el-tabs v-model="activeTab" class="system-tabs">
      <!-- 告警配置 -->
      <el-tab-pane label="告警配置" name="alert">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>告警通知配置</span>
              <el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button>
            </div>
          </template>

          <el-form :model="alertConfig" label-width="150px" v-loading="loading">
            <el-form-item label="紧急联系人">
              <el-input v-model="alertConfig.emergency_contact" placeholder="请输入联系人姓名" />
            </el-form-item>

            <el-form-item label="紧急联系电话">
              <el-input v-model="alertConfig.emergency_phone" placeholder="请输入联系电话" />
            </el-form-item>

            <el-form-item label="通知邮箱">
              <el-input v-model="alertConfig.email" placeholder="请输入邮箱地址" />
            </el-form-item>

            <el-divider content-position="left">告警方式配置</el-divider>

            <el-form-item label="高风险告警">
              <el-checkbox-group v-model="alertConfig.high_alert_methods">
                <el-checkbox label="sms">短信</el-checkbox>
                <el-checkbox label="email">邮件</el-checkbox>
                <el-checkbox label="app">APP推送</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="中风险告警">
              <el-checkbox-group v-model="alertConfig.medium_alert_methods">
                <el-checkbox label="sms">短信</el-checkbox>
                <el-checkbox label="email">邮件</el-checkbox>
                <el-checkbox label="app">APP推送</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="低风险告警">
              <el-checkbox-group v-model="alertConfig.low_alert_methods">
                <el-checkbox label="sms">短信</el-checkbox>
                <el-checkbox label="email">邮件</el-checkbox>
                <el-checkbox label="app">APP推送</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-divider content-position="left">免打扰时段</el-divider>

            <el-form-item label="免打扰开始时间">
              <el-time-picker v-model="quietHoursStart" format="HH:mm" placeholder="选择时间" />
            </el-form-item>

            <el-form-item label="免打扰结束时间">
              <el-time-picker v-model="quietHoursEnd" format="HH:mm" placeholder="选择时间" />
            </el-form-item>

            <el-form-item label="高风险免打扰">
              <el-switch v-model="alertConfig.bypass_quiet_hours" />
              <span class="switch-tip">开启后，高风险事件在免打扰时段仍会通知</span>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 告警历史 -->
      <el-tab-pane label="告警历史" name="history">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>告警历史记录</span>
              <el-button type="primary" @click="loadAlertHistory" :icon="Refresh">刷新</el-button>
            </div>
          </template>

          <el-table :data="alertHistory" stripe v-loading="historyLoading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column label="告警类型" width="120">
              <template #default="{ row }">
                {{ getEventTypeLabel(row.event_type) }}
              </template>
            </el-table-column>
            <el-table-column label="风险等级" width="100">
              <template #default="{ row }">
                <el-tag :type="getRiskTagType(row.risk_level)" size="small">
                  {{ getRiskLabel(row.risk_level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="alert_method" label="通知方式" width="100" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusTagType(row.status)" size="small">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="row.status !== 'acknowledged'"
                  type="primary"
                  size="small"
                  @click="acknowledgeAlert(row.id)"
                >
                  确认
                </el-button>
                <el-button
                  v-if="row.status === 'failed'"
                  type="warning"
                  size="small"
                  @click="resendAlert(row.id)"
                >
                  重发
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="historyPage"
              :page-size="20"
              :total="historyTotal"
              layout="total, prev, pager, next"
              @current-change="handleHistoryPageChange"
            />
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 告警统计 -->
      <el-tab-pane label="告警统计" name="stats">
        <el-card class="config-card">
          <template #header>
            <span>告警统计（近7天）</span>
          </template>

          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="总告警数" :value="alertStats.total" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="已发送" :value="alertStats.sent_count" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="发送失败" :value="alertStats.failed_count" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="成功率" :value="alertStats.total > 0 ? ((alertStats.sent_count / alertStats.total) * 100).toFixed(1) : 0" suffix="%" />
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  getAlertConfig,
  updateAlertConfig,
  getAlertHistory,
  acknowledgeAlert as ackAlert,
  resendAlert as resendAlertApi,
  getAlertStats
} from '@/api/alerts'

const activeTab = ref('alert')
const loading = ref(false)
const saving = ref(false)
const historyLoading = ref(false)

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

const quietHoursStart = ref(null)
const quietHoursEnd = ref(null)

const alertHistory = ref([])
const historyPage = ref(1)
const historyTotal = ref(0)

const alertStats = ref({
  total: 0,
  sent_count: 0,
  failed_count: 0,
  by_type: {},
  by_risk: {},
  by_status: {}
})

const getEventTypeLabel = (type) => {
  const map = { FALL: '跌倒检测', STILLNESS: '长时间静止', NIGHT_ACTIVITY: '夜间异常' }
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
  const map = { pending: '待发送', sent: '已发送', failed: '失败', acknowledged: '已确认' }
  return map[status] || status
}

const getStatusTagType = (status) => {
  const map = { pending: 'warning', sent: 'success', failed: 'danger', acknowledged: 'info' }
  return map[status] || ''
}

const loadConfig = async () => {
  loading.value = true
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
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  } finally {
    loading.value = false
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    await updateAlertConfig({
      ...alertConfig.value,
      quiet_hours_start: quietHoursStart.value ? formatTime(quietHoursStart.value) : alertConfig.value.quiet_hours_start,
      quiet_hours_end: quietHoursEnd.value ? formatTime(quietHoursEnd.value) : alertConfig.value.quiet_hours_end
    })
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

const formatTime = (date) => {
  if (!date) return ''
  const h = date.getHours().toString().padStart(2, '0')
  const m = date.getMinutes().toString().padStart(2, '0')
  return `${h}:${m}`
}

const loadAlertHistory = async () => {
  historyLoading.value = true
  try {
    const response = await getAlertHistory({ page: historyPage.value, per_page: 20 })
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

const acknowledgeAlert = async (alertId) => {
  try {
    await ackAlert(alertId)
    ElMessage.success('告警已确认')
    loadAlertHistory()
  } catch (error) {
    ElMessage.error('确认失败')
  }
}

const resendAlert = async (alertId) => {
  try {
    await resendAlertApi(alertId)
    ElMessage.success('告警已重发')
    loadAlertHistory()
  } catch (error) {
    ElMessage.error('重发失败')
  }
}

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
.system {
  width: 100%;
}

.system-tabs {
  border: none;
}

.config-card {
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

.switch-tip {
  margin-left: 10px;
  font-size: 12px;
  color: #999;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
