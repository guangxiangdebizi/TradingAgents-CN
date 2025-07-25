# 智能体架构快速参考

## 🎯 核心变化

**Agent Service已移除** → **智能体直接集成在Analysis Engine中**

## 📁 新的智能体目录结构

```
backend/analysis-engine/app/agents/
├── base/
│   └── base_agent.py           # 基础智能体类
├── analysts/                   # 分析师团队
│   ├── market_analyst.py       # 市场技术分析师
│   ├── fundamentals_analyst.py # 基本面分析师  
│   ├── news_analyst.py         # 新闻分析师
│   └── social_analyst.py       # 社交媒体分析师
├── researchers/                # 研究员团队
│   ├── bull_researcher.py      # 看涨研究员
│   ├── bear_researcher.py      # 看跌研究员
│   └── research_manager.py     # 研究经理
├── traders/                    # 交易员团队
│   └── trader.py               # 交易员
└── managers/                   # 管理者团队
    └── risk_manager.py         # 风险管理经理
```

## 🔄 工作流程

```
用户请求 → API Gateway → Analysis Engine → 智能体团队协作 → 返回结果
```

### 智能体协作流程
1. **数据收集** → 各分析师并行分析
2. **观点研究** → 看涨/看跌研究员辩论
3. **决策整合** → 研究经理综合决策
4. **交易执行** → 交易员制定执行计划
5. **风险控制** → 风险管理经理最终审核

## 🤖 智能体功能概览

| 智能体 | 主要功能 | 输出 |
|--------|----------|------|
| **MarketAnalyst** | 技术分析、价格趋势、成交量分析 | 技术分析报告 + 投资建议 |
| **FundamentalsAnalyst** | 财务分析、估值分析、行业对比 | 基本面报告 + 投资评级 |
| **NewsAnalyst** | 新闻事件分析、市场情绪评估 | 新闻影响报告 + 情绪预测 |
| **SocialAnalyst** | 社交媒体情绪、讨论热度分析 | 社交情绪报告 + 趋势判断 |
| **BullResearcher** | 挖掘投资机会、看涨因素分析 | 看涨研究报告 + 目标价位 |
| **BearResearcher** | 识别投资风险、看跌因素分析 | 看跌研究报告 + 风险评估 |
| **ResearchManager** | 整合团队观点、制定投资决策 | 最终研究决策 + 执行策略 |
| **Trader** | 交易策略制定、执行计划设计 | 交易执行计划 + 风险控制 |
| **RiskManager** | 综合风险评估、最终投资决策 | 风险管理报告 + 最终决策 |

## 🛠️ 开发要点

### 智能体基类 (BaseAgent)
```python
class BaseAgent:
    def __init__(self, name, description, llm_client, data_client):
        self.name = name
        self.description = description
        self.llm_client = llm_client      # AI推理工具
        self.data_client = data_client    # 数据获取工具
    
    async def analyze(self, symbol: str, context: dict) -> dict:
        # 子类必须实现此方法
        pass
```

### 智能体开发模式
1. **数据获取** → 使用data_client获取市场数据
2. **专业分析** → 内置业务逻辑进行分析计算
3. **AI推理** → 使用llm_client生成专业报告
4. **结果整合** → 返回标准化的分析结果

### 添加新智能体步骤
1. 在对应目录创建智能体文件
2. 继承BaseAgent基类
3. 实现analyze()方法
4. 设计专业提示词模板
5. 在图节点中注册

## 📊 性能优势

| 指标 | 旧架构 (HTTP调用) | 新架构 (内存协作) | 提升 |
|------|------------------|------------------|------|
| **延迟** | 50-100ms per call | <1ms | 50-100x |
| **吞吐量** | 受网络限制 | 受CPU限制 | 10-100x |
| **资源使用** | 多个微服务 | 单一服务 | -30% |
| **部署复杂度** | 高 | 低 | 简化 |

## 🔧 配置变化

### 移除的配置
```bash
# 不再需要这些配置
AGENT_SERVICE_PORT=8008
AGENT_SERVICE_HOST=localhost
AGENT_SERVICE_URL=http://agent-service:8008
```

### Docker服务变化
```yaml
# docker-compose.yml 中移除了
services:
  agent-service:  # ❌ 已删除
    # ...
```

## 📝 重要提醒

### ✅ 保持不变
- API接口完全兼容
- 分析结果格式一致
- 用户体验无变化
- 所有智能体功能完整

### ⚠️ 注意事项
- 智能体日志现在在analysis-engine中
- 不再有独立的agent-service健康检查
- Docker部署不再需要agent-service容器

## 🔍 故障排除

### 常见问题
1. **智能体未找到** → 检查智能体是否正确注册在图节点中
2. **分析失败** → 查看analysis-engine日志，不是agent-service日志
3. **性能问题** → 检查analysis-engine的内存和CPU使用

### 日志位置
```bash
# 智能体日志现在在这里
backend/analysis-engine/logs/
```

## 📚 相关文档

- [完整移除文档](./agent-service-removal.md)
- [智能体开发指南](./agent-development-guide.md)
- [Analysis Engine架构](./analysis-engine-architecture.md)

---

**最后更新**: 2025-01-25  
**状态**: ✅ 生产就绪
