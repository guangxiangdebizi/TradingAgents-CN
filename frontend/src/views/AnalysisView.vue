<template>
  <div class="analysis-view">
    <el-row :gutter="24">
      <!-- 左侧：分析配置 -->
      <el-col :span="16">
        <div class="left-panel">
          <!-- 分析配置标题 -->
          <div class="section-header">
            <el-icon><Setting /></el-icon>
            <h2>分析配置</h2>
          </div>

          <!-- 分析配置表单 -->
          <div class="config-section">
            <el-card class="config-card">
              <template #header>
                <div class="card-title">
                  <el-icon><Document /></el-icon>
                  基础设置
                </div>
              </template>

              <div class="config-form-grid">
                <div class="form-column">
                  <el-form :model="analysisForm" label-width="80px" class="config-form">
                    <!-- 选择市场 -->
                    <el-form-item label="选择市场">
                      <div class="form-field-wrapper">
                        <el-select v-model="analysisForm.marketType" style="width: 200px;" size="small">
                          <el-option
                            v-for="type in marketTypes"
                            :key="type.value"
                            :label="type.label"
                            :value="type.value"
                          />
                        </el-select>
                        <el-tooltip content="选择要分析的股票市场" placement="right">
                          <el-icon class="field-info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                      </div>
                    </el-form-item>

                    <!-- 分析日期 -->
                    <el-form-item label="分析日期">
                      <div class="form-field-wrapper">
                        <el-date-picker
                          v-model="analysisForm.analysisDate"
                          type="date"
                          size="small"
                          style="width: 200px;"
                          :disabled-date="disabledDate"
                        />
                        <el-tooltip content="选择分析的基准日期" placement="right">
                          <el-icon class="field-info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                      </div>
                    </el-form-item>
                  </el-form>
                </div>

                <div class="form-column">
                  <el-form :model="analysisForm" label-width="80px" class="config-form">
                    <!-- 股票代码 -->
                    <el-form-item label="股票代码">
                      <div class="form-field-wrapper">
                        <el-input
                          v-model="analysisForm.stockCode"
                          style="width: 200px;"
                          size="small"
                          :placeholder="getStockPlaceholder()"
                        />
                        <el-tooltip :content="getStockHint()" placement="right">
                          <el-icon class="field-info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                      </div>
                    </el-form-item>

                    <!-- 研究深度 -->
                    <el-form-item label="研究深度">
                      <div class="slider-field-wrapper">
                        <div class="slider-container">
                          <el-slider
                            v-model="analysisForm.researchDepth"
                            :min="1"
                            :max="5"
                            :step="1"
                            :marks="depthMarks"
                            style="width: 200px;"
                            show-stops
                          />
                        </div>
                        <el-tooltip content="选择分析的深度级别，级别越高分析越详细但耗时更长" placement="right">
                          <el-icon class="field-info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                      </div>
                    </el-form-item>
                  </el-form>
                </div>
              </div>
            </el-card>

            <!-- 选择分析师团队 -->
            <el-card class="team-card">
              <template #header>
                <div class="card-title">
                  <el-icon><UserFilled /></el-icon>
                  选择分析师团队
                </div>
              </template>

              <div class="team-options">
                <div class="team-grid">
                  <div class="team-option-row">
                    <el-checkbox v-model="analysisForm.marketAnalyst" class="team-checkbox">
                      <el-icon><TrendCharts /></el-icon>
                      市场分析师
                    </el-checkbox>
                    <el-tooltip content="专注于技术分析、价格走势和市场趋势分析" placement="right">
                      <el-icon class="info-icon"><InfoFilled /></el-icon>
                    </el-tooltip>
                  </div>

                  <div class="team-option-row">
                    <el-checkbox v-model="analysisForm.socialAnalyst" class="team-checkbox">
                      <el-icon><ChatDotRound /></el-icon>
                      社交媒体分析师
                    </el-checkbox>
                    <el-tooltip content="分析社交媒体情绪、舆论热度和投资者情绪" placement="right">
                      <el-icon class="info-icon"><InfoFilled /></el-icon>
                    </el-tooltip>
                  </div>

                  <div class="team-option-row">
                    <el-checkbox v-model="analysisForm.newsAnalyst" class="team-checkbox">
                      <el-icon><Reading /></el-icon>
                      新闻分析师
                    </el-checkbox>
                    <el-tooltip content="收集和分析相关新闻、公告和行业动态" placement="right">
                      <el-icon class="info-icon"><InfoFilled /></el-icon>
                    </el-tooltip>
                  </div>

                  <div class="team-option-row">
                    <el-checkbox v-model="analysisForm.fundamentalAnalyst" class="team-checkbox">
                      <el-icon><DataBoard /></el-icon>
                      基本面分析师
                    </el-checkbox>
                    <el-tooltip content="分析财务数据、业绩指标和公司基本面" placement="right">
                      <el-icon class="info-icon"><InfoFilled /></el-icon>
                    </el-tooltip>
                  </div>
                </div>
              </div>

              <div class="team-summary" v-if="getSelectedAnalystsCount() > 0">
                已选择 {{ getSelectedAnalystsCount() }} 个分析师: {{ getSelectedAnalystsNames() }}
              </div>
              <div class="team-warning" v-else>
                请至少选择一个分析师
              </div>



              <!-- 高级选项 -->
              <el-collapse class="advanced-options">
                <el-collapse-item title="🔧 高级选项" name="advanced">
                  <div class="advanced-content">
                    <div class="advanced-options-grid">
                      <div class="advanced-option-item">
                        <el-checkbox v-model="analysisForm.includeSentiment">
                          包含情绪分析
                        </el-checkbox>
                        <el-tooltip content="分析市场情绪和投资者心理状态" placement="right">
                          <el-icon class="info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                      </div>
                      <div class="advanced-option-item">
                        <el-checkbox v-model="analysisForm.includeRiskAssessment">
                          包含风险评估
                        </el-checkbox>
                        <el-tooltip content="评估投资风险和潜在收益" placement="right">
                          <el-icon class="info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                      </div>
                    </div>
                    <div class="custom-prompt-section">
                      <div class="prompt-label">
                        自定义分析要求
                        <el-tooltip content="输入特定的分析要求或关注点" placement="right">
                          <el-icon class="info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                      </div>
                      <el-input
                        v-model="analysisForm.customPrompt"
                        type="textarea"
                        :rows="3"
                        placeholder="输入特定的分析要求或关注点..."
                        style="margin-top: 8px;"
                      />
                    </div>
                  </div>
                </el-collapse-item>
              </el-collapse>

              <!-- 输入状态提示 -->
              <div class="input-status">
                <div v-if="!analysisForm.stockCode" class="status-info">
                  💡 请在上方输入股票代码，输入完成后按回车键确认
                </div>
              </div>
            </el-card>

            <!-- AI模型配置卡片 -->
            <el-card class="config-card" shadow="hover">
              <template #header>
                <div class="card-title">
                  <el-icon><Cpu /></el-icon>
                  AI模型配置
                </div>
              </template>

              <div class="ai-config-grid">
                <div class="ai-config-row">
                  <div class="ai-config-item">
                    <div class="config-label">
                      LLM提供商
                      <el-tooltip content="选择AI大语言模型提供商" placement="right">
                        <el-icon class="info-icon"><InfoFilled /></el-icon>
                      </el-tooltip>
                    </div>
                    <el-select v-model="analysisForm.llmProvider" style="width: 100%;">
                      <el-option label="阿里百炼" value="dashscope" />
                      <el-option label="DeepSeek" value="deepseek" />
                      <el-option label="OpenAI" value="openai" />
                      <el-option label="Google Gemini" value="gemini" />
                    </el-select>
                  </div>
                  <div class="ai-config-item">
                    <div class="config-label">
                      模型版本
                      <el-tooltip content="选择具体的AI模型版本" placement="right">
                        <el-icon class="info-icon"><InfoFilled /></el-icon>
                      </el-tooltip>
                    </div>
                    <el-select v-model="analysisForm.modelVersion" style="width: 100%;">
                      <el-option label="Plus - 平衡" value="plus-balanced" />
                      <el-option label="Pro - 专业" value="pro" />
                      <el-option label="Max - 最强" value="max" />
                    </el-select>
                  </div>
                </div>
              </div>

              <!-- 高级设置 -->
              <el-collapse class="ai-advanced-options">
                <el-collapse-item title="⚙️ 高级设置" name="advanced">
                  <div class="ai-advanced-content">
                    <div class="ai-advanced-grid">
                      <div class="ai-advanced-item">
                        <el-checkbox v-model="analysisForm.enableMemory">
                          启用记忆功能
                        </el-checkbox>
                        <el-tooltip content="启用AI记忆功能，提升分析连续性" placement="right">
                          <el-icon class="info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                      </div>
                      <div class="ai-advanced-item">
                        <el-checkbox v-model="analysisForm.debugMode">
                          调试模式
                        </el-checkbox>
                        <el-tooltip content="启用调试模式，显示详细分析过程" placement="right">
                          <el-icon class="info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                      </div>
                    </div>
                    <div class="slider-section">
                      <div class="slider-label">
                        最大输出长度
                        <el-tooltip content="控制AI分析报告的最大长度" placement="right">
                          <el-icon class="info-icon"><InfoFilled /></el-icon>
                        </el-tooltip>
                      </div>
                      <el-slider
                        v-model="analysisForm.maxOutputLength"
                        :min="1000"
                        :max="8000"
                        :step="500"
                        show-input
                        style="width: 100%; margin-top: 8px;"
                      />
                    </div>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </el-card>

            <!-- 开始分析按钮 -->
            <div class="analysis-button-container">
              <el-button
                type="primary"
                size="large"
                @click="performAnalysis"
                :loading="loading"
                class="start-analysis-btn"
              >
                <el-icon><TrendCharts /></el-icon>
                开始分析
              </el-button>
            </div>

            <!-- 分析进度模块 -->
            <div v-if="showAnalysisProgress" class="analysis-progress-section">
              <el-card class="progress-card">
                <template #header>
                  <div class="progress-header">
                    <el-icon><TrendCharts /></el-icon>
                    <span>股票分析</span>
                  </div>
                </template>

                <!-- 分析进度 -->
                <el-card class="progress-detail-card" shadow="never">
                  <template #header>
                    <div class="progress-title">
                      <el-icon><TrendCharts /></el-icon>
                      <span>当前任务</span>
                      <el-icon><Loading /></el-icon>
                    </div>
                  </template>

                  <div class="progress-stats">
                    <div class="stat-item">
                      <div class="stat-label">当前步骤:</div>
                      <div class="current-step">
                        <el-icon><Setting /></el-icon>
                        <span>{{ currentStep || '准备中...' }}</span>
                      </div>
                    </div>
                  </div>

                  <div class="progress-metrics">
                    <div class="metric-item">
                      <div class="metric-label">进度</div>
                      <div class="metric-value">{{ progressPercentage || 0 }}%</div>
                    </div>
                    <div class="metric-item">
                      <div class="metric-label">已用时间</div>
                      <div class="metric-value">{{ elapsedTime || '0秒' }}</div>
                    </div>
                    <div class="metric-item">
                      <div class="metric-label">预计剩余</div>
                      <div class="metric-value">{{ estimatedRemaining || '计算中...' }}</div>
                    </div>
                  </div>

                  <el-progress
                    :percentage="progressPercentage || 0"
                    :stroke-width="8"
                    :show-text="false"
                    class="progress-bar"
                  />

                  <div class="current-task">
                    <div class="task-label">当前任务:</div>
                    <div class="task-description">{{ currentTask || '准备中...' }}</div>
                  </div>

                  <div class="current-status">
                    <el-icon><InfoFilled /></el-icon>
                    <span>当前状态: </span>
                    <el-icon><TrendCharts /></el-icon>
                    <span>{{ currentStatus || '准备中...' }}</span>
                  </div>

                  <div class="progress-controls">
                    <el-button v-if="!analysisResult" @click="refreshProgress" :loading="refreshing" size="small">
                      <el-icon><Loading /></el-icon>
                      刷新进度
                    </el-button>
                    <el-button v-if="analysisResult" @click="showAnalysisResult" type="primary" size="large">
                      <el-icon><Document /></el-icon>
                      查看分析报告
                    </el-button>
                    <div v-if="!analysisResult" class="auto-refresh">
                      <el-checkbox v-model="autoRefresh">
                        <el-icon><Loading /></el-icon>
                        自动刷新
                      </el-checkbox>
                    </div>
                  </div>
                </el-card>
              </el-card>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 右侧：使用指南 -->
      <el-col :span="8">
        <div class="right-panel">
          <div class="guide-section">
            <div class="guide-header">
              <el-icon><InfoFilled /></el-icon>
              <h3>使用指南</h3>
            </div>

            <el-collapse v-model="activeGuides" class="guide-collapse">
              <el-collapse-item title="🚀 快速开始" name="quickstart">
                <div class="guide-content">
                  <h4>📋 基本步骤</h4>
                  <ol class="guide-steps">
                    <li>选择股票市场类型（A股/美股/港股）</li>
                    <li>输入股票代码，输入完成后按回车键确认</li>
                    <li>选择分析师团队成员</li>
                    <li>配置AI模型参数</li>
                    <li>点击"开始分析"按钮</li>
                  </ol>
                </div>
              </el-collapse-item>

              <el-collapse-item title="📊 分析师团队说明" name="analysts">
                <div class="guide-content">
                  <div class="analyst-info">
                    <h4>🔍 实时数据：最新资讯和价格走势分析</h4>
                    <p>多维度分析：技术面、基本面、情绪面综合分析</p>
                  </div>
                </div>
              </el-collapse-item>

              <el-collapse-item title="🤖 AI模型说明" name="ai">
                <div class="guide-content">
                  <h4>🧠 智能分析</h4>
                  <p>启用记忆功能：提升分析连续性和准确性</p>
                  <p>调试模式：显示详细的分析过程和调试信息</p>
                  <p>最大输出长度：控制AI分析报告的最大字符数</p>
                </div>
              </el-collapse-item>

              <el-collapse-item title="❓ 常见问题" name="faq">
                <div class="guide-content">
                  <h4>💡 使用提示</h4>
                  <p>股票代码格式：A股使用6位数字，美股使用英文代码，港股使用5位数字</p>
                  <p>分析时间：根据选择的研究深度，分析时间约为1-5分钟</p>
                  <p>结果导出：分析完成后可导出为PDF、Word或Markdown格式</p>
                </div>
              </el-collapse-item>
            </el-collapse>

            <!-- 投资风险提示 -->
            <el-alert
              title="投资风险提示"
              type="warning"
              :closable="false"
              class="risk-alert"
            >
              <template #default>
                <ul class="risk-list">
                  <li>本系统提供的分析结果仅供参考，不构成投资建议</li>
                  <li>投资有风险，入市需谨慎，请理性投资</li>
                  <li>请结合多方信息做出投资决策</li>
                  <li>重大投资决策建议咨询专业投资顾问</li>
                  <li>AI分析存在局限性，市场变化复杂多变</li>
                </ul>
              </template>
            </el-alert>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 分析结果 -->
    <div v-if="analysisResult && !loading && showAnalysisReport" class="analysis-result">
      <!-- 第一部分：分析报告摘要 -->
      <div class="analysis-summary">
        <div class="summary-header">
          <el-icon><Document /></el-icon>
          <h2>分析报告</h2>
        </div>

        <el-card class="summary-card">
          <div class="stock-title">
            <el-icon><TrendCharts /></el-icon>
            <h3>{{ analysisResult.stockCode }} 分析结果</h3>
          </div>

          <!-- 投资决策摘要 -->
          <div class="decision-summary">
            <div class="decision-header">
              <el-icon><Aim /></el-icon>
              <h4>投资决策摘要</h4>
            </div>

            <div class="decision-metrics">
              <div class="metric-item">
                <div class="metric-label">
                  投资建议
                  <el-tooltip content="基于AI分析的投资建议" placement="top">
                    <el-icon class="info-icon"><InfoFilled /></el-icon>
                  </el-tooltip>
                </div>
                <div class="metric-value recommendation">
                  {{ analysisResult.recommendation || '持有' }}
                </div>
                <div class="metric-change positive">
                  <el-icon><ArrowUp /></el-icon>
                  {{ analysisResult.recommendationChange || '20.0%' }}
                </div>
              </div>

              <div class="metric-item">
                <div class="metric-label">
                  置信度
                  <el-tooltip content="AI对分析结果的置信程度" placement="top">
                    <el-icon class="info-icon"><InfoFilled /></el-icon>
                  </el-tooltip>
                </div>
                <div class="metric-value confidence">
                  {{ analysisResult.confidence || '70.0%' }}
                </div>
                <div class="metric-change positive">
                  <el-icon><ArrowUp /></el-icon>
                  {{ analysisResult.confidenceChange || '20.0%' }}
                </div>
              </div>

              <div class="metric-item">
                <div class="metric-label">
                  风险评分
                  <el-tooltip content="投资风险评估分数" placement="top">
                    <el-icon class="info-icon"><InfoFilled /></el-icon>
                  </el-tooltip>
                </div>
                <div class="metric-value risk">
                  {{ analysisResult.riskScore || '50.0%' }}
                </div>
                <div class="metric-change negative">
                  <el-icon><ArrowUp /></el-icon>
                  {{ analysisResult.riskChange || '20.0%' }}
                </div>
              </div>

              <div class="metric-item">
                <div class="metric-label">
                  目标价位
                  <el-tooltip content="预期目标价格" placement="top">
                    <el-icon class="info-icon"><InfoFilled /></el-icon>
                  </el-tooltip>
                </div>
                <div class="metric-value target-price">
                  ¥{{ analysisResult.targetPrice || '135.00' }}
                </div>
              </div>
            </div>

            <!-- AI分析推理 -->
            <div class="ai-reasoning">
              <div class="reasoning-header">
                <el-icon><ChatDotRound /></el-icon>
                <span>AI分析推理</span>
                <el-button text @click="toggleReasoning">
                  <el-icon><ArrowDown v-if="!showReasoning" /><ArrowUp v-else /></el-icon>
                </el-button>
              </div>
              <el-collapse-transition>
                <div v-show="showReasoning" class="reasoning-content">
                  {{ analysisResult.reasoning || '五粮液基本面稳健但缺乏催化剂，技术面偏弱，市场情绪谨慎，当前股价处于合理估值区间但不足以支撑立即买入。' }}
                </div>
              </el-collapse-transition>
            </div>

            <!-- 分析配置信息 -->
            <div class="config-info">
              <div class="config-header">
                <el-icon><Setting /></el-icon>
                <span>分析配置信息</span>
                <el-button text @click="toggleConfigInfo">
                  <el-icon><ArrowDown v-if="!showConfigInfo" /><ArrowUp v-else /></el-icon>
                </el-button>
              </div>
              <el-collapse-transition>
                <div v-show="showConfigInfo" class="config-content">
                  <div class="config-item">
                    <span class="config-label">分析日期:</span>
                    <span class="config-value">{{ formatDate(analysisForm.analysisDate) }}</span>
                  </div>
                  <div class="config-item">
                    <span class="config-label">选择的分析师:</span>
                    <span class="config-value">{{ getSelectedAnalystsNames() }}</span>
                  </div>
                  <div class="config-item">
                    <span class="config-label">研究深度:</span>
                    <span class="config-value">{{ analysisForm.researchDepth }}级</span>
                  </div>
                  <div class="config-item">
                    <span class="config-label">AI模型:</span>
                    <span class="config-value">{{ analysisForm.llmProvider }}</span>
                  </div>
                </div>
              </el-collapse-transition>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 第二部分：详细分析报告 -->
      <div class="detailed-analysis">
        <div class="detailed-header">
          <el-icon><Document /></el-icon>
          <h2>详细分析报告</h2>
        </div>

        <el-card class="detailed-card">
          <!-- 分析标签页 -->
          <el-tabs v-model="activeAnalysisTab" class="analysis-tabs">
            <el-tab-pane label="📈 市场技术分析" name="technical">
              <div class="analysis-section">
                <h3>{{ analysisResult.stockCode }}（{{ analysisResult.stockName }}）技术分析报告</h3>
                <div class="section-content">
                  <h4>一、价格趋势分析</h4>
                  <p>{{ analysisResult.technicalAnalysis || '根据2025年7月10日至2025年7月20日的交易数据，000858（五粮液）的价格整体呈现震荡下行的趋势。从期间最高价126.11元到最低价117.10元，波动幅度为7.01元，显示出市场情绪较为谨慎。' }}</p>

                  <h4>二、技术指标解读</h4>
                  <p>{{ analysisResult.technicalIndicators || '从趋势线来看，000858在短期内处于一个横盘整理的状态，但整体趋势偏弱，尤其是在7月18日后，价格持续承压，表明市场存在一定的抛压。' }}</p>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="🔥 基本面分析" name="fundamental">
              <div class="analysis-section">
                <div class="section-content">
                  <p>{{ analysisResult.fundamentalAnalysis || '基本面分析内容将在这里显示...' }}</p>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="💭 市场情绪分析" name="sentiment">
              <div class="analysis-section">
                <div class="section-content">
                  <p>{{ analysisResult.sentimentAnalysis || '市场情绪分析内容将在这里显示...' }}</p>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="📰 新闻事件分析" name="news">
              <div class="analysis-section">
                <div class="section-content">
                  <p>{{ analysisResult.newsAnalysis || '新闻事件分析内容将在这里显示...' }}</p>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="⚠️ 风险评估" name="risk">
              <div class="analysis-section">
                <div class="section-content">
                  <p>{{ analysisResult.riskAnalysis || '风险评估内容将在这里显示...' }}</p>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="💡 投资建议" name="recommendation">
              <div class="analysis-section">
                <div class="section-content">
                  <p>{{ analysisResult.investmentAdvice || '投资建议内容将在这里显示...' }}</p>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-section">
      <el-card>
        <div class="loading-content">
          <el-icon class="loading-icon"><Loading /></el-icon>
          <h3>正在分析中...</h3>
          <p>AI 正在为您分析 {{ analysisForm.stockCode }}，请稍候</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import {
  Setting,
  Document,
  UserFilled,
  TrendCharts,
  ChatDotRound,
  Reading,
  DataBoard,
  InfoFilled,
  Loading,
  Cpu,
  Aim,
  ArrowUp,
  ArrowDown
} from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const analysisResult = ref(null)
const showAnalysisProgress = ref(false)
const showReasoning = ref(true)
const showConfigInfo = ref(false)
const activeAnalysisTab = ref('technical')
const showAnalysisReport = ref(false)
const autoRefresh = ref(false)
const refreshing = ref(false)
const refreshTimer = ref(null)

