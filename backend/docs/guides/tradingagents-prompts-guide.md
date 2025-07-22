# 🎯 TradingAgents专业提示词使用指南

## 📍 **概述**

基于对TradingAgents原始代码的深入分析，我们为LLM Service创建了一套专业的股票分析提示词模板。这些模板完全复刻了TradingAgents中各个分析师模块的专业能力和分析框架。

## 🏗️ **提示词模板架构**

### **📊 分析师角色体系**

```
TradingAgents提示词体系
├── 📈 基本面分析师 (fundamentals_analyst)
├── 📊 技术分析师 (market_analyst)  
├── 🚀 看涨研究员 (bull_researcher)
├── 📉 看跌研究员 (bear_researcher)
├── 🛡️ 风险管理师 (risk_manager)
└── 👔 研究主管 (research_manager)
```

### **🎯 任务类型映射**

| 任务类型 | 模板ID | 专业领域 |
|----------|--------|----------|
| `fundamentals_analysis` | `tradingagents_fundamentals_analyst_zh` | 基本面分析 |
| `technical_analysis` | `tradingagents_market_analyst_zh` | 技术面分析 |
| `bull_analysis` | `tradingagents_bull_researcher_zh` | 看涨研究 |
| `bear_analysis` | `tradingagents_bear_researcher_zh` | 看跌研究 |
| `risk_management` | `tradingagents_risk_manager_zh` | 风险管理 |
| `research_management` | `tradingagents_research_manager_zh` | 综合决策 |

## 📊 **基本面分析师**

### **核心能力**
- 🔍 **财务分析**：深入分析财务报表，评估盈利能力、偿债能力、营运能力
- 💰 **估值分析**：运用DCF、P/E、P/B、PEG等多种估值方法
- 🏭 **行业分析**：分析行业发展趋势、竞争格局、政策影响
- 🎯 **投资建议**：提供明确的买入/持有/卖出建议和目标价位

### **使用示例**
```http
POST /api/v1/chat/completions
{
  "model": "deepseek-chat",
  "task_type": "fundamentals_analysis",
  "messages": [
    {"role": "user", "content": "请分析五粮液(000858)的投资价值"}
  ]
}
```

### **输出特点**
- ✅ 强制要求调用工具获取真实数据
- 📊 提供详细的财务指标分析
- 💰 包含具体的估值计算过程
- 🎯 明确的投资建议和目标价位

## 📈 **技术分析师**

### **核心能力**
- 📊 **趋势分析**：识别主要趋势、次要趋势和短期波动
- 🔍 **技术指标**：MACD、RSI、KDJ、BOLL等指标分析
- 📏 **支撑阻力**：确定关键的支撑位和阻力位
- 📊 **成交量分析**：分析量价关系和资金流向

### **使用示例**
```http
POST /api/v1/chat/completions
{
  "model": "deepseek-chat",
  "task_type": "technical_analysis",
  "messages": [
    {"role": "user", "content": "请对苹果公司(AAPL)进行技术分析"}
  ]
}
```

### **输出特点**
- 📈 完整的技术指标分析
- 🎯 具体的买卖点位建议
- 📊 详细的图表形态分析
- ⚠️ 风险控制和止损建议

## 🚀 **看涨研究员**

### **核心能力**
- 📈 **增长潜力**：突出市场机会、收入预测和可扩展性
- 🏆 **竞争优势**：强调独特产品、品牌价值、市场地位
- 📊 **积极指标**：挖掘财务健康、行业趋势、积极消息
- 🎯 **反驳看跌**：用数据和逻辑反驳看跌观点

### **使用示例**
```http
POST /api/v1/chat/completions
{
  "model": "deepseek-chat",
  "task_type": "bull_analysis",
  "messages": [
    {"role": "user", "content": "请为特斯拉(TSLA)构建看涨投资案例"}
  ]
}
```

### **输出特点**
- 🚀 强有力的看涨论证
- 📊 基于数据的增长分析
- 🏆 竞争优势深度挖掘
- 💡 具体的投资建议和催化剂

## 📉 **看跌研究员**

### **核心能力**
- ⚠️ **风险识别**：深入分析各种风险和挑战
- 💰 **估值质疑**：质疑当前估值的合理性
- 🏭 **竞争威胁**：识别竞争加剧、市场份额流失风险
- 📉 **财务风险**：分析财务恶化、盈利下降可能性

