# 📊 Data Service API 参考文档

## 🌐 **服务地址**
- **本地开发**: `http://localhost:8002`
- **基础路径**: `/api`

## 📋 **API 分类**

### **1. 🏥 健康检查**

#### `GET /health`
检查服务健康状态
```bash
curl http://localhost:8002/health
```

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-22T02:00:00Z",
  "dependencies": {
    "redis": "connected",
    "mongodb": "connected"
  }
}
```

---

### **2. 📈 股票数据接口**

#### `GET /api/stock/info/{symbol}`
获取股票基本信息
```bash
curl "http://localhost:8002/api/stock/info/AAPL"
```

#### `POST /api/stock/data`
获取股票历史数据
```bash
curl -X POST "http://localhost:8002/api/stock/data" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "start_date": "2024-12-01",
    "end_date": "2024-12-31"
  }'
```

#### `GET /api/stock/fundamentals/{symbol}`
获取股票基本面数据
```bash
curl "http://localhost:8002/api/stock/fundamentals/AAPL?start_date=2024-12-01&end_date=2024-12-31&curr_date=2024-12-31"
```

#### `GET /api/stock/news/{symbol}`
获取股票新闻
```bash
curl "http://localhost:8002/api/stock/news/AAPL"
```

---

### **3. 🚀 增强数据接口 (推荐)**

#### `GET /api/enhanced/stock/{symbol}`
获取增强的股票数据（集成TradingAgents优秀实现）
```bash
curl "http://localhost:8002/api/enhanced/stock/AAPL?start_date=2024-12-01&end_date=2024-12-31&force_refresh=true&clear_all_cache=true"
```

**参数说明**:
- `symbol`: 股票代码 (如: AAPL, 000858, 00700)
- `start_date`: 开始日期 (默认: 2024-12-01)
- `end_date`: 结束日期 (默认: 2024-12-31)
- `force_refresh`: 强制刷新缓存 (默认: false)
- `clear_all_cache`: 清除所有缓存 (默认: false)

#### `GET /api/enhanced/stock/{symbol}/formatted`
获取格式化的增强股票数据
```bash
curl "http://localhost:8002/api/enhanced/stock/AAPL/formatted?force_refresh=true"
```

---

### **4. 🔧 数据源管理接口**

#### `GET /api/data-sources/status`
获取所有数据源状态
```bash
curl "http://localhost:8002/api/data-sources/status"
```

#### `GET /api/data-sources/stats`
获取数据源统计信息
```bash
curl "http://localhost:8002/api/data-sources/stats"
```

#### `POST /api/data-sources/health-check`
手动触发数据源健康检查
```bash
curl -X POST "http://localhost:8002/api/data-sources/health-check"
```

---

### **5. ⚙️ 数据源优先级管理**

#### `GET /api/data-sources/priority/profiles`
获取所有优先级配置文件
```bash
curl "http://localhost:8002/api/data-sources/priority/profiles"
```

#### `GET /api/data-sources/priority/current`
获取当前使用的优先级配置
```bash
curl "http://localhost:8002/api/data-sources/priority/current"
```

#### `POST /api/data-sources/priority/switch`
切换优先级配置文件
```bash
curl -X POST "http://localhost:8002/api/data-sources/priority/switch" \
  -H "Content-Type: application/json" \
  -d '{"profile_name": "professional"}'
```

#### `POST /api/data-sources/priority/reload`
重新加载优先级配置
```bash
curl -X POST "http://localhost:8002/api/data-sources/priority/reload"
```

---

### **6. 💾 本地数据管理**

#### `GET /api/local-data/summary`
获取本地数据存储摘要
```bash
curl "http://localhost:8002/api/local-data/summary"
```

#### `GET /api/local-data/history/{symbol}`
获取特定股票的数据历史
```bash
curl "http://localhost:8002/api/local-data/history/AAPL"
```

#### `POST /api/local-data/cleanup`
清理旧数据
```bash
curl -X POST "http://localhost:8002/api/local-data/cleanup" \
  -H "Content-Type: application/json" \
  -d '{"days": 30}'
