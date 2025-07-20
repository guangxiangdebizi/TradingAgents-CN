<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()

// 响应式数据
const collapsed = ref(false)
const userName = ref('用户')

// 菜单项
const menuItems = [
  { path: '/', titleKey: 'nav.dashboard', icon: 'Monitor' },
  { path: '/analysis', titleKey: 'nav.analysis', icon: 'TrendCharts' },
  { path: '/config', titleKey: 'nav.config', icon: 'Setting' },
  { path: '/cache', titleKey: 'nav.cache', icon: 'FolderOpened' },
  { path: '/tokens', titleKey: 'nav.tokens', icon: 'Coin' },
  { path: '/history', titleKey: 'nav.history', icon: 'Document' },
  { path: '/status', titleKey: 'nav.status', icon: 'Tools' },
  { path: '/about', titleKey: 'nav.about', icon: 'InfoFilled' }
]

// 当前语言
const currentLanguage = computed(() => locale.value)

// 获取当前页面标题
const getCurrentPageTitle = () => {
  const currentItem = menuItems.find(item => item.path === route.path)
  return currentItem ? t(currentItem.titleKey) : t('nav.dashboard')
}

// 切换语言
const changeLanguage = (lang: string) => {
  locale.value = lang
  ElMessage.success(lang === 'zh' ? '已切换到中文' : 'Switched to English')
}

// 测试方法
const testConnection = () => {
  ElMessage.success(t('common.testConnection') + ' - ' + t('common.success'))
}

// 显示帮助
const showHelp = () => {
  router.push('/about')
}
</script>

<template>
  <div id="app" class="app-container">
    <!-- 顶部横幅 -->
    <div class="top-banner">
      <div class="banner-content">
        <div class="banner-left">
          <div class="banner-icon">🚀</div>
          <div class="banner-text">
            <h1>TradingAgents-CN 股票分析平台</h1>
            <p>基于多智能体大语言模型的中文金融交易决策框架</p>
          </div>
        </div>

        <div class="banner-right">
          <!-- 用户信息 -->
          <div class="user-info-banner">
            <el-avatar :size="28" background-color="rgba(255, 255, 255, 0.2)">
              {{ userName.charAt(0) }}
            </el-avatar>
            <span class="user-name">{{ userName }}</span>
          </div>

          <!-- 语言切换 -->
          <el-dropdown @command="changeLanguage" class="language-selector-banner">
            <el-button class="banner-btn">
              <el-icon><Operation /></el-icon>
              {{ currentLanguage === 'zh' ? '中文' : 'English' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="zh">中文</el-dropdown-item>
                <el-dropdown-item command="en">English</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <!-- 帮助指南 -->
          <el-button class="banner-btn" @click="showHelp">
            <el-icon><QuestionFilled /></el-icon>
            帮助指南
          </el-button>
        </div>
      </div>
    </div>

    <el-container class="layout-container">
      <!-- 侧边栏 -->
      <el-aside :width="collapsed ? '64px' : '240px'" class="app-sidebar">
        <!-- 侧边栏头部 -->
        <div class="sidebar-header">
          <div class="logo-container">
            <div class="logo-icon">📊</div>
            <h3 v-if="!collapsed" class="app-title">功能导航</h3>
          </div>
        </div>



        <!-- 导航菜单 -->
        <el-menu
          router
          :collapse="collapsed"
          :default-active="$route.path"
          class="sidebar-menu"
          background-color="transparent"
          text-color="#8a8e99"
          active-text-color="#409eff"
        >
          <el-menu-item
            v-for="item in menuItems"
            :key="item.path"
            :index="item.path"
            class="menu-item"
          >
            <el-icon><component :is="item.icon" /></el-icon>
            <template #title>{{ $t(item.titleKey) }}</template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主要内容区域 -->
      <el-container>
        <!-- 顶部导航栏 -->
        <el-header class="app-header">
          <div class="header-left">
            <el-button
              @click="collapsed = !collapsed"
              class="collapse-btn"
            >
              <el-icon><Expand v-if="collapsed" /><Fold v-else /></el-icon>
            </el-button>

            <div class="breadcrumb">
              <span class="current-page">{{ getCurrentPageTitle() }}</span>
            </div>
          </div>

          <div class="header-right">
            <el-button type="primary" @click="testConnection">
              <el-icon><Connection /></el-icon>
              {{ $t('common.testConnection') }}
            </el-button>
          </div>
        </el-header>

        <!-- 主要内容 -->
        <el-main class="app-main">
          <RouterView />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.app-container {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  margin: 0;
  padding: 0;
  background: #f5f7fa;
}

/* 顶部横幅 */
.top-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  padding: 16px 24px;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
}

.banner-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}

.banner-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.banner-icon {
  font-size: 32px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.banner-text h1 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 700;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.banner-text p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.banner-right {
  display: flex;
  align-items: center;
  gap: 16px;
  transform: translate(8px, 4px);
}

.user-info-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.banner-btn {
  color: white !important;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 6px;
  padding: 8px 12px;
  transition: all 0.3s ease;
  background: transparent !important;
}

.banner-btn:hover {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
}

.language-selector-banner {
  color: white;
}



.layout-container {
  height: calc(100vh - 72px);
  width: 100%;
}

.app-sidebar {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
  overflow: hidden;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0 20px;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 28px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.app-title {
  color: #fff;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}



.sidebar-menu {
  border: none;
  height: calc(100vh - 152px);
  overflow-y: auto;
  padding: 0 10px;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

.menu-item {
  margin: 4px 0;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.menu-item.is-active {
  background: rgba(255, 255, 255, 0.2) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.app-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 24px;
  height: 64px !important;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.collapse-btn {
  font-size: 18px;
  color: #606266 !important;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
  border: none !important;
  background: transparent !important;
}

.collapse-btn:hover {
  background: #f5f7fa !important;
}

.breadcrumb {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.current-page {
  color: #409eff;
}

.language-selector {
  margin-right: 8px;
}

.app-main {
  background: #f5f7fa;
  padding: 24px;
  overflow-y: auto;
  height: calc(100vh - 136px);
  min-height: calc(100vh - 136px);
}

/* Element Plus 菜单样式调整 */
:deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  margin: 4px 0;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
}

:deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
  color: #fff;
}

:deep(.el-menu-item.is-active) {
  background-color: rgba(255, 255, 255, 0.2) !important;
  color: #fff;
  font-weight: 600;
}

:deep(.el-menu-item .el-icon) {
  margin-right: 8px;
  font-size: 16px;
}

/* 下拉菜单样式 */
:deep(.el-dropdown-menu) {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.el-dropdown-menu__item) {
  padding: 8px 16px;
  transition: all 0.3s ease;
}

:deep(.el-dropdown-menu__item:hover) {
  background: #f5f7fa;
  color: #409eff;
}
</style>