// 分析进度数据
const analysisId = ref('')
const progressPercentage = ref(0)
const currentStep = ref('初始化AI分析引擎，准备开始分析')
const currentTask = ref('初始化AI分析引擎，准备开始分析')
const currentStatus = ref('📊 开始分析 000858 股票，这可能需要几分钟时间...')
const elapsedTime = ref('0秒')
const estimatedRemaining = ref('计算中...')
const startTime = ref(null)



const analysisForm = ref({
  marketType: 'A股',
  stockCode: '000858',
  analysisDate: new Date(),
  researchDepth: 3,
  marketAnalyst: true,
  socialAnalyst: false,
  newsAnalyst: false,
  fundamentalAnalyst: true,
  // AI模型配置
  llmProvider: 'dashscope',
  modelVersion: 'plus-balanced',
  enableMemory: true,
  debugMode: false,
  maxOutputLength: 4000,
  // 专业设置
  includeSentiment: true,
  includeRiskAssessment: true,
  customPrompt: ''
})

// 选项数据
const marketTypes = [
  { label: 'A股', value: 'A股' },
  { label: '美股', value: '美股' },
  { label: '港股', value: '港股' }
]

const researchDepths = [
  { label: '1级 - 快速分析', value: 1 },
  { label: '2级 - 基础分析', value: 2 },
  { label: '3级 - 标准分析', value: 3 },
  { label: '4级 - 深度分析', value: 4 },
  { label: '5级 - 全面分析', value: 5 }
]

