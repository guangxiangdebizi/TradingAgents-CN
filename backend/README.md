# 🏗️ TradingAgents Backend

## 📁 目录结构

```
backend/
├── 📚 docs/                    # 文档目录
│   ├── api/                    # API文档
│   ├── data-sources/           # 数据源文档
│   ├── deployment/             # 部署文档
│   ├── development/            # 开发文档
│   ├── troubleshooting/        # 故障排除
│   └── i18n/                   # 国际化文档
├── 🧪 tests/                   # 测试目录
│   ├── unit/                   # 单元测试
│   ├── integration/            # 集成测试
│   ├── performance/            # 性能测试
│   └── fixtures/               # 测试数据
├── 🔧 tools/                   # 工具目录
│   ├── data-sources/           # 数据源工具
│   ├── debugging/              # 调试工具
│   ├── setup/                  # 设置工具
│   └── validation/             # 验证工具
├── 🏗️ scripts/                 # 构建脚本
├── 🔗 shared/                  # 共享模块
├── 🌐 data-service/            # 数据服务
├── 🔍 analysis-engine/         # 分析引擎
├── 🚪 api-gateway/             # API网关
└── ⏰ task-scheduler/          # 任务调度器
```

## 🚀 快速开始

### 1. 环境设置
```bash
# 配置API密钥
python tools/setup/setup_api_keys.py

# 验证配置
python tools/validation/validate_json_config.py
```

### 2. 启动服务
```bash
# 启动数据服务
cd data-service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### 3. 运行测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行API测试
python tests/unit/api/test_api_interactive.py
```

## 📚 文档

- [📖 完整文档](docs/README.md)
- [🔌 API参考](docs/api/data-source-api-reference.md)
- [🌐 数据源配置](docs/data-sources/new-us-data-sources.md)
- [🚀 部署指南](docs/deployment/deployment-guide.md)

## 🧪 测试

- [🧪 测试指南](tests/README.md)
- [🔬 单元测试](tests/unit/)
- [🔗 集成测试](tests/integration/)

## 🔧 工具

- [🔧 工具指南](tools/README.md)
- [⚙️ 设置工具](tools/setup/)
- [🐛 调试工具](tools/debugging/)

## 🌟 主要特性

- ✅ **多数据源支持** - Alpha Vantage, Twelve Data, FinnHub等
- ✅ **智能优先级** - 自动降级和故障转移
- ✅ **缓存机制** - Redis和MongoDB双重缓存
- ✅ **国际化支持** - 多语言日志和错误信息
- ✅ **微服务架构** - 模块化设计，易于扩展
- ✅ **完整测试** - 单元测试和集成测试覆盖
