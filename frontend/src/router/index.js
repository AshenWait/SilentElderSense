import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/dashboard',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '事件看板' }
      },
      {
        path: 'analysis',
        name: 'Analysis',
        component: () => import('@/views/Analysis.vue'),
        meta: { title: '统计分析' }
      },
      {
        path: 'monitor',
        name: 'Monitor',
        component: () => import('@/views/Monitor.vue'),
        meta: { title: '实时监控' }
      },
      {
        path: 'video-detect',
        name: 'VideoDetect',
        component: () => import('@/views/VideoDetect.vue'),
        meta: { title: '视频检测' }
      },
      {
        path: 'system',
        name: 'System',
        component: () => import('@/views/System.vue'),
        meta: { title: '系统设置' }
      }
    ]
  },
  {
    path: '/visualization',
    name: 'Visualization',
    component: () => import('@/views/Visualization.vue'),
    meta: { requiresAuth: true, title: '可视化大屏' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  // 使用 isAuthenticated（已同时检查 token 和 user）
  const isAuthenticated = authStore.isAuthenticated

  if (to.meta.requiresAuth && !isAuthenticated) {
    // 未登录，跳转到登录页
    next('/login')
  } else if (to.meta.role === 'admin' && !authStore.isAdmin) {
    // 权限不足，返回上一页或跳转到首页
    next(from.path || '/dashboard')
  } else {
    next()
  }
})

export default router