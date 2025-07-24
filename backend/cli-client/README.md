# TradingAgents CLI Client (Backend版本)

🚀 **与TradingAgents完全一致的命令行界面**，通过API Gateway调用Backend微服务进行股票分析。

## ✨ 特性

- 🎯 **完全一致的用户体验**: 与TradingAgents原版CLI界面100%一致
- 📊 **8步交互式配置**: 市场选择 → 股票代码 → 分析日期 → 分析师团队 → 研究深度 → API Gateway → LLM提供商 → LLM模型
- 🎨 **美观的界面**: ASCII艺术字、彩色表格、进度条显示
- 🗣️ **多轮辩论监控**: 实时显示投资辩论和风险分析进度
- 📈 **详细结果展示**: 投资建议、风险评估、辩论摘要
- 💾 **结果保存**: 自动保存分析结果为JSON格式

## 🚀 快速开始

### 安装

#### Windows用户（推荐）
```cmd
# 进入CLI客户端目录
cd backend\cli-client

# 使用简单启动脚本（自动安装依赖）
start_simple.bat
```

#### Linux/Mac用户
```bash
# 进入CLI客户端目录
cd backend/cli-client

# 安装依赖
pip install -r requirements.txt

# 使用启动脚本
./start.sh
```

#### 手动安装
```bash
# 克隆项目
git clone <repository-url>
cd backend/cli-client

# 安装依赖
pip install -r requirements.txt

# 或者使用setup.py安装
pip install -e .
```

### 基本使用

#### 1. 标准Python模块方式（推荐）
```bash
# 使用标准Python模块启动
python -m app

# 或者指定main模块
python -m app.main
```

#### 2. 直接运行
```bash
# 直接运行主文件
python app/main.py

# 或者运行旧版本（兼容）
python trading_cli.py
```

#### 3. 安装后使用
```bash
# 安装后可以直接使用命令
trading-cli
# 或者简写
tcli
# 或者使用原版命令名
tradingagents
```

#### 4. 使用启动脚本
```bash
# Linux/Mac
./start.sh

# Windows（推荐使用简单版本）
start_simple.bat

# Windows（完整版本）
start.bat
```

### 快速测试

在运行CLI之前，可以先测试环境是否正确：

```bash
# 测试CLI环境
python test_cli_quick.py
```

这会检查：
- ✅ Python依赖是否正确安装
- ✅ UI组件是否正常工作
- ✅ API Gateway连接状态

## 📖 使用指南

### 8步交互式配置流程

启动CLI后，会按照以下8个步骤进行配置：

| 步骤 | 内容 | 说明 |
|------|------|------|
| **步骤 1/8** | 选择股票市场 | 中国A股、美国股票、香港股票 |
| **步骤 2/8** | 输入股票代码 | 根据选择的市场输入对应的股票代码 |
| **步骤 3/8** | 选择分析日期 | 默认为当前日期，可自定义 |
| **步骤 4/8** | 选择分析师团队 | 市场、基本面、新闻、社交媒体分析师 |
| **步骤 5/8** | 选择研究深度 | 快速(1轮)、标准(3轮)、深度(5轮)辩论 |
| **步骤 6/8** | 选择API Gateway | 本地API Gateway或自定义远程地址 |
| **步骤 7/8** | 选择LLM提供商 | 阿里百炼、DeepSeek、OpenAI、Anthropic、Google等 |
| **步骤 8/8** | 选择LLM模型 | 根据提供商显示可用的具体模型版本 |

### 完整使用流程示例

