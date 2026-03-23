<template>
  <div class="system">
    <!-- 标签页 -->
    <el-tabs v-model="activeTab" class="system-tabs">
      <!-- 场景配置 -->
      <el-tab-pane label="场景配置" name="scene">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>场景配置</span>
              <el-button type="primary" :icon="Plus" @click="addScene">添加场景</el-button>
            </div>
          </template>

          <el-table :data="scenes" stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="场景名称" width="150" />
            <el-table-column prop="location" label="位置" width="120" />
            <el-table-column prop="camera" label="摄像头" width="120" />
            <el-table-column prop="type" label="场景类型" width="120">
              <template #default="{ row }">
                <el-tag size="small">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="area" label="监测区域" width="150" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-switch
                  v-model="row.enabled"
                  @change="handleSceneStatusChange(row)"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editScene(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteScene(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 监测时段设置 -->
      <el-tab-pane label="监测时段" name="time">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>监测时段设置</span>
              <el-button type="primary" :icon="Plus" @click="addTimePeriod">添加时段</el-button>
            </div>
          </template>

          <el-table :data="timePeriods" stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="时段名称" width="150" />
            <el-table-column prop="startTime" label="开始时间" width="120" />
            <el-table-column prop="endTime" label="结束时间" width="120" />
            <el-table-column prop="type" label="时段类型" width="120">
              <template #default="{ row }">
                <el-tag :type="row.type === 'night' ? 'warning' : 'primary'" size="small">
                  {{ row.type === 'night' ? '夜间' : '日间' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="sensitivity" label="灵敏度" width="120">
              <template #default="{ row }">
                <el-tag size="small">{{ row.sensitivity }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-switch
                  v-model="row.enabled"
                  @change="handleTimePeriodStatusChange(row)"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editTimePeriod(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteTimePeriod(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 告警规则 -->
      <el-tab-pane label="告警规则" name="alert">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>告警规则配置</span>
              <el-button type="primary" :icon="Plus" @click="addAlertRule">添加规则</el-button>
            </div>
          </template>

          <el-table :data="alertRules" stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="规则名称" width="180" />
            <el-table-column prop="eventType" label="事件类型" width="150">
              <template #default="{ row }">
                <el-tag size="small">{{ row.eventType }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="riskLevel" label="风险等级" width="120">
              <template #default="{ row }">
                <el-tag :type="getRiskTagType(row.riskLevel)" size="small">
                  {{ getRiskLabel(row.riskLevel) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="threshold" label="阈值" width="120" />
            <el-table-column label="通知方式" width="200">
              <template #default="{ row }">
                <el-tag
                  v-for="method in row.notificationMethods"
                  :key="method"
                  size="small"
                  style="margin-right: 5px;"
                >
                  {{ method }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-switch
                  v-model="row.enabled"
                  @change="handleAlertRuleStatusChange(row)"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editAlertRule(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteAlertRule(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 用户管理 -->
      <el-tab-pane label="用户管理" name="user">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <span>用户管理</span>
              <el-button type="primary" :icon="Plus" @click="addUser">添加用户</el-button>
            </div>
          </template>

          <el-table :data="users" stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="role" label="角色" width="120">
              <template #default="{ row }">
                <el-tag :type="getRoleTagType(row.role)" size="small">
                  {{ getRoleName(row.role) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="phone" label="电话" width="150" />
            <el-table-column prop="email" label="邮箱" width="200" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
                  {{ row.status === 'active' ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editUser(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteUser(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 系统设置 -->
      <el-tab-pane label="系统设置" name="settings">
        <el-card class="config-card">
          <template #header>
            <span>系统设置</span>
          </template>

          <el-form :model="systemSettings" label-width="150px" style="max-width: 800px;">
            <el-form-item label="系统名称">
              <el-input v-model="systemSettings.systemName" />
            </el-form-item>

            <el-form-item label="数据保留天数">
              <el-input-number v-model="systemSettings.dataRetentionDays" :min="7" :max="365" />
              <span style="margin-left: 10px;">天</span>
            </el-form-item>

            <el-form-item label="告警通知间隔">
              <el-input-number v-model="systemSettings.alertInterval" :min="1" :max="60" />
              <span style="margin-left: 10px;">分钟</span>
            </el-form-item>

            <el-form-item label="隐私保护模式">
              <el-switch v-model="systemSettings.privacyMode" />
            </el-form-item>

            <el-form-item label="自动删除原始视频">
              <el-switch v-model="systemSettings.autoDeleteVideo" />
            </el-form-item>

            <el-form-item label="日志级别">
              <el-select v-model="systemSettings.logLevel">
                <el-option label="DEBUG" value="debug" />
                <el-option label="INFO" value="info" />
                <el-option label="WARNING" value="warning" />
                <el-option label="ERROR" value="error" />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveSystemSettings">保存设置</el-button>
              <el-button @click="resetSystemSettings">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 场景编辑对话框 -->
    <el-dialog v-model="sceneDialogVisible" :title="sceneDialogTitle" width="600px">
      <el-form :model="sceneForm" label-width="100px">
        <el-form-item label="场景名称">
          <el-input v-model="sceneForm.name" />
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="sceneForm.location" />
        </el-form-item>
        <el-form-item label="摄像头">
          <el-select v-model="sceneForm.camera">
            <el-option label="客厅摄像头" value="客厅摄像头" />
            <el-option label="卧室摄像头" value="卧室摄像头" />
            <el-option label="卫生间摄像头" value="卫生间摄像头" />
            <el-option label="厨房摄像头" value="厨房摄像头" />
          </el-select>
        </el-form-item>
        <el-form-item label="场景类型">
          <el-select v-model="sceneForm.type">
            <el-option label="起居室" value="起居室" />
            <el-option label="卧室" value="卧室" />
            <el-option label="卫生间" value="卫生间" />
            <el-option label="厨房" value="厨房" />
            <el-option label="走廊" value="走廊" />
          </el-select>
        </el-form-item>
        <el-form-item label="监测区域">
          <el-input v-model="sceneForm.area" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="sceneDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveScene">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('scene')

// 场景配置
const scenes = ref([
  { id: 1, name: '客厅场景', location: '客厅', camera: '客厅摄像头', type: '起居室', area: '客厅全区域', enabled: true },
  { id: 2, name: '卧室场景', location: '卧室', camera: '卧室摄像头', type: '卧室', area: '卧室全区域', enabled: true },
  { id: 3, name: '卫生间场景', location: '卫生间', camera: '卫生间摄像头', type: '卫生间', area: '卫生间全区域', enabled: true },
  { id: 4, name: '厨房场景', location: '厨房', camera: '厨房摄像头', type: '厨房', area: '厨房全区域', enabled: false }
])

const sceneDialogVisible = ref(false)
const sceneDialogTitle = ref('添加场景')
const sceneForm = ref({
  name: '',
  location: '',
  camera: '',
  type: '',
  area: '',
  enabled: true
})

// 监测时段
const timePeriods = ref([
  { id: 1, name: '日间监测', startTime: '06:00', endTime: '22:00', type: 'day', sensitivity: '高', enabled: true },
  { id: 2, name: '夜间监测', startTime: '22:00', endTime: '06:00', type: 'night', sensitivity: '中', enabled: true },
  { id: 3, name: '午休时段', startTime: '12:00', endTime: '14:00', type: 'day', sensitivity: '低', enabled: false }
])

// 告警规则
const alertRules = ref([
  { id: 1, name: '跌倒告警规则', eventType: '跌倒检测', riskLevel: 'high', threshold: '置信度>0.8', notificationMethods: ['短信', 'APP推送'], enabled: true },
  { id: 2, name: '长时间静止告警', eventType: '长时间静止', riskLevel: 'medium', threshold: '静止>30分钟', notificationMethods: ['APP推送'], enabled: true },
  { id: 3, name: '夜间异常告警', eventType: '夜间异常活动', riskLevel: 'low', threshold: '活动>5次', notificationMethods: ['APP推送'], enabled: true }
])

// 用户管理
const users = ref([
  { id: 1, username: 'admin', name: '系统管理员', role: 'admin', phone: '13800138000', email: 'admin@example.com', status: 'active' },
  { id: 2, username: 'family', name: '家属用户', role: 'family', phone: '13800138001', email: 'family@example.com', status: 'active' },
  { id: 3, username: 'monitor', name: '监护人', role: 'monitor', phone: '13800138002', email: 'monitor@example.com', status: 'active' }
])

// 系统设置
const systemSettings = ref({
  systemName: '独居老人异常行为识别与应急响应系统',
  dataRetentionDays: 90,
  alertInterval: 10,
  privacyMode: true,
  autoDeleteVideo: true,
  logLevel: 'info'
})

const getRiskLabel = (level) => {
  const map = { high: '高风险', medium: '中风险', low: '低风险' }
  return map[level] || level
}

const getRiskTagType = (level) => {
  const map = { high: 'danger', medium: 'warning', low: 'info' }
  return map[level] || ''
}

const getRoleName = (role) => {
  const map = { admin: '管理员', family: '家属', monitor: '监护人' }
  return map[role] || role
}

const getRoleTagType = (role) => {
  const map = { admin: 'danger', family: 'primary', monitor: 'success' }
  return map[role] || ''
}

// 场景操作
const addScene = () => {
  sceneDialogTitle.value = '添加场景'
  sceneForm.value = { name: '', location: '', camera: '', type: '', area: '', enabled: true }
  sceneDialogVisible.value = true
}

const editScene = (row) => {
  sceneDialogTitle.value = '编辑场景'
  sceneForm.value = { ...row }
  sceneDialogVisible.value = true
}

const saveScene = () => {
  if (sceneForm.value.id) {
    const index = scenes.value.findIndex(s => s.id === sceneForm.value.id)
    if (index !== -1) {
      scenes.value[index] = { ...sceneForm.value }
    }
  } else {
    scenes.value.push({
      ...sceneForm.value,
      id: Date.now()
    })
  }
  sceneDialogVisible.value = false
  ElMessage.success('保存成功')
}

const deleteScene = (row) => {
  ElMessageBox.confirm('确定要删除该场景吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = scenes.value.findIndex(s => s.id === row.id)
    if (index !== -1) {
      scenes.value.splice(index, 1)
    }
    ElMessage.success('删除成功')
  }).catch(() => {})
}

const handleSceneStatusChange = (row) => {
  ElMessage.success(row.enabled ? '场景已启用' : '场景已禁用')
}

// 时段操作
const addTimePeriod = () => {
  ElMessage.info('添加时段功能开发中')
}

const editTimePeriod = (row) => {
  ElMessage.info('编辑时段功能开发中')
}

const deleteTimePeriod = (row) => {
  ElMessageBox.confirm('确定要删除该时段吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = timePeriods.value.findIndex(t => t.id === row.id)
    if (index !== -1) {
      timePeriods.value.splice(index, 1)
    }
    ElMessage.success('删除成功')
  }).catch(() => {})
}

const handleTimePeriodStatusChange = (row) => {
  ElMessage.success(row.enabled ? '时段已启用' : '时段已禁用')
}

// 告警规则操作
const addAlertRule = () => {
  ElMessage.info('添加告警规则功能开发中')
}

const editAlertRule = (row) => {
  ElMessage.info('编辑告警规则功能开发中')
}

const deleteAlertRule = (row) => {
  ElMessageBox.confirm('确定要删除该告警规则吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = alertRules.value.findIndex(a => a.id === row.id)
    if (index !== -1) {
      alertRules.value.splice(index, 1)
    }
    ElMessage.success('删除成功')
  }).catch(() => {})
}

const handleAlertRuleStatusChange = (row) => {
  ElMessage.success(row.enabled ? '规则已启用' : '规则已禁用')
}

// 用户操作
const addUser = () => {
  ElMessage.info('添加用户功能开发中')
}

const editUser = (row) => {
  ElMessage.info('编辑用户功能开发中')
}

const deleteUser = (row) => {
  ElMessageBox.confirm('确定要删除该用户吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = users.value.findIndex(u => u.id === row.id)
    if (index !== -1) {
      users.value.splice(index, 1)
    }
    ElMessage.success('删除成功')
  }).catch(() => {})
}

// 系统设置操作
const saveSystemSettings = () => {
  ElMessage.success('系统设置已保存')
}

const resetSystemSettings = () => {
  systemSettings.value = {
    systemName: '独居老人异常行为识别与应急响应系统',
    dataRetentionDays: 90,
    alertInterval: 10,
    privacyMode: true,
    autoDeleteVideo: true,
    logLevel: 'info'
  }
  ElMessage.info('系统设置已重置')
}
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
</style>