// 滑块标记
const depthMarks = {
  1: '快速',
  2: '基础',
  3: '标准',
  4: '深度',
  5: '全面'
}

const activeGuides = ref(['quickstart'])

// 计算属性
const canStartAnalysis = computed(() => {
  return analysisForm.value.stockCode && getSelectedAnalystsCount() > 0
})

// 方法
const getStockPlaceholder = () => {
  const placeholders = {
    'A股': '输入A股代码，如 000001, 600519，然后按回车确认',
    '美股': '输入美股代码，如 AAPL, TSLA, MSFT，然后按回车确认',
    '港股': '输入港股代码，如 0700.HK, 9988.HK, 3690.HK，然后按回车确认'
  }
  return placeholders[analysisForm.value.marketType] || placeholders['A股']
}

const getStockHint = () => {
  const hints = {
    'A股': '输入要分析的A股代码，如 000001(平安银行), 600519(贵州茅台)，输入完成后请按回车键确认',
    '美股': '输入要分析的美股代码，输入完成后请按回车键确认',
    '港股': '输入要分析的港股代码，如 0700.HK(腾讯控股), 9988.HK(阿里巴巴), 3690.HK(美团)，输入完成后请按回车键确认'
  }
  return hints[analysisForm.value.marketType] || hints['A股']
}

