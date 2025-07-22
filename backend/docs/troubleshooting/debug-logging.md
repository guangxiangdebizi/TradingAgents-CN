# 🐛 TradingAgents Debug级别国际化日志

## 📋 **概述**

TradingAgents 现在在重要位置添加了**Debug级别的国际化日志**！这些日志提供了详细的系统运行信息，包括API调用、数据处理、缓存操作、性能监控等关键节点的详细记录。

## ✨ **Debug日志特性**

- ✅ **详细追踪**: API请求/响应的完整生命周期
- ✅ **性能监控**: 查询时间、缓存命中率、慢查询警告
- ✅ **数据流追踪**: 数据获取、转换、保存的每个步骤
- ✅ **错误诊断**: 详细的错误信息和调用栈
- ✅ **多语言支持**: 中文、英文等多种语言的debug日志
- ✅ **动态控制**: 运行时开启/关闭debug日志

## 🔧 **启用Debug日志**

### **1. 环境变量控制**
```bash
# 启用debug模式
export DEBUG=true

# 或者在Windows中
set DEBUG=true

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### **2. 代码中控制**
```python
import logging

# 设置日志级别为DEBUG
logging.basicConfig(level=logging.DEBUG)

# 或者只为特定logger设置
logger = logging.getLogger("data-service")
logger.setLevel(logging.DEBUG)
```

### **3. 中间件控制**
```python
# 在main.py中
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

if DEBUG_MODE:
    # 启用所有debug中间件
    app.add_middleware(APIDebugMiddleware, enable_debug=True)
    app.add_middleware(PerformanceMonitorMiddleware, enable_monitoring=True)
    app.add_middleware(ValidationDebugMiddleware, enable_validation_debug=True)
```

## 📊 **Debug日志类型**

### **1. API调试日志**

#### **请求处理流程**
```
📥 收到API请求: GET /api/stock/info/000858
📋 请求参数: {'lang': 'zh-CN', 'format': 'json'}
📄 请求头: {'User-Agent': 'curl/7.68.0', 'Accept': '*/*'}
🔍 开始验证: symbol
✅ 验证通过: symbol
📤 准备响应: 200
📊 响应数据: 1024 字节
✅ 响应已发送: 150ms
```

#### **中间件处理**
```
🔄 中间件开始: APIDebugMiddleware
🔄 中间件开始: I18nMiddleware
✅ 中间件完成: I18nMiddleware - 5ms
✅ 中间件完成: APIDebugMiddleware - 155ms
```

### **2. 数据处理调试日志**

#### **缓存操作**
```
🔍 检查缓存: 000858 - stock_info
📋 缓存结果: miss - 000858
🔍 检查Redis缓存: data:000858:stock_info
❌ Redis缓存未命中: data:000858:stock_info
🔍 检查MongoDB缓存: 000858 - stock_info
❌ MongoDB缓存未命中: 000858 - stock_info
💾 开始保存缓存: 000858 - stock_info
✅ 缓存保存完成: 000858 - TTL: 3600秒
```

#### **数据源调用**
```
🎯 选择数据源: tushare - 000858
📞 调用数据源: tushare - http://api.tushare.pro/stock/info
📨 数据源响应: tushare - success - 2048 字节
🔄 开始数据转换: raw_response -> stock_info
✅ 数据转换完成: 1 条记录
```

#### **数据库操作**
```
🗄️ 开始保存数据库: stock_info - 000858
✅ 数据库保存完成: stock_info - 1 条记录
🔄 开始数据验证: stock_info
✅ 数据验证完成: 1/1
```

### **3. 性能监控日志**

#### **查询性能**
```
⏱️ 查询开始: data_request - 000858
✅ 查询完成: data_request - 150ms
📊 缓存性能: 命中率 85.5% - 平均响应 25.3ms
🗄️ 数据库性能: 查询 100 次 - 平均 45.2ms
🌐 API性能: /api/stock/info - 1000 请求 - 平均 120ms
```

#### **慢查询警告**
```
🐌 慢查询警告: complex_analysis_query - 1500ms (阈值: 1000ms)
🐌 Slow query warning: SELECT * FROM stocks - 2500ms (threshold: 1000ms)
```

### **4. 系统监控日志**

#### **资源使用**
```
💾 内存使用: 512MB / 1024MB (50%)
⚡ CPU使用: 75.2%
💿 磁盘使用: 100GB / 500GB (20%)
🔗 连接池状态: 8/10 活跃连接
🧵 线程池状态: 5/20 活跃线程
```

#### **配置和健康检查**
```
⚙️ 配置加载: config.json - 25 个配置项
🔄 配置更新: cache_ttl = 3600
🏥 服务健康检查: redis - healthy
🏥 服务健康检查: mongodb - healthy
```

## 🌍 **多语言Debug日志**

### **中文Debug日志**
```python
from backend.shared.i18n.logger import get_i18n_logger
from backend.shared.i18n.config import SupportedLanguage

# 创建中文debug日志器
debug_logger = get_i18n_logger("my-service", SupportedLanguage.ZH_CN)

debug_logger.debug_api_request_received("GET", "/api/stock/info/000858")
# 输出: 📥 收到API请求: GET /api/stock/info/000858

debug_logger.debug_cache_hit("000858", "stock_info")
# 输出: 📦 缓存命中: 000858 - stock_info

debug_logger.debug_slow_query("complex_query", 1500, 1000)
# 输出: 🐌 慢查询警告: complex_query - 1500ms (阈值: 1000ms)
```

### **英文Debug日志**
```python
# 切换到英文
debug_logger.set_language(SupportedLanguage.EN_US)

