import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: {
      title: '仪表板',
      requireAuth: false
    }
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('../views/AnalysisView.vue'),
    meta: {
      title: '股票分析',
      requireAuth: false
    }
  },
  {
    path: '/config',
    name: 'Config',
    component: () => import('../views/ConfigView.vue'),
    meta: {
      title: '配置管理',
      requireAuth: false
    }
  },
  {
    path: '/cache',
    name: 'Cache',
    component: () => import('../views/CacheView.vue'),
    meta: {
      title: '缓存管理',
      requireAuth: false
    }
  },
  {
    path: '/tokens',
    name: 'Tokens',
    component: () => import('../views/TokensView.vue'),
    meta: {
      title: 'Token统计',
      requireAuth: false
    }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/HistoryView.vue'),
    meta: {
      title: '历史记录',
      requireAuth: false
    }
  },
  {
    path: '/status',
    name: 'Status',
    component: () => import('../views/StatusView.vue'),
    meta: {
      title: '系统状态',
      requireAuth: false
    }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/AboutView.vue'),
    meta: {
      title: '关于',
      requireAuth: false
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue'),
    meta: {
      title: '页面未找到'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - TradingAgents-CN`
  }
  next()
})

export default router