const disabledDate = (time) => {
  return time.getTime() > Date.now()
}

const getSelectedAnalystsCount = () => {
  let count = 0
  if (analysisForm.value.marketAnalyst) count++
  if (analysisForm.value.socialAnalyst) count++
  if (analysisForm.value.newsAnalyst) count++
  if (analysisForm.value.fundamentalAnalyst) count++
  return count
}

const getSelectedAnalystsNames = () => {
  const names = []
  if (analysisForm.value.marketAnalyst) names.push('市场分析师')
  if (analysisForm.value.socialAnalyst) names.push('社交媒体分析师')
  if (analysisForm.value.newsAnalyst) names.push('新闻分析师')
  if (analysisForm.value.fundamentalAnalyst) names.push('基本面分析师')
  return names.join(', ')
}

// 切换AI分析推理显示
const toggleReasoning = () => {
  showReasoning.value = !showReasoning.value
}

// 切换配置信息显示
const toggleConfigInfo = () => {
  showConfigInfo.value = !showConfigInfo.value
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

// 显示分析报告
const showAnalysisResult = () => {
  showAnalysisReport.value = true
  showAnalysisProgress.value = false
}

// 刷新进度
const refreshProgress = async () => {
  refreshing.value = true
  try {
    // 模拟获取进度数据
    await new Promise(resolve => setTimeout(resolve, 500))

    // 更新进度数据（这里应该调用实际的API）
    progressPercentage.value = Math.min(progressPercentage.value + Math.random() * 10, 100)

    if (startTime.value) {
      const elapsed = Math.floor((Date.now() - startTime.value) / 1000)
      elapsedTime.value = formatTime(elapsed)

      if (progressPercentage.value > 0) {
        const totalEstimated = (elapsed / progressPercentage.value) * 100
        const remaining = Math.max(0, totalEstimated - elapsed)
        estimatedRemaining.value = formatTime(remaining)
      }
    }

    // 更新当前步骤和状态
    const steps = [
      '初始化AI分析引擎',
      '获取股票基础数据',
      '分析技术指标',
      '分析基本面数据',
      '生成分析报告'
    ]
    const currentStepIndex = Math.floor(progressPercentage.value / 20)
    if (currentStepIndex < steps.length) {
      currentStep.value = steps[currentStepIndex]
    }

  } catch (error) {
    console.error('刷新进度失败:', error)
  } finally {
    refreshing.value = false
  }
}

// 格式化时间
const formatTime = (seconds) => {
  if (seconds < 60) {
    return `${seconds}秒`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}分${remainingSeconds}秒`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}小时${minutes}分钟`
  }
}