```

#### `POST /api/local-data/force-refresh`
强制刷新数据（忽略缓存）
```bash
curl -X POST "http://localhost:8002/api/local-data/force-refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "data_type": "stock_info"
  }'
```

---

### **7. 🔧 管理员接口**

#### `POST /api/admin/batch-update`
批量更新数据
```bash
curl -X POST "http://localhost:8002/api/admin/batch-update" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "MSFT", "GOOGL"],
    "data_types": ["stock_info", "stock_data"],
    "force_refresh": true
  }'
```

#### `POST /api/admin/cleanup-cache`
清理缓存数据
```bash
curl -X POST "http://localhost:8002/api/admin/cleanup-cache" \
  -H "Content-Type: application/json" \
  -d '{
    "data_types": ["stock_info"],
    "older_than_hours": 24
  }'
```

#### `GET /api/admin/statistics`
获取数据统计信息
```bash
curl "http://localhost:8002/api/admin/statistics"
```

#### `POST /api/admin/preheat-cache`
预热缓存
```bash
curl -X POST "http://localhost:8002/api/admin/preheat-cache" \
  -H "Content-Type: application/json" \
  -d '["AAPL", "MSFT", "GOOGL"]'
```

---

### **8. 🌍 国际化接口**

#### `GET /api/i18n/languages`
获取支持的语言列表
```bash
curl "http://localhost:8002/api/i18n/languages"
```

#### `GET /api/i18n/current`
获取当前语言
```bash
curl "http://localhost:8002/api/i18n/current"
```

#### `POST /api/i18n/set-language`
设置语言
```bash
curl -X POST "http://localhost:8002/api/i18n/set-language" \
  -H "Content-Type: application/json" \
  -d '{"language": "zh"}'
```

---

## 🎯 **常用示例**

### **获取美股数据 (推荐)**
```bash
# 使用增强API获取AAPL数据，强制使用新数据源
curl "http://localhost:8002/api/enhanced/stock/AAPL?force_refresh=true&clear_all_cache=true"
```

### **获取A股数据**
```bash
# 获取平安银行数据
curl "http://localhost:8002/api/enhanced/stock/000001?start_date=2024-12-01&end_date=2024-12-31"
```

### **获取港股数据**
```bash
# 获取腾讯控股数据
curl "http://localhost:8002/api/enhanced/stock/00700?start_date=2024-12-01&end_date=2024-12-31"
```

### **检查数据源状态**
```bash
# 查看当前数据源优先级
curl "http://localhost:8002/api/data-sources/priority/current"

# 查看数据源健康状态
curl "http://localhost:8002/api/data-sources/status"
```

---

## 📊 **当前数据源优先级**

### **美股数据源优先级**:
1. **Alpha Vantage** (最高优先级)
2. **Twelve Data** (第二优先级)
3. **FinnHub** (第三优先级)
4. **YFinance** (第四优先级)
5. **AKShare** (备用)

### **A股数据源优先级**:
1. **Tushare** (最高优先级)
2. **AKShare** (第二优先级)
3. **BaoStock** (备用)

### **港股数据源优先级**:
1. **AKShare** (最高优先级)
2. **Twelve Data** (第二优先级)
3. **YFinance** (备用)

---

## 🔍 **响应格式**

所有API都返回统一的响应格式：

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 具体数据内容
  },
  "timestamp": "2025-01-22T02:00:00Z"
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-01-22T02:00:00Z"
}
```

---

## 💡 **使用建议**

1. **推荐使用增强API** (`/api/enhanced/stock/{symbol}`) 获取股票数据
2. **使用 `force_refresh=true`** 获取最新数据
3. **使用 `clear_all_cache=true`** 强制使用新数据源
4. **定期检查数据源状态** 确保服务正常
5. **根据需要切换优先级配置** 优化数据获取策略
