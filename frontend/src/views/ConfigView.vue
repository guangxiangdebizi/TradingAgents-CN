<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

// 配置数据
const config = reactive({
  api: {
    baseUrl: 'http://localhost:8000',
    timeout: 30000,
    retryCount: 3
  },
  llm: {
    provider: 'deepseek',
    model: 'deepseek-chat',
    temperature: 0.7,
    maxTokens: 4000
  },
  data: {
    source: 'akshare',
    cacheEnabled: true,
    cacheExpiry: 3600
  },
  system: {
    logLevel: 'INFO',
    enableDebug: false,
    maxConcurrency: 5
  }
})

const loading = ref(false)

// LLM 提供商选项
const llmProviders = [
  { label: 'DeepSeek', value: 'deepseek' },
  { label: 'OpenAI', value: 'openai' },
  { label: 'Qwen', value: 'qwen' },
  { label: 'Claude', value: 'claude' }
]

// 数据源选项
const dataSources = [
  { label: 'AKShare', value: 'akshare' },
  { label: 'Tushare', value: 'tushare' },
  { label: 'Yahoo Finance', value: 'yfinance' },
  { label: 'BaoStock', value: 'baostock' }
]

// 日志级别选项
const logLevels = [
  { label: 'DEBUG', value: 'DEBUG' },
  { label: 'INFO', value: 'INFO' },
  { label: 'WARNING', value: 'WARNING' },
  { label: 'ERROR', value: 'ERROR' }
]

// 保存配置
const saveConfig = async () => {
  loading.value = true
  try {
    // 模拟 API 调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('配置保存失败')
  } finally {
    loading.value = false
  }
}

// 重置配置
const resetConfig = () => {
  Object.assign(config, {
    api: {
      baseUrl: 'http://localhost:8000',
      timeout: 30000,
      retryCount: 3
    },
    llm: {
      provider: 'deepseek',
      model: 'deepseek-chat',
      temperature: 0.7,
      maxTokens: 4000
    },
    data: {
      source: 'akshare',
      cacheEnabled: true,
      cacheExpiry: 3600
    },
    system: {
      logLevel: 'INFO',
      enableDebug: false,
      maxConcurrency: 5
    }
  })
  ElMessage.info('配置已重置')
}

// 测试连接
const testConnection = async () => {
  try {
    ElMessage.loading('测试连接中...')
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('连接测试成功')
  } catch (error) {
    ElMessage.error('连接测试失败')
  }
}
</script>

<template>
  <div class="config-view">
    <div class="config-header">
      <h1>⚙️ 配置管理</h1>
      <p>管理系统各项配置参数</p>
    </div>

    <el-row :gutter="24">
      <!-- API 配置 -->
      <el-col :span="12">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><Connection /></el-icon>
              <span>API 配置</span>
            </div>
          </template>
          
          <el-form :model="config.api" label-width="120px">
            <el-form-item label="API 地址">
              <el-input v-model="config.api.baseUrl" placeholder="http://localhost:8000" />
            </el-form-item>
            <el-form-item label="超时时间(ms)">
              <el-input-number v-model="config.api.timeout" :min="1000" :max="60000" :step="1000" />
            </el-form-item>
            <el-form-item label="重试次数">
              <el-input-number v-model="config.api.retryCount" :min="0" :max="10" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testConnection">
                <el-icon><Connection /></el-icon>
                测试连接
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- LLM 配置 -->
      <el-col :span="12">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><ChatDotRound /></el-icon>
              <span>LLM 配置</span>
            </div>
          </template>
          
          <el-form :model="config.llm" label-width="120px">
            <el-form-item label="提供商">
              <el-select v-model="config.llm.provider" style="width: 100%">
                <el-option
                  v-for="item in llmProviders"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="模型">
              <el-input v-model="config.llm.model" placeholder="deepseek-chat" />
            </el-form-item>
            <el-form-item label="温度">
              <el-slider v-model="config.llm.temperature" :min="0" :max="2" :step="0.1" show-input />
            </el-form-item>
            <el-form-item label="最大Token">
              <el-input-number v-model="config.llm.maxTokens" :min="100" :max="8000" :step="100" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" style="margin-top: 24px;">
      <!-- 数据源配置 -->
      <el-col :span="12">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><DataBoard /></el-icon>
              <span>数据源配置</span>
            </div>
          </template>
          
          <el-form :model="config.data" label-width="120px">
            <el-form-item label="数据源">
              <el-select v-model="config.data.source" style="width: 100%">
                <el-option
                  v-for="item in dataSources"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="启用缓存">
              <el-switch v-model="config.data.cacheEnabled" />
            </el-form-item>
            <el-form-item label="缓存过期(秒)">
              <el-input-number v-model="config.data.cacheExpiry" :min="60" :max="86400" :step="60" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 系统配置 -->
      <el-col :span="12">
        <el-card class="config-card">
          <template #header>
            <div class="card-header">
              <el-icon><Tools /></el-icon>
              <span>系统配置</span>
            </div>
          </template>
          
          <el-form :model="config.system" label-width="120px">
            <el-form-item label="日志级别">
              <el-select v-model="config.system.logLevel" style="width: 100%">
                <el-option
                  v-for="item in logLevels"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="调试模式">
              <el-switch v-model="config.system.enableDebug" />
            </el-form-item>
            <el-form-item label="最大并发">
              <el-input-number v-model="config.system.maxConcurrency" :min="1" :max="20" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作按钮 -->
    <div class="config-actions">
      <el-button type="primary" size="large" @click="saveConfig" :loading="loading">
        <el-icon><Check /></el-icon>
        保存配置
      </el-button>
      <el-button size="large" @click="resetConfig">
        <el-icon><Refresh /></el-icon>
        重置配置
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.config-view {
  padding: 0;
}

.config-header {
  margin-bottom: 30px;
}

.config-header h1 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.config-header p {
  margin: 0;
  color: #909399;
  font-size: 16px;
}

.config-card {
  margin-bottom: 24px;
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

.config-actions {
  margin-top: 30px;
  text-align: center;
}

.config-actions .el-button {
  margin: 0 10px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-slider) {
  margin: 12px 0;
}
</style>