```bash
# 启动CLI（推荐方式）
$ python -m app

# 或者
$ python -m app.main

████████╗██████╗  █████╗ ██████╗ ██╗███╗   ██╗ ██████╗  █████╗  ██████╗ ███████╗███╗   ██╗████████╗███████╗
╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝ ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝
   ██║   ██████╔╝███████║██║  ██║██║██╔██╗ ██║██║  ███╗███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ███████╗
   ██║   ██╔══██╗██╔══██║██║  ██║██║██║╚██╗██║██║   ██║██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ╚════██║
   ██║   ██║  ██║██║  ██║██████╔╝██║██║ ╚████║╚██████╔╝██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ███████║
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝

TradingAgents: 多智能体大语言模型金融交易框架 - CLI
Multi-Agents LLM Financial Trading Framework - CLI

工作流程 | Workflow Steps:
I. 分析师团队 | Analyst Team → II. 研究团队 | Research Team → III. 交易员 | Trader → IV. 风险管理 | Risk Management → V. 投资组合管理 | Portfolio Management

Built by Backend Team (Based on TradingAgents)

┌─────────────────────────────────────────────────────────────┐
│ 步骤 1/8: 选择股票市场 | Step 1/8: Select Stock Market      │
│ 请选择您要分析的股票市场 | Please select the stock market   │
│ you want to analyze                                         │
└─────────────────────────────────────────────────────────────┘

可选市场 | Available Markets:
  1. 中国A股 | China A-shares
  2. 美国股票 | US Stocks
  3. 香港股票 | Hong Kong Stocks

请选择市场 | Select market [1]: 1
✅ 已选择: 中国A股 | China A-shares

┌─────────────────────────────────────────────────────────────┐
│ 步骤 2/6: 输入股票代码 | Step 2/6: Enter Stock Ticker       │
│ 请输入中国A股 | China A-shares的股票代码 | Please enter the │
│ stock ticker for 中国A股 | China A-shares                   │
└─────────────────────────────────────────────────────────────┘

请输入中国A股 | China A-shares股票代码 | Enter 中国A股 | China A-shares ticker symbol [000001]: 000001
✅ 股票代码: 000001

# ... 继续其他步骤 ...

┌─────────────────────────────────────────────────────────────┐
│ 步骤 7/8: 选择LLM提供商 | Step 7/8: Select LLM Provider     │
│ 请选择要使用的大语言模型提供商 | Please select the LLM      │
│ provider to use                                             │
└─────────────────────────────────────────────────────────────┘

正在获取支持的LLM提供商... | Fetching supported LLM providers...

可选LLM提供商 | Available LLM Providers:
  1. 阿里百炼 | Alibaba DashScope
     阿里云通义千问系列模型
  2. DeepSeek
     DeepSeek系列模型
  3. OpenAI
     GPT系列模型

选择LLM提供商 | Select LLM provider [1]: 1
✅ 已选择: 阿里百炼 | Alibaba DashScope

┌─────────────────────────────────────────────────────────────┐
│ 步骤 8/8: 选择LLM模型 | Step 8/8: Select LLM Model         │
│ 请选择阿里百炼的具体模型 | Please select the specific model │
└─────────────────────────────────────────────────────────────┘

正在获取阿里百炼的模型列表... | Fetching models for 阿里百炼...

阿里百炼可用模型 | Available Models for 阿里百炼:
  1. 通义千问Plus (最新版)
     高性能通用模型
  2. 通义千问Turbo (最新版)
     快速响应模型
  3. 通义千问Max (最新版)
     最强性能模型

选择阿里百炼模型 | Select 阿里百炼 model [1]: 1
✅ 已选择: 通义千问Plus (最新版)

步骤 1: 连接API Gateway | Connecting to API Gateway
✅ API Gateway连接成功 | API Gateway connected successfully

步骤 2: 启动分析 | Starting Analysis
🔄 正在为 000001 启动综合分析...
✅ 分析已启动，ID: uuid-12345

步骤 3: 执行分析 | Executing Analysis
🔄 [15.2s] 执行步骤: market_analyst
🔄 [32.1s] 执行步骤: fundamentals_analyst
🗣️ 投资辩论 第1/3轮 - bull_researcher
🗣️ 投资辩论 第2/3轮 - bear_researcher
⚠️ 风险分析 第1/2轮 - risky_analyst
✅ 分析完成!

步骤 4: 分析结果 | Analysis Results

🎯 最终投资建议 | Final Investment Recommendation
┌─────────────────────┬─────────────────────────────────┐
│ 项目 | Item          │ 值 | Value                     │
├─────────────────────┼─────────────────────────────────┤
│ 投资动作 | Action     │ buy                             │
│ 置信度 | Confidence  │ 75.00%                          │
│ 目标价格 | Target Price│ 15.50                          │
│ 推理依据 | Reasoning  │ 基于多轮辩论和风险分析的综合建议 │
└─────────────────────┴─────────────────────────────────┘

是否查看详细分析报告? | View detailed analysis reports? [y/N]: y
是否保存分析结果? | Save analysis results? [y/N]: y
✅ 结果已保存到: results/analysis_uuid-12345_20240122_143022.json
✅ 分析完成! | Analysis completed!
```

## ⚙️ 配置管理

### 配置文件

CLI会在用户主目录创建配置文件 `~/.trading_cli_config.json`：

