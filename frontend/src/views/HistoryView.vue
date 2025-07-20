<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 历史记录数据
const historyData = ref([
  {
    id: 1,
    stockCode: '000001',
    stockName: '平安银行',
    analysisType: '综合分析',
    result: 'BUY',
    confidence: 85,
    timestamp: '2024-01-15 14:30:25',
    duration: '2.3s',
    tokens: 1250,
    cost: 0.05,
    status: 'success'
  },
  {
    id: 2,
    stockCode: '000002',
    stockName: '万科A',
    analysisType: '技术分析',
    result: 'HOLD',
    confidence: 72,
    timestamp: '2024-01-15 13:45:12',
    duration: '1.8s',
    tokens: 980,
    cost: 0.04,
    status: 'success'
  },
  {
    id: 3,
    stockCode: '600036',
    stockName: '招商银行',
    analysisType: '基础分析',
    result: 'SELL',
    confidence: 68,
    timestamp: '2024-01-15 12:20:08',
    duration: '3.1s',
    tokens: 1450,
    cost: 0.06,
    status: 'success'
  },
  {
    id: 4,
    stockCode: '000858',
    stockName: '五粮液',
    analysisType: '综合分析',
    result: 'ERROR',
    confidence: 0,
    timestamp: '2024-01-15 11:15:33',
    duration: '0.5s',
    tokens: 0,
    cost: 0,
    status: 'failed'
  }
])

const loading = ref(false)
const searchQuery = ref('')
const selectedDate = ref('')
const selectedStatus = ref('')

// 过滤选项
const statusOptions = [
  { label: '全部', value: '' },
  { label: '成功', value: 'success' },
  { label: '失败', value: 'failed' }
]

const analysisTypes = [
  { label: '全部', value: '' },
  { label: '基础分析', value: '基础分析' },
  { label: '技术分析', value: '技术分析' },
  { label: '综合分析', value: '综合分析' }
]

// 过滤后的数据
const filteredData = computed(() => {
  let data = historyData.value

  if (searchQuery.value) {
    data = data.filter(item => 
      item.stockCode.includes(searchQuery.value) || 
      item.stockName.includes(searchQuery.value)
    )
  }

  if (selectedStatus.value) {
    data = data.filter(item => item.status === selectedStatus.value)
  }

  return data
})

// 刷新数据
const refreshData = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetails = (row: any) => {
  ElMessage.info(`查看 ${row.stockName} 的分析详情`)
}

// 重新分析
const reAnalyze = (row: any) => {
  ElMessage.info(`重新分析 ${row.stockName}`)
}

// 导出数据
const exportData = () => {
  ElMessage.success('导出功能开发中...')
}

// 获取结果标签类型
const getResultType = (result: string) => {
  switch (result) {
    case 'BUY': return 'success'
    case 'HOLD': return 'warning'
    case 'SELL': return 'danger'
    case 'ERROR': return 'info'
    default: return 'info'
  }
}

// 获取结果文本
const getResultText = (result: string) => {
  switch (result) {
    case 'BUY': return '买入'
    case 'HOLD': return '持有'
    case 'SELL': return '卖出'
    case 'ERROR': return '错误'
    default: return '未知'
  }
}

// 获取状态标签类型
const getStatusType = (status: string) => {
  return status === 'success' ? 'success' : 'danger'
}

// 获取状态文本
const getStatusText = (status: string) => {
  return status === 'success' ? '成功' : '失败'
}

onMounted(() => {
  refreshData()
})
</script>

<template>
  <div class="history-view">
    <div class="history-header">
      <h1>📝 历史记录</h1>
      <p>查看所有股票分析历史记录</p>
    </div>

    <!-- 搜索和过滤 -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input
            v-model="searchQuery"
            placeholder="搜索股票代码或名称"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="selectedStatus" placeholder="状态筛选" clearable>
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-date-picker
            v-model="selectedDate"
            type="date"
            placeholder="选择日期"
            clearable
          />
        </el-col>
        <el-col :span="8">
          <el-button type="primary" @click="refreshData" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button @click="exportData">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 历史记录表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>分析记录 ({{ filteredData.length }})</span>
        </div>
      </template>

      <el-table
        :data="filteredData"
        style="width: 100%"
        :loading="loading"
        stripe
      >
        <el-table-column prop="stockCode" label="股票代码" width="100" />
        <el-table-column prop="stockName" label="股票名称" width="120" />
        <el-table-column prop="analysisType" label="分析类型" width="100" />
        <el-table-column prop="result" label="分析结果" width="100">
          <template #default="{ row }">
            <el-tag :type="getResultType(row.result)" size="small">
              {{ getResultText(row.result) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="置信度" width="100">
          <template #default="{ row }">
            <span v-if="row.confidence > 0">{{ row.confidence }}%</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="分析时间" width="160" />
        <el-table-column prop="duration" label="耗时" width="80" />
        <el-table-column prop="tokens" label="Token" width="80">
          <template #default="{ row }">
            <span v-if="row.tokens > 0">{{ row.tokens }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="cost" label="成本" width="80">
          <template #default="{ row }">
            <span v-if="row.cost > 0">${{ row.cost.toFixed(3) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetails(row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button type="success" size="small" @click="reAnalyze(row)">
              <el-icon><Refresh /></el-icon>
              重新分析
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredData.length"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="20"
        />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.history-view {
  padding: 0;
}

.history-header {
  margin-bottom: 30px;
}

.history-header h1 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.history-header p {
  margin: 0;
  color: #909399;
  font-size: 16px;
}

.filter-card {
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.table-card {
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

:deep(.el-table) {
  border-radius: 8px;
}

:deep(.el-table th) {
  background-color: #fafafa;
}
</style>
