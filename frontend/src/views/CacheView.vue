<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 缓存数据
const cacheData = ref([
  {
    id: 1,
    key: 'stock_data_000001',
    type: '股票数据',
    size: '2.3 MB',
    created: '2024-01-15 10:30:00',
    expires: '2024-01-15 11:30:00',
    hits: 156,
    status: 'active'
  },
  {
    id: 2,
    key: 'analysis_result_000002',
    type: '分析结果',
    size: '1.8 MB',
    created: '2024-01-15 09:45:00',
    expires: '2024-01-15 10:45:00',
    hits: 89,
    status: 'expired'
  },
  {
    id: 3,
    key: 'market_overview',
    type: '市场概览',
    size: '512 KB',
    created: '2024-01-15 08:20:00',
    expires: '2024-01-15 09:20:00',
    hits: 234,
    status: 'active'
  }
])

const loading = ref(false)
const selectedItems = ref([])

// 缓存统计
const cacheStats = ref({
  totalSize: '4.6 MB',
  totalItems: 3,
  hitRate: '87.5%',
  memoryUsage: '45%'
})

// 刷新缓存数据
const refreshCache = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('缓存数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    loading.value = false
  }
}

// 清理过期缓存
const clearExpired = async () => {
  try {
    await ElMessageBox.confirm('确定要清理所有过期缓存吗？', '确认操作', {
      type: 'warning'
    })
    
    loading.value = true
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 移除过期项
    cacheData.value = cacheData.value.filter(item => item.status !== 'expired')
    cacheStats.value.totalItems = cacheData.value.length
    
    ElMessage.success('过期缓存已清理')
  } catch (error) {
    // 用户取消
  } finally {
    loading.value = false
  }
}

// 清空所有缓存
const clearAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有缓存吗？此操作不可恢复！', '危险操作', {
      type: 'error'
    })
    
    loading.value = true
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    cacheData.value = []
    cacheStats.value = {
      totalSize: '0 MB',
      totalItems: 0,
      hitRate: '0%',
      memoryUsage: '0%'
    }
    
    ElMessage.success('所有缓存已清空')
  } catch (error) {
    // 用户取消
  } finally {
    loading.value = false
  }
}

// 删除选中项
const deleteSelected = async () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请选择要删除的缓存项')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedItems.value.length} 个缓存项吗？`, '确认删除', {
      type: 'warning'
    })
    
    loading.value = true
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 删除选中项
    cacheData.value = cacheData.value.filter(item => !selectedItems.value.includes(item.id))
    selectedItems.value = []
    cacheStats.value.totalItems = cacheData.value.length
    
    ElMessage.success('选中缓存已删除')
  } catch (error) {
    // 用户取消
  } finally {
    loading.value = false
  }
}

// 获取状态标签类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'expired': return 'danger'
    default: return 'info'
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'active': return '活跃'
    case 'expired': return '已过期'
    default: return '未知'
  }
}

onMounted(() => {
  refreshCache()
})
</script>

<template>
  <div class="cache-view">
    <div class="cache-header">
      <h1>💾 缓存管理</h1>
      <p>管理系统缓存数据，优化性能</p>
    </div>

    <!-- 缓存统计 -->
    <el-row :gutter="24" class="cache-stats">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ cacheStats.totalSize }}</div>
            <div class="stat-label">总缓存大小</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ cacheStats.totalItems }}</div>
            <div class="stat-label">缓存项数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ cacheStats.hitRate }}</div>
            <div class="stat-label">命中率</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ cacheStats.memoryUsage }}</div>
            <div class="stat-label">内存使用率</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作按钮 -->
    <div class="cache-actions">
      <el-button type="primary" @click="refreshCache" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
      <el-button type="warning" @click="clearExpired" :loading="loading">
        <el-icon><Delete /></el-icon>
        清理过期
      </el-button>
      <el-button type="danger" @click="deleteSelected" :loading="loading">
        <el-icon><Delete /></el-icon>
        删除选中
      </el-button>
      <el-button type="danger" @click="clearAll" :loading="loading">
        <el-icon><Delete /></el-icon>
        清空所有
      </el-button>
    </div>

    <!-- 缓存列表 -->
    <el-card class="cache-table-card">
      <template #header>
        <div class="card-header">
          <el-icon><FolderOpened /></el-icon>
          <span>缓存列表</span>
        </div>
      </template>

      <el-table
        :data="cacheData"
        v-model:selection="selectedItems"
        style="width: 100%"
        :loading="loading"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="key" label="缓存键" min-width="200" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="size" label="大小" width="100" />
        <el-table-column prop="created" label="创建时间" width="160" />
        <el-table-column prop="expires" label="过期时间" width="160" />
        <el-table-column prop="hits" label="命中次数" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="deleteSelected">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.cache-view {
  padding: 0;
}

.cache-header {
  margin-bottom: 30px;
}

.cache-header h1 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.cache-header p {
  margin: 0;
  color: #909399;
  font-size: 16px;
}

.cache-stats {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.stat-content {
  padding: 20px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.cache-actions {
  margin-bottom: 24px;
}

.cache-actions .el-button {
  margin-right: 12px;
}

.cache-table-card {
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
</style>
