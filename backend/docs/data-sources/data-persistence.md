# 💾 TradingAgents 数据持久化系统

## 📋 **概述**

TradingAgents 现在具备完整的**数据持久化功能**！所有从数据源获取的数据都会自动保存到本地 MongoDB 数据库中，确保数据的持久性和可追溯性。

## ✨ **核心特性**

- ✅ **自动保存**: 所有获取的数据自动保存到 MongoDB
- ✅ **双重缓存**: Redis + MongoDB 双重缓存策略
- ✅ **历史数据**: 完整的历史数据存储和管理
- ✅ **数据分类**: 按数据类型分别存储到不同集合
- ✅ **元数据记录**: 记录数据来源、更新时间等元信息
- ✅ **数据清理**: 自动清理过期和冗余数据
- ✅ **查询接口**: 提供丰富的数据查询和管理接口

## 🗄️ **数据库结构**

### **MongoDB 集合设计**

```
tradingagents 数据库
├── cached_data          # 缓存数据表
├── stock_info           # 股票基本信息表
├── stock_data           # 股票价格数据表
├── fundamentals         # 基本面数据表
└── news                 # 新闻数据表
```

#### **1. cached_data (缓存数据表)**
```json
{
  "symbol": "000858",
  "data_type": "stock_info",
  "data": { /* 完整的数据结构 */ },
  "source": "tushare",
  "timestamp": "2025-01-21T10:00:00",
  "expires_at": "2025-01-22T10:00:00"
}
```

#### **2. stock_info (股票基本信息表)**
```json
{
  "symbol": "000858",
  "data": {
    "name": "五粮液",
    "industry": "白酒",
    "market_cap": 1000000000
  },
  "source": "tushare",
  "market_type": "a_share",
  "updated_at": "2025-01-21T10:00:00",
  "created_at": "2025-01-21T10:00:00"
}
```

#### **3. stock_data (股票价格数据表)**
```json
{
  "symbol": "000858",
  "date": "2024-01-15",
  "open": 100.0,
  "high": 105.0,
  "low": 98.0,
  "close": 103.0,
  "volume": 1000000,
  "amount": 103000000.0,
  "source": "tushare",
  "market_type": "a_share",
  "updated_at": "2025-01-21T10:00:00"
}
```

#### **4. fundamentals (基本面数据表)**
```json
{
  "symbol": "000858",
  "report_date": "2024-12-31",
  "data": {
    "roe": 15.5,
    "pe_ratio": 20.0,
    "pb_ratio": 2.5
  },
  "source": "tushare",
  "market_type": "a_share",
  "updated_at": "2025-01-21T10:00:00"
}
```

#### **5. news (新闻数据表)**
```json
{
  "symbol": "000858",
  "title": "五粮液发布年报",
  "content": "五粮液发布2024年年报...",
  "publish_time": "2025-01-20T09:00:00",
  "source": "akshare",
  "url": "https://example.com/news/123",
  "market_type": "a_share",
  "updated_at": "2025-01-21T10:00:00"
}
```

## 🔄 **数据流程**

```
用户请求 → 检查缓存 → 数据源获取 → 保存到数据库 → 返回结果
    ↓           ↓           ↓            ↓
  API调用    Redis缓存   数据源工厂    MongoDB存储
```

### **详细流程**

1. **用户请求数据**
2. **检查 Redis 缓存** - 如果有效缓存，直接返回
3. **检查 MongoDB 缓存** - 如果 Redis 失效但 MongoDB 有效，返回并更新 Redis
4. **从数据源获取** - 如果缓存都失效，从数据源获取新数据
5. **保存到数据库** - 同时保存到 Redis 和 MongoDB
6. **保存历史数据** - 保存到对应的历史数据表
7. **返回结果** - 返回给用户

## 🚀 **使用方法**

### **1. 自动数据保存**

数据保存是完全自动的，当您调用任何数据获取接口时，数据会自动保存：

```bash
# 获取股票信息 - 自动保存到 stock_info 表
curl http://localhost:8002/api/stock/info/000858

# 获取股票数据 - 自动保存到 stock_data 表
curl -X POST http://localhost:8002/api/stock/data \
  -H "Content-Type: application/json" \
  -d '{"symbol": "000858", "start_date": "2024-01-01", "end_date": "2024-01-10"}'
```

### **2. 查看本地数据摘要**

```bash
# 查看数据库存储摘要
curl http://localhost:8002/api/local-data/summary
```

### **3. 查看特定股票的数据历史**

```bash
# 查看 000858 的完整数据历史
curl http://localhost:8002/api/local-data/history/000858
```

### **4. 强制刷新数据**

```bash
# 强制从数据源重新获取数据（忽略缓存）
curl -X POST http://localhost:8002/api/local-data/force-refresh \
  -H "Content-Type: application/json" \
  -d '{"symbol": "000858", "data_type": "stock_info"}'
```

### **5. 清理旧数据**

```bash
# 清理30天前的旧数据
curl -X POST http://localhost:8002/api/local-data/cleanup \
  -H "Content-Type: application/json" \
  -d '{"days": 30}'
```