const performAnalysis = async () => {
  if (!canStartAnalysis.value) {
    return
  }

  // 初始化分析进度
  showAnalysisProgress.value = true
  showAnalysisReport.value = false
  loading.value = true
  analysisResult.value = null

  // 生成分析ID
  const now = new Date()
  const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '')
  const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, '')
  analysisId.value = `analysis_${Math.random().toString(36).substring(2, 8)}_${dateStr}_${timeStr}`

  // 重置进度数据
  progressPercentage.value = 0
  startTime.value = Date.now()
  currentStep.value = '初始化AI分析引擎，准备开始分析'
  currentTask.value = '初始化AI分析引擎，准备开始分析'
  currentStatus.value = `📊 开始分析 ${analysisForm.value.stockCode} 股票，这可能需要几分钟时间...`

  try {
    // 模拟分析过程
    await new Promise(resolve => setTimeout(resolve, 3000))

    // 模拟分析结果
    analysisResult.value = {
      stockCode: analysisForm.value.stockCode,
      stockName: '五粮液',
      currentPrice: '123.78',
      change: '+2.15',
      changePercent: '+1.77%',
      recommendation: '持有',
      confidence: '70.0%',
      riskScore: '50.0%',
      targetPrice: '135.00',
      recommendationChange: '20.0%',
      confidenceChange: '20.0%',
      riskChange: '20.0%',
      reasoning: '五粮液基本面稳健但缺乏催化剂，技术面偏弱，市场情绪谨慎，当前股价处于合理估值区间但不足以支撑立即买入。',
      technicalAnalysis: '根据2025年7月10日至2025年7月20日的交易数据，000858（五粮液）的价格整体呈现震荡下行的趋势。从期间最高价126.11元到最低价117.10元，波动幅度为7.01元，显示出市场情绪较为谨慎。具体来看：\n\n• 2025-07-10：开盘价为123.40元，收盘价为123.78元，小幅上涨。\n• 2025-07-14：价格达到125.41元，是期间内的高点。\n• 2025-07-18：价格下跌至123.78元，接近前期低点。\n• 2025-07-20：价格维持在123.78元附近，未出现明显反弹。',
      technicalIndicators: '从趋势线来看，000858在短期内处于一个横盘整理的状态，但整体趋势偏弱，尤其是在7月18日后，价格持续承压，表明市场存在一定的抛压。',
      fundamentalAnalysis: '五粮液作为白酒行业龙头企业，基本面相对稳健。公司拥有深厚的品牌底蕴和稳定的市场地位，但在当前经济环境下，消费升级趋势放缓，高端白酒市场竞争加剧。',
      sentimentAnalysis: '市场情绪方面，投资者对白酒板块整体保持谨慎态度。近期缺乏明显的催化剂事件，机构投资者持仓相对稳定，但新增资金流入有限。',
      newsAnalysis: '近期五粮液相关新闻主要集中在产品创新和渠道拓展方面，但缺乏重大利好消息。行业政策环境相对稳定，未出现明显的负面影响。',
      riskAnalysis: '主要风险包括：1）消费需求疲软风险；2）行业竞争加剧风险；3）原材料成本上涨风险；4）政策调控风险。建议投资者关注公司业绩变化和行业发展趋势。',
      investmentAdvice: '综合考虑技术面、基本面和市场情绪，建议对五粮液采取"持有"策略。短期内股价可能继续震荡，但长期来看，公司基本面支撑股价稳定。建议投资者耐心等待更好的买入时机。'
    }

    // 完成分析
    progressPercentage.value = 100
    currentStep.value = '分析完成'
    currentTask.value = '分析完成'
    currentStatus.value = '✅ 分析成功完成！'

  } catch (error) {
    console.error('分析失败:', error)
    currentStatus.value = '❌ 分析失败，请重试'
  } finally {
    loading.value = false
    // 注意：不隐藏showAnalysisProgress，保持进度模块显示
  }
}

