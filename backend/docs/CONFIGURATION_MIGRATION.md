# 配置文件迁移指南

## 📋 **概述**

为了更好地管理Backend微服务的配置，我们将配置文件从根目录的 `.env` 迁移到 `backend/.backend_env`。

## 🔄 **迁移步骤**

### 1. **备份现有配置**

如果您之前有 `.env` 文件，请先备份：

```bash
# 备份现有配置
cp .env .env.backup
```

### 2. **创建新的Backend配置**

```bash
# 复制示例配置
cp backend/.backend_env.example backend/.backend_env
```

### 3. **迁移配置内容**

将您的API密钥从旧的 `.env` 文件迁移到新的 `backend/.backend_env` 文件：

#### **LLM服务密钥**
```bash
# 旧配置 (.env)
DASHSCOPE_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# 新配置 (backend/.backend_env)
DASHSCOPE_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

#### **数据源密钥**
```bash
# 旧配置 (.env)
TUSHARE_TOKEN=your_token_here
FINNHUB_API_KEY=your_key_here

# 新配置 (backend/.backend_env)
TUSHARE_TOKEN=your_token_here
FINNHUB_API_KEY=your_key_here
```

### 4. **验证配置**

启动任一Backend服务验证配置是否正确：

```bash
cd backend/data-service
python -m app.main
```

您应该看到：
```
✅ 加载Backend环境变量: C:\code\TradingAgentsCN\backend\.backend_env
```

## 🔍 **配置差异**

### **新增配置项**

新的 `.backend_env` 文件包含了更多的微服务配置：

```bash
# 微服务端口配置
API_GATEWAY_PORT=8000
ANALYSIS_ENGINE_PORT=8001
DATA_SERVICE_PORT=8002
TASK_SCHEDULER_PORT=8003
LLM_SERVICE_PORT=8004
MEMORY_SERVICE_PORT=8006
AGENT_SERVICE_PORT=8008

# 数据库配置
MONGODB_URL=mongodb://admin:tradingagents123@localhost:27017/tradingagents?authSource=admin
REDIS_URL=redis://localhost:6379/0

# Embedding服务配置
DEFAULT_EMBEDDING_PROVIDER=dashscope
DEFAULT_EMBEDDING_MODEL=text-embedding-v3

# Ollama本地服务配置 (可选)
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# 系统配置
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### **移除的配置项**

一些旧的配置项已不再需要或已重新组织。

## 🔒 **安全注意事项**

1. **不要提交敏感文件**
   - `.backend_env` 已添加到 `.gitignore`
   - 只提交 `.backend_env.example` 示例文件

2. **保护API密钥**
   - 定期轮换API密钥
   - 不要在代码或文档中硬编码密钥

3. **环境隔离**
   - 开发、测试、生产环境使用不同的配置
   - 使用环境变量覆盖机制

## 🛠️ **故障排除**

### **配置文件未找到**

如果看到警告：
```
⚠️ Backend环境文件不存在: /path/to/.backend_env
```

解决方案：
```bash
# 确保文件存在
ls -la backend/.backend_env

# 如果不存在，复制示例文件
cp backend/.backend_env.example backend/.backend_env
```

### **API密钥无效**

如果服务启动失败，检查：
1. API密钥格式是否正确
2. API密钥是否有效且未过期
3. 配置文件语法是否正确（无多余空格、引号等）

### **端口冲突**

如果遇到端口占用错误：
1. 检查 `.backend_env` 中的端口配置
2. 确保没有其他服务占用相同端口
3. 修改端口配置并重启服务

## 📚 **相关文档**

- [Backend启动指引](README_STARTUP.md)
- [开发环境配置](docs/development/getting-started.md)
- [本地开发指南](docs/development/local-development.md)
- [数据源配置](docs/data-sources/data-management.md)

## 🆘 **获取帮助**

如果在迁移过程中遇到问题：

1. 检查相关文档
2. 运行服务状态检查：`python backend/check_services.py`
3. 查看服务启动日志
4. 提交Issue或联系开发团队