### **使用示例**
```http
POST /api/v1/chat/completions
{
  "model": "deepseek-chat",
  "task_type": "bear_analysis",
  "messages": [
    {"role": "user", "content": "请为比亚迪(002594)分析投资风险"}
  ]
}
```

### **输出特点**
- ⚠️ 全面的风险识别
- 💰 估值过高的证据
- 📉 谨慎的投资建议
- 🎯 具体的风险催化剂

## 🛡️ **风险管理师**

### **核心能力**
- 🔍 **风险识别**：系统性风险和非系统性风险
- 📊 **风险评估**：量化分析风险概率和影响
- 🛡️ **风险控制**：仓位管理、止损策略、对冲方案
- 📈 **压力测试**：极端情况下的表现分析

### **使用示例**
```http
POST /api/v1/chat/completions
{
  "model": "deepseek-chat",
  "task_type": "risk_management",
  "messages": [
    {"role": "user", "content": "请对茅台(600519)进行风险管理分析"}
  ]
}
```

### **输出特点**
- 📊 量化的风险指标
- 🛡️ 具体的风险控制措施
- 📈 压力测试和情景分析
- 🎯 明确的仓位建议

## 👔 **研究主管**

### **核心能力**
- 🔄 **研究整合**：整合各分析师的研究成果
- ⚖️ **观点平衡**：平衡看涨和看跌观点
- 🎯 **决策制定**：基于综合分析做出最终建议
- 📊 **质量控制**：确保分析的逻辑性和准确性

### **使用示例**
```http
POST /api/v1/chat/completions
{
  "model": "deepseek-chat",
  "task_type": "research_management",
  "messages": [
    {"role": "user", "content": "请综合分析宁德时代(300750)并做出最终投资决策"}
  ]
}
```

### **输出特点**
- 🎯 明确的最终投资建议
- ⚖️ 平衡的观点权重分配
- 📊 详细的情景分析
- 🛡️ 完整的风险控制策略

## 🔧 **使用最佳实践**

### **1. 模型选择建议**
```yaml
# 推荐模型配置
DeepSeek: 中文理解强，适合A股分析
OpenAI GPT-4: 逻辑推理强，适合复杂分析
阿里百炼: 本土化好，适合中国市场
```

### **2. 参数优化**
```json
{
  "temperature": 0.1,     // 低温度确保分析的一致性
  "max_tokens": 1500,     // 足够的token支持详细分析
  "task_type": "fundamentals_analysis"  // 明确指定任务类型
}
```

### **3. 变量传递**
```json
{
  "symbol": "000858",
  "company_name": "五粮液",
  "current_date": "2025-01-22",
  "market_type": "中国A股",
  "currency": "人民币"
}
```

## 🧪 **测试验证**

### **运行测试**
```bash
# 测试TradingAgents提示词
python backend/tests/unit/llm-service/test_tradingagents_prompts.py

# 测试提示词管理
python backend/tests/unit/llm-service/test_prompt_management.py
```

### **验证要点**
- ✅ 提示词模板正确加载
- ✅ 任务类型正确映射
- ✅ 输出格式符合预期
- ✅ 关键词匹配度高
- ✅ 分析逻辑清晰

## 📊 **性能监控**

### **关键指标**
- 📈 **响应时间**: < 30秒
- 🎯 **准确率**: > 90%
- 📝 **完整性**: 包含所有必要分析维度
- 🔍 **专业性**: 使用专业术语和分析框架

### **质量评估**
```python
# 评估维度
quality_metrics = {
    "专业性": "使用专业金融术语",
    "完整性": "包含所有分析维度", 
    "准确性": "数据和逻辑准确",
    "可操作性": "提供具体建议"
}
```

## 🚀 **扩展开发**

### **添加新角色**
1. 创建新的YAML模板文件
2. 更新model_mappings.yaml
3. 添加相应的测试用例
4. 更新文档说明

### **优化现有模板**
1. 收集用户反馈
2. 分析输出质量
3. 调整提示词内容
4. 验证改进效果

这套TradingAgents专业提示词系统为LLM Service提供了强大的股票分析能力，让AI能够像专业分析师团队一样进行多角度、深层次的投资分析！🎯