// 监听自动刷新状态
watch(autoRefresh, (newValue) => {
  if (newValue && showAnalysisProgress.value && loading.value) {
    // 开始自动刷新
    refreshTimer.value = setInterval(() => {
      if (showAnalysisProgress.value && loading.value) {
        refreshProgress()
      } else {
        // 停止自动刷新
        if (refreshTimer.value) {
          clearInterval(refreshTimer.value)
          refreshTimer.value = null
        }
      }
    }, 5000) // 每5秒刷新一次
  } else {
    // 停止自动刷新
    if (refreshTimer.value) {
      clearInterval(refreshTimer.value)
      refreshTimer.value = null
    }
  }
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
})
</script>

<style scoped>
.analysis-view {
  padding: 20px;
  background-color: #fafafa;
  min-height: 100vh;
}

/* 左侧面板 */
.left-panel {
  padding-right: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  color: #262730;
  font-size: 26px;
  font-weight: 600;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.config-card, .team-card {
  background: white;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  box-shadow: none;
}

.config-card :deep(.el-card__body),
.team-card :deep(.el-card__body) {
  padding: 16px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #262730;
  font-size: 18px;
}

.config-form {
  padding: 0;
}

.config-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.form-column {
  display: flex;
  flex-direction: column;
}

.config-form .el-form-item {
  margin-bottom: 16px;
}

.config-form .el-form-item__label {
  color: #262730;
  font-weight: 500;
  font-size: 15px;
}

.form-field-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.slider-field-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.slider-container {
  display: flex;
  align-items: center;
  width: 200px;
}

.field-info-icon {
  color: #8b949e;
  cursor: help;
  font-size: 16px;
}

.form-hint {
  margin-top: 2px;
  font-size: 12px;
  color: #8b949e;
  margin-left: 0;
  line-height: 1.4;
}

.team-options {
  margin-bottom: 12px;
}

.team-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 16px;
}

