# 📊 TradingAgents 数据源优先级配置

## 🎯 **更新内容**

根据您的建议，我们已经调整了美股数据源的优先级配置，**FinnHub 现在是美股数据的首选数据源**。

## 📈 **数据源优先级配置**

### **A股市场** 🇨🇳
| 数据类别 | 优先级顺序 | 说明 |
|---------|-----------|------|
| 基本信息 | **Tushare** → AKShare | Tushare 数据最全面 |
| 价格数据 | **Tushare** → AKShare → BaoStock | Tushare 数据质量最高 |
| 基本面数据 | **Tushare** → AKShare | Tushare 财务数据最专业 |
| 新闻数据 | **AKShare** | AKShare 新闻覆盖较好 |

### **美股市场** 🇺🇸
| 数据类别 | 优先级顺序 | 说明 |
|---------|-----------|------|
| 基本信息 | **FinnHub** → YFinance → AKShare | FinnHub 美股信息最全面 |
| 价格数据 | **FinnHub** → YFinance → AKShare | FinnHub 数据质量高，频率限制合理 |
| 基本面数据 | **FinnHub** → YFinance | FinnHub 财务指标丰富 |
| 新闻数据 | **FinnHub** → AKShare | FinnHub 新闻质量高，带情感分析 |

### **港股市场** 🇭🇰
| 数据类别 | 优先级顺序 | 说明 |
|---------|-----------|------|
| 基本信息 | **AKShare** → YFinance | AKShare 港股支持较好 |
| 价格数据 | **AKShare** → YFinance | AKShare 数据更新及时 |
| 新闻数据 | **AKShare** | AKShare 港股新闻覆盖 |

## ⚡ **频率限制配置**

| 数据源 | 频率限制 | 说明 |
|-------|---------|------|
| **Tushare** | 200次/分钟 | Pro版本，A股首选 |
| **FinnHub** | 60次/分钟 | 免费版，美股首选 |
| **AKShare** | 100次/分钟 | 开源免费，多市场支持 |
| **BaoStock** | 60次/分钟 | 免费，A股历史数据 ✨ |
| **YFinance** | 30次/分钟 | ⚠️ 限制较严，降为备用 ✨ |

## 🔧 **配置文件结构**

```
backend/data-service/app/datasources/
├── base.py              # 基础抽象类和接口
├── factory.py           # 数据源工厂类
├── config.py            # 配置管理器
├── tushare_source.py    # Tushare 数据源实现
├── akshare_source.py    # AKShare 数据源实现
├── finnhub_source.py    # FinnHub 数据源实现 ✨
├── baostock_source.py   # BaoStock 数据源实现 ✨ 新增
└── yfinance_source.py   # YFinance 数据源实现 ✨ 新增
```

## 🚀 **使用方法**

### **1. 配置API密钥**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置API密钥
TUSHARE_TOKEN=your_tushare_token_here
FINNHUB_API_KEY=your_finnhub_api_key_here
```

### **2. 验证配置**
```bash
# 验证数据源配置
cd backend
python validate_data_sources_config.py

# 测试数据源工厂
python test_data_sources.py

# 完整测试所有数据源
python test_all_data_sources.py
```

### **3. 在代码中使用**
```python
from datasources.factory import get_data_source_factory
from datasources.base import MarketType

# 获取数据源工厂
factory = get_data_source_factory()

# 自动检测市场类型
market_type = factory.detect_market_type("AAPL")  # 返回 MarketType.US_STOCK

