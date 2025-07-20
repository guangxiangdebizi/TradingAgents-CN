<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// Token 统计数据
const tokenStats = ref({
  today: {
    input: 12450,
    output: 8920,
    total: 21370,
    cost: 0.85
  },
  thisMonth: {
    input: 345600,
    output: 234800,
    total: 580400,
    cost: 23.22
  },
  total: {
    input: 1234567,
    output: 876543,
    total: 2111110,
    cost: 84.44
  }
})

// 模型使用统计
const modelStats = ref([
  {
    model: 'deepseek-chat',
    requests: 1234,
    tokens: 456789,
    cost: 18.27,
    percentage: 65.2
  },
  {
    model: 'gpt-3.5-turbo',
    requests: 567,
    tokens: 234567,
    cost: 4.69,
    percentage: 20.8
  },
  {
    model: 'qwen-plus',
    requests: 345,
    tokens: 123456,
    cost: 2.47,
    percentage: 14.0
  }
])

// 每日使用趋势（模拟数据）
const dailyUsage = ref([
  { date: '01-10', tokens: 15000, cost: 0.60 },
  { date: '01-11', tokens: 18000, cost: 0.72 },
  { date: '01-12', tokens: 22000, cost: 0.88 },
  { date: '01-13', tokens: 19000, cost: 0.76 },
  { date: '01-14', tokens: 25000, cost: 1.00 },
  { date: '01-15', tokens: 21370, cost: 0.85 }
])

const loading = ref(false)