.team-option-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 2px 0;
}

.team-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  color: #262730;
}

.team-checkbox :deep(.el-checkbox__label) {
  color: #262730;
  font-weight: 500;
}

.info-icon {
  color: #8b949e;
  cursor: help;
  font-size: 16px;
}

.team-summary {
  background: #e8f5e8;
  padding: 10px;
  border-radius: 6px;
  font-size: 14px;
  color: #0d7377;
  margin-bottom: 12px;
  border-left: 4px solid #28a745;
}

.team-warning {
  background: #fff3cd;
  padding: 10px;
  border-radius: 6px;
  font-size: 14px;
  color: #856404;
  margin-bottom: 12px;
  border-left: 4px solid #ffc107;
}

.input-status {
  margin: 16px 0;
}

.status-info {
  background: #e3f2fd;
  padding: 12px;
  border-radius: 6px;
  font-size: 15px;
  color: #1976d2;
  border-left: 4px solid #2196f3;
}

.status-success {
  background: #e8f5e8;
  padding: 12px;
  border-radius: 6px;
  font-size: 15px;
  color: #0d7377;
  border-left: 4px solid #28a745;
}

.advanced-options {
  margin-bottom: 16px;
}

.advanced-options :deep(.el-collapse-item__header) {
  background: transparent;
  border: none;
  color: #262730;
  font-size: 15px;
}

/* AI模型配置 */
.ai-model-config {
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #262730;
  margin-bottom: 16px;
}

.model-config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

/* 专业设置 */
.professional-settings {
  margin-bottom: 20px;
}

.professional-content {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.slider-setting {
  width: 100%;
}

.slider-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
}

.advanced-options {
  margin-top: 20px;
}

.advanced-content {
  padding: 8px 0;
}

.advanced-options-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 16px;
  margin-bottom: 16px;
}

.advanced-option-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 2px 0;
}

.custom-prompt-section {
  margin-top: 16px;
}

.prompt-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
}

/* AI模型配置样式 */
.ai-config-grid {
  margin-bottom: 20px;
}

.ai-config-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 16px;
}

.ai-config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.ai-advanced-options {
  margin-top: 20px;
}

.ai-advanced-content {
  padding: 8px 0;
}

.ai-advanced-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 16px;
  margin-bottom: 16px;
}

.ai-advanced-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 2px 0;
}

.slider-section {
  margin-top: 16px;
}

.slider-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
}

.analysis-button-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.start-analysis-btn {
  height: 56px;
  font-size: 18px;
  font-weight: 600;
  padding: 0 80px;
  border-radius: 8px;
  background: #ff4b4b;
  border-color: #ff4b4b;
  min-width: 280px;
}

.start-analysis-btn:hover {
  background: #ff6b6b;
  border-color: #ff6b6b;
}

/* 右侧面板 */
.right-panel {
  padding-left: 20px;
}

.guide-section {
  position: sticky;
  top: 20px;
}

.guide-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  background: #e3f2fd;
  padding: 12px;
  border-radius: 8px;
}

.guide-header h3 {
  margin: 0;
  color: #1976d2;
  font-size: 18px;
  font-weight: 600;
}

.guide-collapse {
  margin-bottom: 20px;
  background: white;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
}

.guide-collapse :deep(.el-collapse-item__header) {
  background: transparent;
  border: none;
  color: #262730;
  font-size: 15px;
  padding: 12px 16px;
}

.guide-collapse :deep(.el-collapse-item__content) {
  padding: 0 16px 12px 16px;
}

.guide-content {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #8b949e;
  line-height: 1.6;
  font-size: 15px;
}

.risk-alert {
  margin-top: 20px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
}

.risk-alert :deep(.el-alert__title) {
  color: #856404;
  font-weight: 600;
  font-size: 16px;
}

.risk-list {
  margin: 8px 0 0 0;
  padding-left: 16px;
  color: #856404;
}

.risk-list li {
  margin-bottom: 6px;
  font-size: 14px;
  line-height: 1.5;
}

/* 分析进度模块 */
.analysis-progress-section {
  margin-top: 24px;
}

.progress-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.analysis-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 0;
  font-size: 14px;
  color: #606266;
  background: #f5f7fa;
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 16px;
}

.progress-detail-card {
  border: none;
  background: #fafbfc;
}

.progress-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #409eff;
}