debug_logger.debug_api_request_received("GET", "/api/stock/info/000858")
# 输出: 📥 API request received: GET /api/stock/info/000858

debug_logger.debug_cache_hit("000858", "stock_info")
# 输出: 📦 Cache hit: 000858 - stock_info

debug_logger.debug_slow_query("complex_query", 1500, 1000)
# 输出: 🐌 Slow query warning: complex_query - 1500ms (threshold: 1000ms)
```

## 🔧 **Debug日志方法**

### **API相关**
```python
debug_logger.debug_api_request_received(method, path)      # API请求接收
debug_logger.debug_api_request_params(params)             # 请求参数
debug_logger.debug_api_request_headers(headers)           # 请求头
debug_logger.debug_api_response_prepared(status_code)     # 响应准备
debug_logger.debug_api_response_data(data_size)           # 响应数据大小
debug_logger.debug_api_response_sent(duration)            # 响应发送时间
debug_logger.debug_validation_start(field)                # 验证开始
debug_logger.debug_validation_passed(field)               # 验证通过
debug_logger.debug_validation_failed(field, error)       # 验证失败
```

### **数据相关**
```python
debug_logger.debug_cache_check_start(symbol, data_type)   # 缓存检查开始
debug_logger.debug_cache_check_result(result, symbol)     # 缓存检查结果
debug_logger.debug_data_source_select(source, symbol)     # 数据源选择
debug_logger.debug_data_source_call(source, url)          # 数据源调用
debug_logger.debug_data_source_response(source, status, size)  # 数据源响应
debug_logger.debug_data_transform_start(from_fmt, to_fmt) # 数据转换开始
debug_logger.debug_data_transform_end(records)            # 数据转换完成
debug_logger.debug_cache_save_start(symbol, data_type)    # 缓存保存开始
debug_logger.debug_cache_save_end(symbol, ttl)            # 缓存保存完成
debug_logger.debug_db_save_start(collection, symbol)      # 数据库保存开始
debug_logger.debug_db_save_end(collection, count)         # 数据库保存完成
```

### **性能相关**
```python
debug_logger.debug_query_start(query_type, symbol)        # 查询开始
debug_logger.debug_query_end(query_type, duration)        # 查询完成
debug_logger.debug_cache_performance(hit_rate, avg_time)  # 缓存性能
debug_logger.debug_slow_query(query, duration, threshold) # 慢查询警告
```

### **系统相关**
```python
debug_logger.debug_memory_usage(used, total, percent)     # 内存使用
debug_logger.debug_cpu_usage(percent)                     # CPU使用
debug_logger.debug_connection_pool(active, max_conn)      # 连接池状态
debug_logger.debug_config_loaded(config_file, keys)       # 配置加载
debug_logger.debug_service_health_check(service, status)  # 健康检查
```

## 🧪 **测试Debug日志**

### **运行测试脚本**
```bash
cd backend

# 测试基础debug日志
python test_debug_logging.py basic

# 测试API debug日志
python test_debug_logging.py api

# 测试性能debug日志
python test_debug_logging.py performance

# 测试错误debug日志
python test_debug_logging.py error

# 测试中间件debug日志
python test_debug_logging.py middleware

# 测试语言切换debug日志
python test_debug_logging.py language

# 运行完整测试
python test_debug_logging.py
```

### **测试结果示例**
```
🐛 测试基础Debug日志功能
========================================
📋 中文Debug日志测试:
2025-07-21 23:11:26,456 | test-debug | DEBUG | 📥 收到API请求: GET /api/test
2025-07-21 23:11:26,456 | test-debug | DEBUG | 🔍 开始验证: symbol
2025-07-21 23:11:26,456 | test-debug | DEBUG | ✅ 验证通过: symbol

📋 英文Debug日志测试:
2025-07-21 23:11:26,456 | test-debug | DEBUG | 📥 API request received: POST /api/data
2025-07-21 23:11:26,456 | test-debug | DEBUG | 🔍 Validation start: date_range
2025-07-21 23:11:26,456 | test-debug | WARNING | 🐌 Slow query warning: SELECT * FROM stocks - 2500ms (threshold: 1000ms)
```

## 🎯 **最佳实践**

### **1. 生产环境配置**
```python
# 生产环境建议关闭debug日志
DEBUG_MODE = False

# 或者只在特定条件下启用
DEBUG_MODE = os.getenv("ENABLE_DEBUG", "false").lower() == "true"
```

### **2. 性能考虑**
```python
# 对于高频操作，使用条件判断
if debug_logger.logger.isEnabledFor(logging.DEBUG):
    debug_logger.debug_cache_check_start(symbol, data_type)
```

### **3. 敏感信息过滤**
```python
# 过滤敏感信息
safe_headers = {}
for key, value in headers.items():
    if key.lower() not in ['authorization', 'cookie', 'x-api-key']:
        safe_headers[key] = value
    else:
        safe_headers[key] = "***"
```

### **4. 日志轮转**
```python
# 配置日志轮转避免日志文件过大
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    'debug.log', maxBytes=10*1024*1024, backupCount=5
)
```

## 🎉 **总结**

现在 TradingAgents 具备了完整的Debug级别国际化日志：

✅ **全面覆盖**: API、数据、缓存、性能、系统等各个方面  
✅ **详细追踪**: 完整的请求/响应生命周期  
✅ **性能监控**: 实时的性能指标和慢查询警告  
✅ **多语言支持**: 中文、英文等多种语言  
✅ **动态控制**: 运行时开启/关闭debug功能  
✅ **易于诊断**: 详细的错误信息和调用栈  

这些debug日志将大大提高系统的可观测性和问题诊断能力！🔍