// 刷新统计数据
const refreshStats = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('统计数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}

// 导出报告
const exportReport = () => {
  ElMessage.success('报告导出功能开发中...')
}

// 获取成本颜色
const getCostColor = (cost: number) => {
  if (cost < 1) return '#67c23a'
  if (cost < 5) return '#e6a23c'
  return '#f56c6c'
}

onMounted(() => {
  refreshStats()
})
</script>

<template>
  <div class="tokens-view">
    <div class="tokens-header">
      <h1>🔑 Token统计</h1>
      <p>监控 AI 模型 Token 使用情况和成本</p>
    </div>

    <!-- 统计概览 -->
    <el-row :gutter="24" class="stats-overview">
      <el-col :span="8">
        <el-card class="overview-card today">
          <div class="card-content">
            <div class="card-icon">📅</div>
            <div class="card-info">
              <h3>今日使用</h3>
              <div class="token-info">
                <div class="token-item">
                  <span class="label">输入:</span>
                  <span class="value">{{ tokenStats.today.input.toLocaleString() }}</span>
                </div>
                <div class="token-item">
                  <span class="label">输出:</span>
                  <span class="value">{{ tokenStats.today.output.toLocaleString() }}</span>
                </div>
                <div class="token-total">
                  总计: {{ tokenStats.today.total.toLocaleString() }} tokens
                </div>
                <div class="cost-info">
                  成本: ${{ tokenStats.today.cost.toFixed(2) }}
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="overview-card month">
          <div class="card-content">
            <div class="card-icon">📊</div>
            <div class="card-info">
              <h3>本月使用</h3>
              <div class="token-info">
                <div class="token-item">
                  <span class="label">输入:</span>
                  <span class="value">{{ tokenStats.thisMonth.input.toLocaleString() }}</span>
                </div>
                <div class="token-item">
                  <span class="label">输出:</span>
                  <span class="value">{{ tokenStats.thisMonth.output.toLocaleString() }}</span>
                </div>
                <div class="token-total">
                  总计: {{ tokenStats.thisMonth.total.toLocaleString() }} tokens
                </div>
                <div class="cost-info">
                  成本: ${{ tokenStats.thisMonth.cost.toFixed(2) }}
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="overview-card total">
          <div class="card-content">
            <div class="card-icon">💰</div>
            <div class="card-info">
              <h3>累计使用</h3>
              <div class="token-info">
                <div class="token-item">
                  <span class="label">输入:</span>
                  <span class="value">{{ tokenStats.total.input.toLocaleString() }}</span>
                </div>
                <div class="token-item">
                  <span class="label">输出:</span>
                  <span class="value">{{ tokenStats.total.output.toLocaleString() }}</span>
                </div>
                <div class="token-total">
                  总计: {{ tokenStats.total.total.toLocaleString() }} tokens
                </div>
                <div class="cost-info">
                  成本: ${{ tokenStats.total.cost.toFixed(2) }}
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作按钮 -->
    <div class="tokens-actions">
      <el-button type="primary" @click="refreshStats" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
      <el-button @click="exportReport">
        <el-icon><Download /></el-icon>
        导出报告
      </el-button>
    </div>

    <el-row :gutter="24">
      <!-- 模型使用统计 -->
      <el-col :span="12">
        <el-card class="stats-card">
          <template #header>
            <div class="card-header">
              <el-icon><ChatDotRound /></el-icon>
              <span>模型使用统计</span>
            </div>
          </template>

          <div class="model-stats">
            <div v-for="model in modelStats" :key="model.model" class="model-item">
              <div class="model-info">
                <div class="model-name">{{ model.model }}</div>
                <div class="model-details">
                  <span>请求: {{ model.requests }}</span>
                  <span>Token: {{ model.tokens.toLocaleString() }}</span>
                  <span :style="{ color: getCostColor(model.cost) }">
                    成本: ${{ model.cost.toFixed(2) }}
                  </span>
                </div>
              </div>
              <div class="model-percentage">
                <el-progress 
                  :percentage="model.percentage" 
                  :stroke-width="8"
                  :show-text="false"
                />
                <span class="percentage-text">{{ model.percentage }}%</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 每日使用趋势 -->
      <el-col :span="12">
        <el-card class="stats-card">
          <template #header>
            <div class="card-header">
              <el-icon><TrendCharts /></el-icon>
              <span>每日使用趋势</span>
            </div>
          </template>

          <div class="daily-trends">
            <div v-for="day in dailyUsage" :key="day.date" class="trend-item">
              <div class="trend-date">{{ day.date }}</div>
              <div class="trend-bar">
                <div 
                  class="trend-fill" 
                  :style="{ width: (day.tokens / 25000 * 100) + '%' }"
                ></div>
              </div>
              <div class="trend-info">
                <span class="trend-tokens">{{ day.tokens.toLocaleString() }}</span>
                <span class="trend-cost">${{ day.cost.toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.tokens-view {
  padding: 0;
}

.tokens-header {
  margin-bottom: 30px;
}

.tokens-header h1 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.tokens-header p {
  margin: 0;
  color: #909399;
  font-size: 16px;
}

.stats-overview {
  margin-bottom: 24px;
}

.overview-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: none;
}

.card-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.card-icon {
  font-size: 32px;
  opacity: 0.8;
}

.card-info h3 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.token-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 14px;
}

.token-item .label {
  color: #909399;
}

.token-item .value {
  color: #606266;
  font-weight: 500;
}

.token-total {
  margin: 8px 0;
  font-weight: 600;
  color: #409eff;
}

.cost-info {
  font-size: 16px;
  font-weight: 700;
  color: #67c23a;
}

.tokens-actions {
  margin-bottom: 24px;
}

.tokens-actions .el-button {
  margin-right: 12px;
}

.stats-card {
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

.model-stats {
  padding: 0;
}

.model-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.model-item:last-child {
  border-bottom: none;
}

.model-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.model-details {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.model-percentage {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
}

.percentage-text {
  font-size: 12px;
  color: #606266;
  min-width: 30px;
}

.daily-trends {
  padding: 0;
}

.trend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.trend-item:last-child {
  border-bottom: none;
}

.trend-date {
  min-width: 50px;
  font-size: 12px;
  color: #909399;
}

.trend-bar {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.trend-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #67c23a);
  transition: width 0.3s ease;
}

.trend-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 80px;
}

.trend-tokens {
  font-size: 12px;
  color: #606266;
}

.trend-cost {
  font-size: 11px;
  color: #67c23a;
  font-weight: 600;
}
</style>