## 🔧 **管理工具**

### **1. 数据持久化测试工具**

```bash
cd backend

# 运行完整的数据持久化测试
python test_data_persistence.py

# 只查看数据摘要
python test_data_persistence.py summary

# 查看特定股票的数据历史
python test_data_persistence.py history 000858

# 强制刷新数据
python test_data_persistence.py refresh 000858

# 清理旧数据
python test_data_persistence.py cleanup
```

### **2. MongoDB 数据查看工具**

```bash
cd backend

# 查看集合信息
python mongodb_data_viewer.py info

# 查看缓存数据
python mongodb_data_viewer.py cache

# 查看股票数据
python mongodb_data_viewer.py stock 000858

# 查看数据统计
python mongodb_data_viewer.py stats

# 清理测试数据
python mongodb_data_viewer.py cleanup

# 导出股票数据
python mongodb_data_viewer.py export 000858 data.json
```

## 📊 **缓存策略**

### **Redis 缓存 (短期)**
- **股票信息**: 1小时
- **股票数据**: 30分钟
- **基本面数据**: 6小时
- **新闻数据**: 30分钟

### **MongoDB 缓存 (中期)**
- **股票信息**: 24小时
- **股票数据**: 1小时
- **基本面数据**: 6小时
- **新闻数据**: 30分钟

### **历史数据 (长期)**
- **股票信息**: 永久保存，更新时覆盖
- **股票数据**: 按日期保存，永久保存
- **基本面数据**: 按报告期保存，永久保存
- **新闻数据**: 按发布时间保存，定期清理

## 🔍 **数据查询示例**

### **通过 API 查询**

```bash
# 获取本地数据摘要
curl http://localhost:8002/api/local-data/summary

# 获取股票数据历史
curl http://localhost:8002/api/local-data/history/000858
```

### **直接查询 MongoDB**

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.tradingagents

# 查询股票信息
stock_info = db.stock_info.find_one({"symbol": "000858"})

# 查询最近的股票数据
stock_data = list(db.stock_data.find({"symbol": "000858"}).sort("date", -1).limit(10))

# 查询基本面数据
fundamentals = list(db.fundamentals.find({"symbol": "000858"}))

# 查询新闻数据
news = list(db.news.find({"symbol": "000858"}).sort("publish_time", -1).limit(20))
```

## 🧹 **数据清理**

### **自动清理策略**
- **过期缓存**: 自动清理过期的缓存数据
- **旧新闻**: 清理30天前的新闻数据
- **重复数据**: 防止重复数据插入

### **手动清理**
```bash
# 通过 API 清理
curl -X POST http://localhost:8002/api/local-data/cleanup \
  -d '{"days": 30}'

# 通过工具清理
python mongodb_data_viewer.py cleanup
```

## 📈 **性能优化**

### **索引优化**
```javascript
// MongoDB 索引建议
db.stock_info.createIndex({"symbol": 1})
db.stock_data.createIndex({"symbol": 1, "date": -1})
db.fundamentals.createIndex({"symbol": 1, "report_date": -1})
db.news.createIndex({"symbol": 1, "publish_time": -1})
db.cached_data.createIndex({"symbol": 1, "data_type": 1})
db.cached_data.createIndex({"expires_at": 1})
```

### **查询优化**
- 使用复合索引提高查询性能
- 限制查询结果数量
- 使用投影减少数据传输

## 🔧 **故障排除**

### **常见问题**

1. **数据没有保存到 MongoDB**
   ```bash
   # 检查 MongoDB 连接
   python mongodb_data_viewer.py info
   
   # 查看服务日志
   docker logs tradingagents-data-service
   ```

2. **缓存不生效**
   ```bash
   # 检查 Redis 连接
   redis-cli ping
   
   # 查看 Redis 键
   redis-cli keys "data:*"
   ```

3. **数据格式错误**
   ```bash
   # 强制刷新数据
   python test_data_persistence.py refresh 000858
   ```

## 📊 **监控和统计**

### **数据统计**
```bash
# 查看数据统计
python mongodb_data_viewer.py stats

# API 方式查看
curl http://localhost:8002/api/local-data/summary
```

### **性能监控**
- 监控数据库大小
- 监控查询性能
- 监控缓存命中率

## 🎉 **总结**

现在 TradingAgents 具备了完整的数据持久化能力：

✅ **自动保存**: 所有数据自动保存到 MongoDB  
✅ **智能缓存**: Redis + MongoDB 双重缓存  
✅ **历史追踪**: 完整的数据历史记录  
✅ **灵活查询**: 丰富的查询和管理接口  
✅ **性能优化**: 索引优化和查询优化  
✅ **数据清理**: 自动和手动数据清理  
✅ **监控工具**: 完善的数据查看和管理工具  

您的数据现在安全地存储在本地，随时可以查询和分析！🚀

### **快速验证**

```bash
# 1. 获取一些数据
curl http://localhost:8002/api/stock/info/000858

# 2. 查看是否保存成功
python mongodb_data_viewer.py stock 000858

# 3. 查看数据摘要
python test_data_persistence.py summary
```
