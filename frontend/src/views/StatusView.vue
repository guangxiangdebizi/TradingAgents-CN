<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 系统状态数据
const systemStatus = ref({
  api: {
    status: 'online',
    responseTime: 125,
    uptime: '99.9%',
    lastCheck: '2024-01-15 14:30:00'
  },
  database: {
    status: 'online',
    connections: 15,
    maxConnections: 100,
    queryTime: 45
  },
  cache: {
    status: 'online',
    hitRate: 87.5,
    memoryUsage: 45,
    totalKeys: 1234
  },
  llm: {
    status: 'online',
    provider: 'DeepSeek',
    model: 'deepseek-chat',
    avgResponseTime: 2.3
  }
})

// 服务列表
const services = ref([
  {
    name: 'API Gateway',
    status: 'running',
    port: 8000,
    cpu: 15.2,
    memory: 256,
    uptime: '5d 12h 30m'
  },
  {
    name: 'Data Service',
    status: 'running',
    port: 8001,
    cpu: 8.7,
    memory: 128,
    uptime: '5d 12h 28m'
  },
  {
    name: 'Analysis Engine',
    status: 'running',
    port: 8002,
    cpu: 25.6,
    memory: 512,
    uptime: '5d 12h 25m'
  },
  {
    name: 'Cache Service',
    status: 'warning',
    port: 6379,
    cpu: 5.3,
    memory: 64,
    uptime: '2d 8h 15m'
  }
])

// 系统资源
const systemResources = ref({
  cpu: {
    usage: 18.5,
    cores: 8,
    load: [0.8, 1.2, 0.9]
  },
  memory: {
    used: 6.2,
    total: 16,
    usage: 38.8
  },
  disk: {
    used: 45.6,
    total: 100,
    usage: 45.6
  },
  network: {
    inbound: 125.6,
    outbound: 89.3
  }
})

const loading = ref(false)

