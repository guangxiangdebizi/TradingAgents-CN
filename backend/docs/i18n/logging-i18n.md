# 🌍 TradingAgents 国际化日志系统

## 📋 **概述**

TradingAgents 现在支持**国际化日志功能**！系统可以根据语言设置自动将日志消息翻译为对应的语言，支持中文、英文、日文等多种语言的日志输出。

## ✨ **核心特性**

- ✅ **多语言日志**: 支持中文、英文、日文等多种语言
- ✅ **自动翻译**: 日志消息根据设置语言自动翻译
- ✅ **兼容模式**: 兼容现有的日志代码，无需大量修改
- ✅ **高性能**: 1000条日志仅耗时6.5ms，平均每条0.007ms
- ✅ **结构化日志**: 支持参数化的结构化日志消息
- ✅ **动态切换**: 运行时动态切换日志语言

## 🚀 **使用方法**

### **1. 基础使用**

#### **创建国际化日志器**
```python
from backend.shared.i18n.logger import get_i18n_logger
from backend.shared.i18n.config import SupportedLanguage

# 创建中文日志器
logger_zh = get_i18n_logger("my-service", SupportedLanguage.ZH_CN)

# 创建英文日志器
logger_en = get_i18n_logger("my-service", SupportedLanguage.EN_US)

# 创建日文日志器
logger_ja = get_i18n_logger("my-service", SupportedLanguage.JA_JP)
```

#### **使用预定义的日志方法**
```python
# 服务启动日志
logger_zh.startup()                    # 输出: 🚀 数据服务启动中...
logger_en.startup()                    # 输出: 🚀 Data service starting...

# 数据库连接日志
logger_zh.database_connected()         # 输出: ✅ 数据库连接成功
logger_en.database_connected()         # 输出: ✅ Database connected successfully

# 缓存操作日志
logger_zh.cache_hit("000858", "stock_info")     # 输出: 📦 缓存命中: 000858 - stock_info
logger_en.cache_hit("000858", "stock_info")     # 输出: 📦 Cache hit: 000858 - stock_info

# 数据获取日志
logger_zh.data_fetched("000858", "tushare")     # 输出: 📊 数据获取成功: 000858 - tushare
logger_en.data_fetched("000858", "tushare")     # 输出: 📊 Data fetched successfully: 000858 - tushare
```

#### **使用通用日志方法**
```python
# 使用翻译键
logger_zh.info("log.data_service.startup")
logger_zh.error("log.data_service.database_error", error="连接超时")

# 带参数的日志
logger_zh.info("log.data_manager.request_completed", symbol="000858", duration=150)
```

### **2. 兼容模式使用**

#### **创建兼容日志器**
```python
from backend.shared.i18n.logger import get_compatible_logger

# 创建兼容日志器（类似传统日志器）
logger = get_compatible_logger("my-service", SupportedLanguage.ZH_CN)

# 使用传统方式记录日志
logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")

# 支持参数格式化
logger.info("股票 %s 的价格是 %.2f", "000858", 123.45)
logger.info("处理了 {count} 条记录", count=100)
```

### **3. 动态语言切换**

#### **运行时切换语言**
```python
from backend.shared.i18n.logger import get_i18n_logger
from backend.shared.i18n.config import SupportedLanguage

logger = get_i18n_logger("my-service")

# 切换到中文
logger.set_language(SupportedLanguage.ZH_CN)
logger.startup()  # 输出: 🚀 数据服务启动中...

# 切换到英文
logger.set_language(SupportedLanguage.EN_US)
logger.startup()  # 输出: 🚀 Data service starting...
```

#### **通过API设置日志语言**
```bash
# 设置为中文
curl -X POST "http://localhost:8002/api/i18n/set-log-language" \
     -H "Content-Type: application/json" \
     -d '{"language": "zh-CN"}'

# 设置为英文
curl -X POST "http://localhost:8002/api/i18n/set-log-language" \
     -H "Content-Type: application/json" \
     -d '{"language": "en-US"}'
```

## 📊 **预定义日志方法**

### **服务生命周期**
```python
logger.startup()                    # 服务启动
logger.startup_complete()           # 服务启动完成
logger.shutdown()                   # 服务关闭
logger.shutdown_complete()          # 服务关闭完成
```

### **数据库操作**
```python
logger.database_connected()         # 数据库连接成功
logger.database_error("连接超时")    # 数据库错误
logger.redis_connected()            # Redis连接成功
logger.redis_error("连接失败")       # Redis错误
```

### **缓存操作**
```python
logger.cache_hit("000858", "stock_info")      # 缓存命中
logger.cache_miss("000858", "stock_info")     # 缓存未命中
logger.cache_expired("000858", "stock_info")  # 缓存过期
logger.cache_updated("000858", "stock_info")  # 缓存更新
```

### **数据操作**
```python
logger.data_fetched("000858", "tushare")      # 数据获取成功
logger.data_fetch_failed("000858", "网络错误") # 数据获取失败
logger.data_saved("000858", "stock_info")     # 数据保存成功
logger.data_save_failed("000858", "格式错误")  # 数据保存失败
```

### **数据管理器操作**
```python
logger.manager_initialized()                   # 管理器初始化成功
logger.processing_request("000858", "stock_info") # 处理数据请求
logger.request_completed("000858", 150)        # 请求完成（耗时150ms）
logger.request_failed("000858", "数据源不可用") # 请求失败
```

