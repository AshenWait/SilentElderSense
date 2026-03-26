<template>
  <div class="main-layout">
    <el-container>
      <el-aside width="240px" class="sidebar">
        <div class="logo">
          <el-icon class="logo-icon"><Monitor /></el-icon>
          <span class="logo-text">智慧养老监测</span>
        </div>

        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          router
          text-color="#fff"
          active-text-color="#fff"
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>事件看板</span>
          </el-menu-item>

          <el-menu-item index="/analysis">
            <el-icon><TrendCharts /></el-icon>
            <span>统计分析</span>
          </el-menu-item>

          <el-menu-item index="/monitor">
            <el-icon><VideoCamera /></el-icon>
            <span>实时监控</span>
          </el-menu-item>

          <el-menu-item index="/video-detect">
            <el-icon><VideoPlay /></el-icon>
            <span>视频检测</span>
          </el-menu-item>

          <el-menu-item v-if="authStore.isAdmin" index="/system">
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </el-menu-item>

          <el-menu-item index="/visualization">
            <el-icon><DataBoard /></el-icon>
            <span>可视化大屏</span>
          </el-menu-item>
        </el-menu>

        <div class="sidebar-footer">
          <div class="user-info">
            <el-avatar :size="40" :icon="UserFilled" />
            <div class="user-details">
              <p class="user-name">{{ authStore.user?.name }}</p>
              <p class="user-role">{{ getRoleName(authStore.user?.role) }}</p>
            </div>
          </div>
          <el-button type="danger" plain @click="handleLogout" size="small">
            退出登录
          </el-button>
        </div>
      </el-aside>

      <el-container>
        <el-header class="header">
          <div class="header-left">
            <h2 class="page-title">{{ pageTitle }}</h2>
          </div>

          <div class="header-right">
            <el-badge :value="pendingEvents" class="badge-item" type="danger">
              <el-button :icon="Bell" circle />
            </el-badge>
            <span class="current-time">{{ currentTime }}</span>
          </div>
        </el-header>

        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useEventsStore } from '@/stores/events'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  Monitor, DataAnalysis, TrendCharts, VideoCamera,
  Setting, DataBoard, UserFilled, Bell, VideoPlay
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const eventsStore = useEventsStore()

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => route.meta.title || '事件看板')
const pendingEvents = computed(() => eventsStore.statistics.pending)

const currentTime = ref('')
let timeInterval = null

const updateTime = () => {
  currentTime.value = new Date().toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getRoleName = (role) => {
  const roleMap = {
    admin: '系统管理员',
    family: '家属用户',
    monitor: '监护人'
  }
  return roleMap[role] || '访客'
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }).catch(() => {})
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.main-layout {
  width: 100%;
  height: 100vh;
}

.el-container {
  height: 100%;
}

.sidebar {
  background: linear-gradient(180deg, #1a237e 0%, #0d47a1 100%);
  display: flex;
  flex-direction: column;
  border-right: none;
}

.logo {
  height: 70px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  font-size: 32px;
  color: #fff;
  margin-right: 12px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
  padding-top: 20px;
}

.sidebar-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  margin: 5px 12px;
  border-radius: 8px;
  transition: all 0.3s;
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.sidebar-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.sidebar-menu .el-menu-item .el-icon {
  margin-right: 10px;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.user-details {
  margin-left: 12px;
  flex: 1;
}

.user-name {
  font-size: 14px;
  color: #fff;
  margin: 0;
  font-weight: 500;
}

.user-role {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin: 4px 0 0 0;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.badge-item {
  margin-right: 10px;
}

.current-time {
  font-size: 14px;
  color: #666;
}

.main-content {
  background: #f5f7fa;
  padding: 24px;
  overflow-y: auto;
}
</style>