// 刷新状态
const refreshStatus = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('状态已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}

// 重启服务
const restartService = (serviceName: string) => {
  ElMessage.info(`重启服务: ${serviceName}`)
}

// 获取状态颜色
const getStatusColor = (status: string) => {
  switch (status) {
    case 'online':
    case 'running': return '#67c23a'
    case 'warning': return '#e6a23c'
    case 'offline':
    case 'stopped': return '#f56c6c'
    default: return '#909399'
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'online': return '在线'
    case 'running': return '运行中'
    case 'warning': return '警告'
    case 'offline': return '离线'
    case 'stopped': return '已停止'
    default: return '未知'
  }
}

// 获取资源使用率颜色
const getUsageColor = (usage: number) => {
  if (usage < 50) return '#67c23a'
  if (usage < 80) return '#e6a23c'
  return '#f56c6c'
}

onMounted(() => {
  refreshStatus()
})
</script>

<template>
  <div class="status-view">
    <div class="status-header">
      <h1>🔧 系统状态</h1>
      <p>监控系统各组件运行状态</p>
    </div>

    <!-- 核心服务状态 -->
    <el-row :gutter="24" class="core-services">
      <el-col :span="6">
        <el-card class="service-card">
          <div class="service-content">
            <div class="service-icon" :style="{ color: getStatusColor(systemStatus.api.status) }">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="service-info">
              <h3>API 服务</h3>
              <div class="service-status">
                <el-tag :color="getStatusColor(systemStatus.api.status)" effect="light" size="small">
                  {{ getStatusText(systemStatus.api.status) }}
                </el-tag>
              </div>
              <div class="service-metrics">
                <div>响应时间: {{ systemStatus.api.responseTime }}ms</div>
                <div>可用性: {{ systemStatus.api.uptime }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="service-card">
          <div class="service-content">
            <div class="service-icon" :style="{ color: getStatusColor(systemStatus.database.status) }">
              <el-icon><DataBoard /></el-icon>
            </div>
            <div class="service-info">
              <h3>数据库</h3>
              <div class="service-status">
                <el-tag :color="getStatusColor(systemStatus.database.status)" effect="light" size="small">
                  {{ getStatusText(systemStatus.database.status) }}
                </el-tag>
              </div>
              <div class="service-metrics">
                <div>连接数: {{ systemStatus.database.connections }}/{{ systemStatus.database.maxConnections }}</div>
                <div>查询时间: {{ systemStatus.database.queryTime }}ms</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="service-card">
          <div class="service-content">
            <div class="service-icon" :style="{ color: getStatusColor(systemStatus.cache.status) }">
              <el-icon><FolderOpened /></el-icon>
            </div>
            <div class="service-info">
              <h3>缓存服务</h3>
              <div class="service-status">
                <el-tag :color="getStatusColor(systemStatus.cache.status)" effect="light" size="small">
                  {{ getStatusText(systemStatus.cache.status) }}
                </el-tag>
              </div>
              <div class="service-metrics">
                <div>命中率: {{ systemStatus.cache.hitRate }}%</div>
                <div>内存使用: {{ systemStatus.cache.memoryUsage }}%</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="service-card">
          <div class="service-content">
            <div class="service-icon" :style="{ color: getStatusColor(systemStatus.llm.status) }">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="service-info">
              <h3>AI 模型</h3>
              <div class="service-status">
                <el-tag :color="getStatusColor(systemStatus.llm.status)" effect="light" size="small">
                  {{ getStatusText(systemStatus.llm.status) }}
                </el-tag>
              </div>
              <div class="service-metrics">
                <div>提供商: {{ systemStatus.llm.provider }}</div>
                <div>响应时间: {{ systemStatus.llm.avgResponseTime }}s</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作按钮 -->
    <div class="status-actions">
      <el-button type="primary" @click="refreshStatus" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新状态
      </el-button>
    </div>

    <el-row :gutter="24">
      <!-- 服务列表 -->
      <el-col :span="12">
        <el-card class="services-card">
          <template #header>
            <div class="card-header">
              <el-icon><Monitor /></el-icon>
              <span>服务列表</span>
            </div>
          </template>

          <div class="services-list">
            <div v-for="service in services" :key="service.name" class="service-item">
              <div class="service-basic">
                <div class="service-name">{{ service.name }}</div>
                <div class="service-port">:{{ service.port }}</div>
                <el-tag 
                  :color="getStatusColor(service.status)" 
                  effect="light" 
                  size="small"
                >
                  {{ getStatusText(service.status) }}
                </el-tag>
              </div>
              <div class="service-details">
                <div class="detail-item">
                  <span>CPU: {{ service.cpu }}%</span>
                  <el-progress 
                    :percentage="service.cpu" 
                    :stroke-width="4"
                    :show-text="false"
                    :color="getUsageColor(service.cpu)"
                  />
                </div>
                <div class="detail-item">
                  <span>内存: {{ service.memory }}MB</span>
                </div>
                <div class="detail-item">
                  <span>运行时间: {{ service.uptime }}</span>
                </div>
              </div>
              <div class="service-actions">
                <el-button size="small" @click="restartService(service.name)">
                  <el-icon><Refresh /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 系统资源 -->
      <el-col :span="12">
        <el-card class="resources-card">
          <template #header>
            <div class="card-header">
              <el-icon><Monitor /></el-icon>
              <span>系统资源</span>
            </div>
          </template>

          <div class="resources-list">
            <div class="resource-item">
              <div class="resource-header">
                <span class="resource-name">CPU 使用率</span>
                <span class="resource-value">{{ systemResources.cpu.usage }}%</span>
              </div>
              <el-progress 
                :percentage="systemResources.cpu.usage" 
                :stroke-width="8"
                :color="getUsageColor(systemResources.cpu.usage)"
              />
              <div class="resource-details">
                核心数: {{ systemResources.cpu.cores }} | 负载: {{ systemResources.cpu.load.join(', ') }}
              </div>
            </div>

            <div class="resource-item">
              <div class="resource-header">
                <span class="resource-name">内存使用</span>
                <span class="resource-value">{{ systemResources.memory.usage }}%</span>
              </div>
              <el-progress 
                :percentage="systemResources.memory.usage" 
                :stroke-width="8"
                :color="getUsageColor(systemResources.memory.usage)"
              />
              <div class="resource-details">
                已用: {{ systemResources.memory.used }}GB / 总计: {{ systemResources.memory.total }}GB
              </div>
            </div>

            <div class="resource-item">
              <div class="resource-header">
                <span class="resource-name">磁盘使用</span>
                <span class="resource-value">{{ systemResources.disk.usage }}%</span>
              </div>
              <el-progress 
                :percentage="systemResources.disk.usage" 
                :stroke-width="8"
                :color="getUsageColor(systemResources.disk.usage)"
              />
              <div class="resource-details">
                已用: {{ systemResources.disk.used }}GB / 总计: {{ systemResources.disk.total }}GB
              </div>
            </div>

            <div class="resource-item">
              <div class="resource-header">
                <span class="resource-name">网络流量</span>
                <span class="resource-value">{{ systemResources.network.inbound + systemResources.network.outbound }} MB/s</span>
              </div>
              <div class="network-details">
                <div class="network-item">
                  <span>入站: {{ systemResources.network.inbound }} MB/s</span>
                </div>
                <div class="network-item">
                  <span>出站: {{ systemResources.network.outbound }} MB/s</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.status-view {
  padding: 0;
}

.status-header {
  margin-bottom: 30px;
}

.status-header h1 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.status-header p {
  margin: 0;
  color: #909399;
  font-size: 16px;
}

.core-services {
  margin-bottom: 24px;
}

.service-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.service-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.service-icon {
  font-size: 32px;
}

.service-info h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.service-status {
  margin-bottom: 8px;
}

.service-metrics {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.status-actions {
  margin-bottom: 24px;
}

.services-card,
.resources-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.service-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.service-item:last-child {
  border-bottom: none;
}

.service-basic {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 200px;
}

.service-name {
  font-weight: 600;
  color: #303133;
}

.service-port {
  font-size: 12px;
  color: #909399;
}

.service-details {
  flex: 1;
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #606266;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.resource-item {
  margin-bottom: 24px;
}

.resource-item:last-child {
  margin-bottom: 0;
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.resource-name {
  font-weight: 600;
  color: #303133;
}

.resource-value {
  font-weight: 600;
  color: #409eff;
}

.resource-details {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.network-details {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
}

.network-item {
  font-size: 12px;
  color: #606266;
}
</style>
