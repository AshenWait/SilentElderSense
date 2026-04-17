<template>
  <div class="community-select-page">
    <div class="header-section">
      <h2 class="title">选择要查看的社区组</h2>
      <p class="subtitle">请选择您要管理或查看分析数据的目标社区，或选择全局视图（全部社区）。</p>
    </div>

    <div class="community-grid">
      <!-- 全部社区卡片 -->
      <div 
        class="community-card all-card" 
        :class="{ active: platformStore.selectedGroupId === null }"
        @click="selectGroup(null)"
      >
        <div class="card-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
             <path d="M2 17l10 5 10-5"/>
             <path d="M2 12l10 5 10-5"/>
          </svg>
        </div>
        <div class="card-content">
          <h3 class="card-title">全部社区 (全局视图)</h3>
          <p class="card-desc">查看平台下属所有社区的综合统计数据与趋势分析。</p>
        </div>
      </div>

      <!-- 具体社区组 -->
      <div 
        v-for="c in platformStore.communities" 
        :key="c.id"
        class="community-card"
        :class="{ active: platformStore.selectedGroupId === c.id }"
        @click="selectGroup(c.id)"
      >
        <div class="card-icon">
           <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
        </div>
        <div class="card-content">
          <h3 class="card-title">{{ c.name }}</h3>
          <p class="card-desc">{{ c.address || '暂无详细地址' }}</p>
          <div class="card-meta">
            <span class="member-count">覆盖用户: {{ c.member_count }} 人</span>
            <span class="status-badge" :class="c.status === 'active' ? 'active' : 'inactive'">
              {{ c.status === 'active' ? '运营中' : '已停用' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePlatformStore } from '@/stores/platform'
import { ElMessage } from 'element-plus'

const router = useRouter()
const platformStore = usePlatformStore()

onMounted(async () => {
  if (platformStore.communities.length === 0) {
    await platformStore.fetchCommunities()
  }
})

const selectGroup = (id) => {
  platformStore.selectGroup(id)
  ElMessage.success('已切换目标社区')
}
</script>

<style scoped>
.community-select-page {
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 40px;
}

.header-section {
  margin-bottom: 32px;
}

.title {
  font-size: 24px;
  font-weight: 700;
  color: #f0f0f5;
  margin: 0 0 8px 0;
}

.subtitle {
  color: #aaa;
  margin: 0;
  font-size: 14px;
}

.community-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.community-card {
  background: rgba(26, 26, 36, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.community-card:hover {
  transform: translateY(-4px);
  border-color: rgba(249, 115, 22, 0.3);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.community-card.active {
  border-color: #f97316;
  background: rgba(249, 115, 22, 0.05);
}

.all-card {
  background: linear-gradient(135deg, rgba(26, 26, 36, 0.8) 0%, rgba(31, 41, 55, 0.8) 100%);
}

.all-card.active {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.1) 0%, rgba(26, 26, 36, 0.8) 100%);
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fb923c;
}

.active .card-icon {
  background: rgba(249, 115, 22, 0.15);
}

.card-icon svg {
  width: 24px;
  height: 24px;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #f0f0f5;
}

.card-desc {
  margin: 0;
  font-size: 13px;
  color: #888;
  line-height: 1.5;
  flex: 1;
}

.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.member-count {
  font-size: 13px;
  color: #aaa;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: rgba(34, 197, 94, 0.1);
  color: #4ade80;
}

.status-badge.inactive {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
}
</style>