### **系统操作**
```python
logger.cleanup_started()                       # 开始清理
logger.cleanup_completed(100)                  # 清理完成（100条记录）
logger.force_refresh("000858", "stock_info")   # 强制刷新
logger.rate_limit_hit("tushare")               # 触发频率限制
logger.network_error("连接超时")                # 网络错误
```

## 🔧 **配置和集成**

### **在数据管理器中使用**
```python
from backend.shared.i18n.logger import get_i18n_logger
from backend.shared.i18n.config import SupportedLanguage

class DataManager:
    def __init__(self, mongodb_client, redis_client, language=None):
        # 初始化国际化日志器
        self.logger = get_i18n_logger("data-manager", language)
        
        # 记录初始化日志
        self.logger.manager_initialized()
    
    def set_log_language(self, language: SupportedLanguage):
        """设置日志语言"""
        self.logger.set_language(language)
    
    async def get_data(self, symbol: str, data_type: str):
        # 记录开始处理
        self.logger.processing_request(symbol, data_type)
        
        try:
            # 数据处理逻辑...
            self.logger.data_fetched(symbol, "tushare")
            self.logger.request_completed(symbol, 150)
            return data
        except Exception as e:
            self.logger.request_failed(symbol, str(e))
            raise
```

### **在FastAPI中集成**
```python
from backend.shared.i18n.logger import get_i18n_logger

# 创建应用级日志器
app_logger = get_i18n_logger("api-service")

@app.on_event("startup")
async def startup_event():
    app_logger.startup()

@app.on_event("shutdown") 
async def shutdown_event():
    app_logger.shutdown()

@app.get("/api/data/{symbol}")
async def get_data(symbol: str):
    app_logger.api_request("GET", f"/api/data/{symbol}")
    # API逻辑...
    app_logger.api_response(200, "success")
```

## 📝 **日志翻译键**

### **服务日志键**
```
log.data_service.startup              # 🚀 数据服务启动中...
log.data_service.startup_complete     # ✅ 数据服务启动完成
log.data_service.database_connected   # ✅ 数据库连接成功
log.data_service.cache_hit            # 📦 缓存命中: {symbol} - {data_type}
log.data_service.data_fetched         # 📊 数据获取成功: {symbol} - {source}
```

### **管理器日志键**
```
log.data_manager.initialized         # ✅ 数据管理器初始化成功
log.data_manager.processing_request  # 🔄 处理数据请求: {symbol} - {data_type}
log.data_manager.request_completed   # ✅ 数据请求完成: {symbol} - 耗时 {duration}ms
log.data_manager.fallback_triggered  # 🔄 触发回退机制: {reason}
```

## 🧪 **测试和验证**

### **运行测试脚本**
```bash
cd backend

# 测试基础日志功能
python test_i18n_logging.py basic

# 测试API调用日志
python test_i18n_logging.py api zh-CN

# 测试兼容模式
python test_i18n_logging.py compat

# 测试性能
python test_i18n_logging.py perf

# 运行完整测试
python test_i18n_logging.py
```

### **测试结果示例**
```
🌍 测试基础国际化日志功能
========================================
📋 中文日志测试:
2025-07-21 22:51:45,359 | test-zh | INFO | 🚀 数据服务启动中...
2025-07-21 22:51:45,359 | test-zh | INFO | ✅ 数据库连接成功

📋 英文日志测试:
2025-07-21 22:51:45,360 | test-en | INFO | 🚀 Data service starting...
2025-07-21 22:51:45,360 | test-en | INFO | ✅ Database connected successfully

⚡ 性能测试:
✅ 1000条国际化日志耗时: 6.50ms
   平均每条日志: 0.007ms
```

## 🎯 **最佳实践**

### **1. 日志器命名**
```python
# 使用模块名作为日志器名称
logger = get_i18n_logger("data-service")
logger = get_i18n_logger("analysis-engine")
logger = get_i18n_logger("api-gateway")
```

### **2. 错误处理**
```python
try:
    # 业务逻辑
    result = process_data()
    logger.data_saved(symbol, "stock_info")
except Exception as e:
    logger.data_save_failed(symbol, str(e))
    raise
```

### **3. 性能考虑**
```python
# 对于高频日志，使用DEBUG级别
logger.debug("log.data_service.cache_hit", symbol=symbol, data_type=data_type)

# 对于重要事件，使用INFO级别
logger.info("log.data_service.data_fetched", symbol=symbol, source=source)
```

### **4. 参数化日志**
```python
# 好的做法：使用参数化
logger.request_completed(symbol, duration)

# 避免：字符串拼接
logger.info(f"请求完成: {symbol} - 耗时 {duration}ms")  # 不推荐
```

## 🎉 **总结**

现在 TradingAgents 具备了完整的国际化日志支持：

✅ **多语言支持**: 中文、英文、日文等多种语言  
✅ **自动翻译**: 日志消息根据语言自动翻译  
✅ **高性能**: 平均每条日志仅0.007ms  
✅ **易于使用**: 预定义方法和兼容模式  
✅ **动态切换**: 运行时切换日志语言  
✅ **结构化**: 支持参数化的结构化日志  

您的 TradingAgents 系统现在可以为全球开发者和运维人员提供本地化的日志体验！🌍
