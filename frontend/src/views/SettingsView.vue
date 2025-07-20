<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

// 设置表单数据
const settingsForm = reactive({
  // API 配置
  apiSettings: {
    baseUrl: 'http://localhost:8000',
    timeout: 30000,
    retryCount: 3
  },
  // 数据源配置
  dataSource: {
    primary: 'akshare',
    backup: 'yfinance',
    enableCache: true,
    cacheExpiry: 3600
  },
  // LLM 配置
  llmSettings: {
    provider: 'deepseek',
    model: 'deepseek-chat',
    temperature: 0.7,
    maxTokens: 4000
  },
  // 通知设置
  notifications: {
    enableEmail: false,
    enablePush: true,
    analysisComplete: true,
    systemAlerts: true
  }
})

const loading = ref(false)

// 数据源选项
const dataSourceOptions = [
  { label: 'AKShare', value: 'akshare' },
  { label: 'Yahoo Finance', value: 'yfinance' },
  { label: 'Tushare', value: 'tushare' },
  { label: 'BaoStock', value: 'baostock' }
]

// LLM 提供商选项
const llmProviders = [
  { label: 'DeepSeek', value: 'deepseek' },
  { label: 'OpenAI', value: 'openai' },
  { label: 'Tongyi', value: 'tongyi' },
  { label: 'Google Gemini', value: 'gemini' }
]

// 保存设置
const saveSettings = async () => {
  loading.value = true
  
  try {
    // 模拟 API 调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('设置保存成功')
  } catch (error) {
    ElMessage.error('设置保存失败')
  } finally {
    loading.value = false
  }
}

// 重置设置
const resetSettings = () => {
  Object.assign(settingsForm, {
    apiSettings: {
      baseUrl: 'http://localhost:8000',
      timeout: 30000,
      retryCount: 3
    },
    dataSource: {
      primary: 'akshare',
      backup: 'yfinance',
      enableCache: true,
      cacheExpiry: 3600
    },
    llmSettings: {
      provider: 'deepseek',
      model: 'deepseek-chat',
      temperature: 0.7,
      maxTokens: 4000
    },
    notifications: {
      enableEmail: false,
      enablePush: true,
      analysisComplete: true,
      systemAlerts: true
    }
  })
  
  ElMessage.info('设置已重置为默认值')
}

// 测试连接
const testConnection = async () => {
  try {
    ElMessage.info('正在测试连接...')
    await new Promise(resolve => setTimeout(resolve, 2000))
    ElMessage.success('连接测试成功')
  } catch (error) {
    ElMessage.error('连接测试失败')
  }
}
</script>

<template>
  <div class="settings-view">
    <div class="settings-header">
      <h1>系统设置</h1>
      <p>配置 TradingAgents-CN 系统参数</p>
    </div>

    <el-form :model="settingsForm" label-width="140px">
      <!-- API 配置 -->
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <el-icon><Connection /></el-icon>
            <span>API 配置</span>
          </div>
        </template>

        <el-form-item label="API 基础地址">
          <el-input v-model="settingsForm.apiSettings.baseUrl" placeholder="http://localhost:8000" />
        </el-form-item>

        <el-form-item label="请求超时时间">
          <el-input-number
            v-model="settingsForm.apiSettings.timeout"
            :min="5000"
            :max="120000"
            :step="1000"
            style="width: 200px"
          />
          <span style="margin-left: 10px; color: #909399;">毫秒</span>
        </el-form-item>

        <el-form-item label="重试次数">
          <el-input-number
            v-model="settingsForm.apiSettings.retryCount"
            :min="0"
            :max="10"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="testConnection">
            <el-icon><Connection /></el-icon>
            测试连接
          </el-button>
        </el-form-item>
      </el-card>

      <!-- 数据源配置 -->
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <el-icon><Coin /></el-icon>
            <span>数据源配置</span>
          </div>
        </template>

        <el-form-item label="主要数据源">
          <el-select v-model="settingsForm.dataSource.primary" style="width: 200px">
            <el-option
              v-for="item in dataSourceOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="备用数据源">
          <el-select v-model="settingsForm.dataSource.backup" style="width: 200px">
            <el-option
              v-for="item in dataSourceOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="启用缓存">
          <el-switch v-model="settingsForm.dataSource.enableCache" />
        </el-form-item>

        <el-form-item label="缓存过期时间" v-if="settingsForm.dataSource.enableCache">
          <el-input-number
            v-model="settingsForm.dataSource.cacheExpiry"
            :min="300"
            :max="86400"
            :step="300"
            style="width: 200px"
          />
          <span style="margin-left: 10px; color: #909399;">秒</span>
        </el-form-item>
      </el-card>

      <!-- LLM 配置 -->
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <el-icon><ChatDotRound /></el-icon>
            <span>LLM 配置</span>
          </div>
        </template>

        <el-form-item label="LLM 提供商">
          <el-select v-model="settingsForm.llmSettings.provider" style="width: 200px">
            <el-option
              v-for="item in llmProviders"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="模型名称">
          <el-input v-model="settingsForm.llmSettings.model" style="width: 300px" />
        </el-form-item>

        <el-form-item label="Temperature">
          <el-slider
            v-model="settingsForm.llmSettings.temperature"
            :min="0"
            :max="2"
            :step="0.1"
            :format-tooltip="(val) => val.toFixed(1)"
            style="width: 300px"
          />
        </el-form-item>

        <el-form-item label="最大 Token 数">
          <el-input-number
            v-model="settingsForm.llmSettings.maxTokens"
            :min="1000"
            :max="32000"
            :step="1000"
            style="width: 200px"
          />
        </el-form-item>
      </el-card>

      <!-- 通知设置 -->
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <el-icon><Bell /></el-icon>
            <span>通知设置</span>
          </div>
        </template>

        <el-form-item label="邮件通知">
          <el-switch v-model="settingsForm.notifications.enableEmail" />
        </el-form-item>

        <el-form-item label="推送通知">
          <el-switch v-model="settingsForm.notifications.enablePush" />
        </el-form-item>

        <el-form-item label="分析完成通知">
          <el-switch v-model="settingsForm.notifications.analysisComplete" />
        </el-form-item>

        <el-form-item label="系统警报">
          <el-switch v-model="settingsForm.notifications.systemAlerts" />
        </el-form-item>
      </el-card>

      <!-- 操作按钮 -->
      <div class="settings-actions">
        <el-button type="primary" @click="saveSettings" :loading="loading">
          <el-icon><Check /></el-icon>
          保存设置
        </el-button>
        <el-button @click="resetSettings">
          <el-icon><Refresh /></el-icon>
          重置为默认
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<style scoped>
.settings-view {
  padding: 0;
}

.settings-header {
  margin-bottom: 30px;
}

.settings-header h1 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.settings-header p {
  margin: 0;
  color: #909399;
  font-size: 16px;
}

.settings-card {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.settings-actions {
  text-align: center;
  padding: 30px 0;
}

.settings-actions .el-button {
  margin: 0 10px;
}
</style>
