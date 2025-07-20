<template>
  <div class="analysis-container">
    <!-- 配置面板 -->
    <el-card class="config-panel" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>⚙️ 分析配置</span>
        </div>
      </template>
      
      <el-form :model="analysisForm" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="市场类型" prop="marketType">
              <el-select v-model="analysisForm.marketType" placeholder="选择市场">
                <el-option label="A股" value="A股" />
                <el-option label="美股" value="美股" />
                <el-option label="港股" value="港股" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="股票代码" prop="stockCode">
              <el-input 
                v-model="analysisForm.stockCode" 
                placeholder="输入股票代码"
                @keyup.enter="startAnalysis"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="研究深度" prop="researchDepth">
          <el-slider 
            v-model="analysisForm.researchDepth" 
            :min="1" 
            :max="5" 
            :marks="depthMarks"
            show-stops
          />
        </el-form-item>
        
        <el-form-item label="分析师团队" prop="analysts">
          <el-checkbox-group v-model="analysisForm.analysts">
            <el-checkbox label="market">📈 市场分析师</el-checkbox>
            <el-checkbox label="fundamentals">📊 基本面分析师</el-checkbox>
            <el-checkbox label="news">📰 新闻分析师</el-checkbox>
            <el-checkbox label="social">💭 社交媒体分析师</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="自定义提示">
          <el-input 
            v-model="analysisForm.customPrompt" 
            type="textarea" 
            :rows="3"
            placeholder="可选：添加特定的分析要求"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="startAnalysis"
            :loading="isAnalyzing"
            :disabled="!canStartAnalysis"
            size="large"
          >
            <el-icon><VideoPlay /></el-icon>
            {{ isAnalyzing ? '分析中...' : '🚀 开始分析' }}
          </el-button>
          
          <el-button 
            v-if="isAnalyzing" 
            @click="stopAnalysis"
            type="danger"
            size="large"
          >
            <el-icon><VideoPause /></el-icon>
            停止分析
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 进度显示 -->
    <el-card v-if="currentAnalysis" class="progress-panel" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>📊 分析进度</span>
          <el-tag :type="getStatusType(currentAnalysis.status)">
            {{ getStatusText(currentAnalysis.status) }}
          </el-tag>
        </div>
      </template>
      
      <AnalysisProgress 
        :analysis-id="currentAnalysis.id"
        :progress="currentAnalysis.progress"
        :status="currentAnalysis.status"
        :steps="currentAnalysis.steps"
        @progress-update="handleProgressUpdate"
      />
    </el-card>
    
    <!-- 结果显示 -->
    <el-card v-if="analysisResult" class="result-panel" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>📈 分析报告</span>
          <div>
            <el-button @click="exportReport('pdf')" type="primary" size="small">
              <el-icon><Download /></el-icon>
              导出PDF
            </el-button>
            <el-button @click="exportReport('word')" size="small">
              <el-icon><Document /></el-icon>
              导出Word
            </el-button>
          </div>
        </div>
      </template>
      
      <AnalysisResult :result="analysisResult" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay, VideoPause, Download, Document } from '@element-plus/icons-vue'
import { useAnalysisStore } from '@/stores/analysis'
import { useWebSocket } from '@/composables/useWebSocket'
import AnalysisProgress from '@/components/analysis/AnalysisProgress.vue'
import AnalysisResult from '@/components/analysis/AnalysisResult.vue'
import type { AnalysisForm, AnalysisData } from '@/types/analysis'

// 状态管理
const analysisStore = useAnalysisStore()
const { connect, disconnect, isConnected } = useWebSocket()

// 表单数据
const analysisForm = reactive<AnalysisForm>({
  marketType: 'A股',
  stockCode: '',
  researchDepth: 3,
  analysts: ['market', 'fundamentals'],
  customPrompt: ''
})

// 表单验证规则
const rules = {
  marketType: [{ required: true, message: '请选择市场类型', trigger: 'change' }],
  stockCode: [{ required: true, message: '请输入股票代码', trigger: 'blur' }],
  analysts: [{ required: true, message: '请选择至少一个分析师', trigger: 'change' }]
}

// 深度标记
const depthMarks = {
  1: '快速',
  2: '基础', 
  3: '标准',
  4: '深度',
  5: '全面'
}

// 响应式数据
const formRef = ref()
const isAnalyzing = ref(false)
const currentAnalysis = ref<AnalysisData | null>(null)
const analysisResult = ref(null)

// 计算属性
const canStartAnalysis = computed(() => {
  return analysisForm.stockCode && analysisForm.analysts.length > 0 && !isAnalyzing.value
})

// 方法
const startAnalysis = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    isAnalyzing.value = true
    const response = await analysisStore.startAnalysis(analysisForm)
    
    currentAnalysis.value = {
      id: response.analysisId,
      status: 'running',
      progress: 0,
      steps: []
    }
    
    // 连接WebSocket监听进度
    connect(`/ws/analysis/${response.analysisId}`)
    
    ElMessage.success('分析已启动！')
    
  } catch (error) {
    ElMessage.error('启动分析失败：' + error.message)
    isAnalyzing.value = false
  }
}

const stopAnalysis = async () => {
  try {
    await ElMessageBox.confirm('确定要停止当前分析吗？', '确认停止', {
      type: 'warning'
    })
    
    if (currentAnalysis.value) {
      await analysisStore.stopAnalysis(currentAnalysis.value.id)
      isAnalyzing.value = false
      currentAnalysis.value = null
      disconnect()
      ElMessage.info('分析已停止')
    }
  } catch {
    // 用户取消
  }
}

const handleProgressUpdate = (data: any) => {
  if (currentAnalysis.value) {
    currentAnalysis.value.progress = data.progress
    currentAnalysis.value.status = data.status
    currentAnalysis.value.steps = data.steps
    
    if (data.status === 'completed') {
      isAnalyzing.value = false
      analysisResult.value = data.result
      ElMessage.success('分析完成！')
      disconnect()
    } else if (data.status === 'failed') {
      isAnalyzing.value = false
      ElMessage.error('分析失败：' + data.error)
      disconnect()
    }
  }
}

const exportReport = async (format: 'pdf' | 'word') => {
  if (!analysisResult.value) return
  
  try {
    const blob = await analysisStore.exportReport(currentAnalysis.value!.id, format)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `analysis_report_${currentAnalysis.value!.id}.${format}`
    a.click()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success(`${format.toUpperCase()}报告导出成功！`)
  } catch (error) {
    ElMessage.error('导出失败：' + error.message)
  }
}

const getStatusType = (status: string) => {
  const types = {
    running: 'primary',
    completed: 'success',
    failed: 'danger',
    stopped: 'warning'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts = {
    running: '分析中',
    completed: '已完成',
    failed: '失败',
    stopped: '已停止'
  }
  return texts[status] || '未知'
}

// 生命周期
onMounted(() => {
  // 恢复之前的分析状态
  analysisStore.loadCurrentAnalysis()
})

onUnmounted(() => {
  disconnect()
})
</script>

<style scoped>
.analysis-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.config-panel,
.progress-panel,
.result-panel {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-form {
  max-width: 800px;
}

.el-slider {
  margin: 20px 0;
}
</style>