```json
{
  "backend_url": "http://localhost:8001",
  "default_analysis_type": "comprehensive",
  "auto_refresh": true,
  "refresh_interval": 2,
  "max_wait_time": 300,
  "max_debate_rounds": 3,
  "max_risk_rounds": 2,
  "show_progress": true,
  "color_output": true,
  "save_history": true
}
```

### 环境变量

支持以下环境变量：

```bash
export TRADING_CLI_BACKEND_URL="http://localhost:8001"
export TRADING_CLI_ANALYSIS_TYPE="comprehensive"
export TRADING_CLI_AUTO_REFRESH="true"
export TRADING_CLI_LOG_LEVEL="INFO"
```

### 预设模式

支持多种预设配置：

```bash
# 快速模式 (1轮辩论)
trading-cli> set preset quick

# 标准模式 (3轮辩论)
trading-cli> set preset standard

# 详细模式 (5轮辩论)
trading-cli> set preset detailed

# 静默模式 (无进度显示)
trading-cli> set preset silent
```

## 🔧 高级功能

### 批量分析

```python
# 创建批量分析脚本
import asyncio
from trading_cli import BackendClient

async def batch_analyze():
    symbols = ["000001", "000002", "600036"]

    async with BackendClient() as client:
        tasks = []
        for symbol in symbols:
            task = client.start_analysis(symbol)
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        for symbol, result in zip(symbols, results):
            print(f"{symbol}: {result}")

asyncio.run(batch_analyze())
```

### 自定义分析配置

```bash
# 自定义辩论轮数
trading-cli> analyze 000001 --max-debate-rounds 5 --max-risk-rounds 3

# 指定分析类型
trading-cli> analyze 000001 --analysis-type quick
```

### 结果导出

```bash
# 导出分析结果为JSON
trading-cli> result uuid-12345 --export result.json

# 导出为CSV格式
trading-cli> result uuid-12345 --export result.csv --format csv
```

## 🐛 故障排查

### 常见问题

#### 1. Windows批处理脚本错误
```cmd
# 如果start.bat出现错误，使用简单版本
start_simple.bat

# 或者直接运行Python（推荐）
python -m app

# 或者运行旧版本
python trading_cli.py
```

#### 2. Python依赖问题
```bash
# 检查Python版本（需要3.8+）
python --version

# 重新安装依赖
pip install --upgrade -r requirements.txt

# 如果有权限问题，使用用户安装
pip install --user -r requirements.txt
```

#### 3. 连接API Gateway失败
```bash
❌ API Gateway连接失败: Connection refused

# 解决方案:
# 1. 检查API Gateway是否启动
curl http://localhost:8000/health

# 2. 在CLI中会提示选择API Gateway地址
# 可以选择自定义URL或确认API Gateway正在运行
```

#### 4. 中文显示问题
```cmd
# Windows命令行中文显示问题
chcp 65001

# 或者使用PowerShell
powershell
python -m app
```

#### 5. 模块导入错误
```bash
# 测试环境
python test_cli_quick.py

# 如果缺少模块，重新安装
pip install rich typer aiohttp loguru
```

### 调试模式

```bash
# 启用详细日志
export TRADING_CLI_LOG_LEVEL=DEBUG
python trading_cli.py

# 保存日志到文件
export TRADING_CLI_LOG_FILE=trading_cli.log
python trading_cli.py
```

## 🔄 与TradingAgents对比

| 功能 | TradingAgents | Backend CLI |
|------|---------------|-------------|
| **分析能力** | 本地LangGraph | 微服务+图引擎 |
| **多轮辩论** | ✅ | ✅ |
| **风险分析** | ✅ | ✅ |
| **实时监控** | ❌ | ✅ |
| **历史记录** | ❌ | ✅ |
| **配置管理** | 基础 | 高级 |
| **可扩展性** | 有限 | 高 |
| **部署方式** | 单机 | 分布式 |

## 📚 API参考

### BackendClient类

```python
class BackendClient:
    async def health_check() -> Dict[str, Any]
    async def start_analysis(symbol: str, analysis_type: str = "comprehensive") -> Dict[str, Any]
    async def get_analysis_status(analysis_id: str) -> Dict[str, Any]
    async def get_analysis_result(analysis_id: str) -> Dict[str, Any]
    async def cancel_analysis(analysis_id: str) -> Dict[str, Any]
```

### 配置选项

详细配置选项请参考 `config.py` 中的 `CLIConfig` 类。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [Backend项目文档](../docs/)
- [API文档](../docs/api/)
- [故障排查指南](../docs/troubleshooting/)
- [TradingAgents项目](https://github.com/your-org/TradingAgents)