.progress-stats {
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.current-step {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #409eff;
  font-weight: 500;
}

.progress-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.metric-item {
  text-align: center;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.progress-bar {
  margin: 16px 0;
}

.current-task {
  margin: 16px 0;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.task-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.task-description {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.current-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px;
  background: #e8f4fd;
  border-radius: 6px;
  border: 1px solid #b3d8ff;
  margin: 16px 0;
  font-size: 14px;
  color: #409eff;
}

.progress-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.auto-refresh {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 分析结果 */
.analysis-result {
  margin-top: 24px;
}

.result-card {
  background: white;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  box-shadow: none;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-header h3 {
  margin: 0;
  color: #262730;
  font-size: 18px;
  font-weight: 600;
}

.stock-info {
  margin-bottom: 20px;
}

.price-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.current-price {
  font-size: 24px;
  font-weight: 700;
  color: #262730;
}

.price-change.positive {
  color: #28a745;
  font-weight: 600;
}

.recommendation {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.confidence {
  font-size: 16px;
  color: #8b949e;
}

.analysis-details {
  margin-top: 20px;
}

.detail-card {
  height: 200px;
  background: white;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  box-shadow: none;
}

.detail-card :deep(.el-card__header) {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f8f9fa;
  color: #262730;
  font-weight: 600;
}

/* 加载状态 */
.loading-section {
  margin-top: 24px;
}

.loading-content {
  text-align: center;
  padding: 40px;
  background: white;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
}

.loading-icon {
  font-size: 32px;
  color: #ff4b4b;
  margin-bottom: 16px;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-content h3 {
  margin: 0 0 8px 0;
  color: #262730;
  font-size: 18px;
}

.loading-content p {
  margin: 0;
  color: #8b949e;
}

/* 指南内容样式 */
.guide-section-content {
  font-size: 15px;
  line-height: 1.6;
}

.guide-section-content h4 {
  color: #262730;
  font-size: 17px;
  font-weight: 600;
  margin: 16px 0 8px 0;
}

.guide-section-content ol,
.guide-section-content ul {
  margin: 8px 0;
  padding-left: 20px;
}

.guide-section-content li {
  margin-bottom: 8px;
}

.guide-section-content code {
  background: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.warning-note {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  padding: 8px;
  margin: 8px 0;
  color: #856404;
  font-size: 14px;
}

.tip-note {
  background: #e3f2fd;
  border: 1px solid #bbdefb;
  border-radius: 4px;
  padding: 8px;
  margin: 8px 0;
  color: #1976d2;
  font-size: 14px;
}

.faq-item {
  margin-bottom: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #dee2e6;
}

.faq-item strong {
  color: #262730;
}

/* 分析报告样式 */
.analysis-result {
  margin-top: 24px;
}

.analysis-summary {
  margin-bottom: 24px;
}

.summary-header,
.detailed-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.summary-header h2,
.detailed-header h2 {
  margin: 0;
  color: #262730;
  font-size: 24px;
  font-weight: 600;
}

.stock-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.stock-title h3 {
  margin: 0;
  color: #262730;
  font-size: 20px;
  font-weight: 600;
}

.decision-summary {
  margin-top: 16px;
}

.decision-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.decision-header h4 {
  margin: 0;
  color: #262730;
  font-size: 18px;
  font-weight: 600;
}

.decision-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.metric-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.metric-label {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 14px;
  color: #8b949e;
  margin-bottom: 8px;
}

.info-icon {
  font-size: 12px;
  color: #8b949e;
}

.metric-value {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 4px;
}

.metric-value.recommendation {
  color: #f56c6c;
}

.metric-value.confidence {
  color: #67c23a;
}

.metric-value.risk {
  color: #e6a23c;
}

.metric-value.target-price {
  color: #409eff;
}

.metric-change {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  font-size: 12px;
  font-weight: 500;
}

.metric-change.positive {
  color: #67c23a;
}

.metric-change.negative {
  color: #f56c6c;
}

.ai-reasoning,
.config-info {
  margin-top: 24px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.reasoning-header,
.config-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  cursor: pointer;
}

.reasoning-header span,
.config-header span {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #262730;
}

.reasoning-content,
.config-content {
  padding: 16px;
  background: white;
}

.reasoning-content {
  line-height: 1.6;
  color: #262730;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.config-item:last-child {
  border-bottom: none;
}

.config-label {
  font-weight: 500;
  color: #8b949e;
}

.config-value {
  color: #262730;
}

.detailed-analysis {
  margin-top: 24px;
}

.analysis-tabs {
  margin-top: 16px;
}

.analysis-section h3 {
  color: #262730;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
}

.analysis-section h4 {
  color: #262730;
  font-size: 16px;
  font-weight: 600;
  margin: 16px 0 8px 0;
}

.section-content {
  line-height: 1.6;
  color: #262730;
}

.section-content p {
  margin-bottom: 16px;
}

/* 分析进度模块 */
.analysis-progress-section {
  margin-top: 24px;
}

.progress-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #262730;
}

.progress-detail-card {
  margin-top: 16px;
  background: #f8f9fa;
}

.progress-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #262730;
}

.progress-stats {
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.stat-label {
  font-weight: 500;
  color: #8b949e;
}

.current-step {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #262730;
}

.progress-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.metric-item {
  text-align: center;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.metric-label {
  font-size: 12px;
  color: #8b949e;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #262730;
}

.progress-bar {
  margin: 16px 0;
}

.current-task {
  margin: 16px 0;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.task-label {
  font-weight: 500;
  color: #8b949e;
  margin-bottom: 4px;
}

.task-description {
  color: #262730;
}

.current-status {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 16px 0;
  padding: 12px;
  background: #e3f2fd;
  border-radius: 6px;
  color: #1976d2;
}

.progress-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px;
}

.auto-refresh {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