# 获取美股信息（自动使用 FinnHub）
stock_info = await factory.get_stock_info("AAPL", market_type)
```

## 📊 **FinnHub 数据源特性**

### **支持的数据类型**
- ✅ **基本信息**: 公司名称、行业、市值、股本等
- ✅ **价格数据**: OHLCV 日线数据
- ✅ **基本面数据**: PE、PB、ROE、ROA、财务比率等
- ✅ **新闻数据**: 公司新闻 + 情感分析

### **数据质量优势**
- 🎯 **专业性**: 专门针对美股市场优化
- 📈 **实时性**: 数据更新及时
- 🔍 **准确性**: 数据质量高，错误率低
- 💡 **增值服务**: 提供情感分析等增值数据

### **API限制**
- 🆓 **免费版**: 60次/分钟，足够日常使用
- 💰 **付费版**: 更高频率限制和更多功能
- 🔐 **认证**: 需要API密钥

## 🔄 **智能降级策略**

当数据源不可用时，系统会自动降级：

```
FinnHub 失败 → YFinance → AKShare → 原有统一工具
```

1. **主数据源失败**: 自动切换到次优数据源
2. **所有新数据源失败**: 降级到原有统一工具
3. **完全失败**: 返回缓存数据（如果可用）

## 📈 **性能优化**

### **缓存策略**
- **基本信息**: 缓存24小时
- **价格数据**: 缓存1小时
- **基本面数据**: 缓存6小时
- **新闻数据**: 缓存30分钟

### **请求优化**
- **批量请求**: 支持批量获取数据
- **并发控制**: 避免超出频率限制
- **重试机制**: 智能重试和退避策略

## 🔍 **监控和调试**

### **健康检查**
```bash
# 检查所有数据源状态
curl http://localhost:8002/api/data-sources/status

# 获取数据源统计
curl http://localhost:8002/api/data-sources/stats
```

### **调试工具**
```bash
# 启动调试环境
cd backend
python debug_data_sync.py

# 监控 Celery 任务
python scripts/monitor_celery.py
```

## 💡 **最佳实践**

### **API密钥管理**
1. **必需配置**: `TUSHARE_TOKEN` (A股) + `FINNHUB_API_KEY` (美股)
2. **安全存储**: 使用环境变量，不要硬编码
3. **权限控制**: 定期轮换API密钥

### **频率控制**
1. **合理间隔**: 避免短时间内大量请求
2. **批量操作**: 优先使用批量接口
3. **缓存利用**: 充分利用本地缓存

### **错误处理**
1. **优雅降级**: 数据源失败时自动切换
2. **错误记录**: 详细记录错误信息
3. **监控告警**: 及时发现数据源问题

## 🎉 **总结**

通过这次优化，我们实现了：

1. ✅ **FinnHub 优先**: 美股数据现在优先使用 FinnHub
2. ✅ **智能路由**: 根据市场类型自动选择最佳数据源
3. ✅ **容错机制**: 数据源失败时自动降级
4. ✅ **配置灵活**: 支持动态调整优先级
5. ✅ **监控完善**: 全面的健康检查和统计

这样的配置确保了：
- **A股数据**: 使用 Tushare 获得最专业的数据
- **美股数据**: 使用 FinnHub 获得最优质的数据
- **港股数据**: 使用 AKShare 获得较好的覆盖
- **容错保障**: 任何数据源失败都有备用方案

## 📈 **新增数据源特性**

### **BaoStock 数据源** ✨
- ✅ **完全免费**: 无需API密钥，开箱即用
- ✅ **A股专业**: 专门针对A股市场设计
- ✅ **历史数据丰富**: 提供完整的历史价格数据
- ✅ **基本面支持**: 提供基础的财务指标
- ⚠️ **需要登录**: 每次使用需要登录/登出
- 📊 **数据类型**: 基本信息、价格数据、部分基本面

### **YFinance 数据源** ✨
- ✅ **多市场支持**: 美股、港股数据
- ✅ **基本面丰富**: 提供详细的财务指标和比率
- ✅ **新闻支持**: 提供股票相关新闻
- ✅ **免费使用**: 无需API密钥
- ⚠️ **频率限制严格**: 30次/分钟，需要控制请求频率
- 📊 **数据类型**: 基本信息、价格数据、基本面、新闻

### **完整数据源对比**

| 数据源 | 市场支持 | API密钥 | 频率限制 | 数据质量 | 特色功能 |
|-------|---------|---------|----------|----------|----------|
| **Tushare** | A股 | 需要 | 200/分钟 | ⭐⭐⭐⭐⭐ | 专业财务数据 |
| **FinnHub** | 美股 | 需要 | 60/分钟 | ⭐⭐⭐⭐⭐ | 情感分析 |
| **AKShare** | 多市场 | 无需 | 100/分钟 | ⭐⭐⭐⭐ | 开源免费 |
| **BaoStock** | A股 | 无需 | 60/分钟 | ⭐⭐⭐ | 历史数据丰富 |
| **YFinance** | 美股/港股 | 无需 | 30/分钟 | ⭐⭐⭐ | 基本面详细 |

现在您可以放心使用这个完整的数据源管理系统了！🚀
