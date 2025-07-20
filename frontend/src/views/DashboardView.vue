<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { t } = useI18n()

// 响应式数据
const userName = ref('用户')

const stats = ref([
  { key: 'totalAnalysis', value: '156', icon: 'TrendCharts', color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  { key: 'successRate', value: '98.5%', icon: 'CircleCheckFilled', color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { key: 'avgTime', value: '1.2s', icon: 'Clock', color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  { key: 'activeUsers', value: '24', icon: 'UserFilled', color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }
])

const quickActions = ref([
  {
    key: 'newAnalysis',
    icon: 'TrendCharts',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    desc: '开始新的股票分析',
    action: () => router.push('/analysis')
  },
  {
    key: 'viewReports',
    icon: 'Document',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    desc: '查看历史分析报告',
    action: () => ElMessage.info('功能开发中...')
  },
  {
    key: 'settings',
    icon: 'Setting',
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    desc: '配置系统参数',
    action: () => router.push('/settings')
  },
  {
    key: 'help',
    icon: 'InfoFilled',
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    desc: '查看帮助文档',
    action: () => router.push('/about')
  }
])

// 处理快速操作
const handleAction = (action: () => void) => {
  action()
}

onMounted(() => {
  // 模拟数据加载
  ElMessage.success(t('common.loading'))
})
</script>

<template>
  <div class="dashboard">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="banner-content">
        <div class="welcome-text">
          <h1 class="welcome-title">{{ $t('dashboard.welcome', { name: userName }) }}</h1>
          <p class="welcome-subtitle">{{ $t('dashboard.subtitle') }}</p>
          <div class="quick-tip">
            <el-icon><Star /></el-icon>
            <span>{{ $t('dashboard.quickActions') }}</span>
          </div>
        </div>
        <div class="banner-actions">
          <el-button type="primary" size="large" @click="$router.push('/analysis')">
            <el-icon><TrendCharts /></el-icon>
            {{ $t('dashboard.actions.newAnalysis') }}
          </el-button>
          <el-button size="large" @click="$router.push('/settings')">
            <el-icon><Setting /></el-icon>
            {{ $t('dashboard.actions.settings') }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="24">
        <el-col :span="6" v-for="stat in stats" :key="stat.key">
          <div class="stat-card">
            <div class="stat-icon" :style="{ background: stat.color }">
              <el-icon><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ $t(`dashboard.stats.${stat.key}`) }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 主要内容区域 -->
    <el-row :gutter="24" class="main-content">
      <!-- 快速操作 -->
      <el-col :span="12">
        <el-card class="content-card">
          <template #header>
            <div class="card-header">
              <el-icon><Operation /></el-icon>
              <span>{{ $t('dashboard.quickActions') }}</span>
            </div>
          </template>

          <div class="quick-actions">
            <div
              v-for="action in quickActions"
              :key="action.key"
              class="action-item"
              @click="handleAction(action.action)"
            >
              <div class="action-icon" :style="{ background: action.color }">
                <el-icon><component :is="action.icon" /></el-icon>
              </div>
              <div class="action-content">
                <div class="action-title">{{ $t(`dashboard.actions.${action.key}`) }}</div>
                <div class="action-desc">{{ action.desc }}</div>
              </div>
              <el-icon class="action-arrow"><Right /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 系统状态 -->
      <el-col :span="12">
        <el-card class="content-card">
          <template #header>
            <div class="card-header">
              <el-icon><Monitor /></el-icon>
              <span>{{ $t('dashboard.performance') }}</span>
            </div>
          </template>

          <div class="system-status">
            <div class="status-item">
              <div class="status-label">API 连接状态</div>
              <el-tag type="success" size="small">
                <el-icon><CircleCheckFilled /></el-icon>
                正常
              </el-tag>
            </div>
            <div class="status-item">
              <div class="status-label">数据源状态</div>
              <el-tag type="success" size="small">
                <el-icon><CircleCheckFilled /></el-icon>
                在线
              </el-tag>
            </div>
            <div class="status-item">
              <div class="status-label">AI 模型状态</div>
              <el-tag type="success" size="small">
                <el-icon><CircleCheckFilled /></el-icon>
                就绪
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 0;
}

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  color: white;
  position: relative;
  overflow: hidden;
}

.welcome-banner::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  transform: translate(50%, -50%);
}

.banner-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.welcome-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.welcome-subtitle {
  font-size: 16px;
  margin: 0 0 16px 0;
  opacity: 0.9;
}

.quick-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  opacity: 0.8;
}

.banner-actions {
  display: flex;
  gap: 12px;
}

.banner-actions .el-button {
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  color: white;
  font-weight: 600;
}

.banner-actions .el-button:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

/* 主要内容区域 */
.main-content {
  margin-bottom: 24px;
}

.content-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 快速操作 */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.action-item:hover {
  background: #f8f9fa;
  border-color: #409eff;
  transform: translateX(4px);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.action-content {
  flex: 1;
}

.action-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.action-desc {
  font-size: 14px;
  color: #909399;
}

.action-arrow {
  color: #c0c4cc;
  transition: all 0.3s ease;
}

.action-item:hover .action-arrow {
  color: #409eff;
  transform: translateX(4px);
}

/* 系统状态 */
.system-status {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  font-size: 14px;
  color: #606266;
}

:deep(.el-tag) {
  border-radius: 6px;
  font-weight: 500;
}
</style>
