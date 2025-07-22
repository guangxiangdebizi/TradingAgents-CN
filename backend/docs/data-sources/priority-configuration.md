# 🎯 数据源优先级管理系统

## 📋 **概述**

TradingAgents 现在支持**完全可配置的数据源优先级管理**！您可以根据个人喜好、数据质量要求、成本考虑等因素，灵活调整数据源的优先级顺序。

## ✨ **核心特性**

- ✅ **多种预设配置**: 提供5种预设配置文件，满足不同需求
- ✅ **动态切换**: 运行时无需重启即可切换配置
- ✅ **自定义优先级**: 支持针对特定市场和数据类型设置优先级
- ✅ **配置持久化**: 配置自动保存，重启后保持设置
- ✅ **命令行工具**: 提供便捷的CLI管理工具
- ✅ **API接口**: 支持通过API动态管理配置
- ✅ **配置导入导出**: 支持配置文件的备份和分享

## 📊 **预设配置文件**

### **1. default (默认配置)**
平衡的数据源优先级配置，兼顾数据质量和可用性
```
A股: Tushare → AKShare → BaoStock
美股: FinnHub → YFinance → AKShare
港股: AKShare → YFinance
```

### **2. akshare_first (AKShare 优先)** ⭐
**适合喜欢开源免费数据源的用户**
```
A股: AKShare → Tushare → BaoStock
美股: AKShare → FinnHub → YFinance
港股: AKShare → YFinance
```

### **3. professional (专业配置)**
优先使用付费专业数据源，数据质量最高
```
A股: Tushare → AKShare
美股: FinnHub → YFinance
港股: YFinance → AKShare
```

### **4. free_only (免费配置)**
只使用免费数据源，无需API密钥
```
A股: AKShare → BaoStock
美股: AKShare → YFinance
港股: AKShare → YFinance
```

### **5. speed_first (速度优先)**
优先使用响应速度快的数据源
```
A股: AKShare → BaoStock → Tushare
美股: YFinance → AKShare → FinnHub
港股: YFinance → AKShare
```

## 🔧 **使用方法**

### **方法1: 命令行工具** (推荐)

```bash
cd backend

# 查看当前配置
python manage_data_source_priority.py show

# 列出所有配置文件
python manage_data_source_priority.py list

# 切换到 AKShare 优先配置
python manage_data_source_priority.py switch akshare_first

# 交互式设置自定义优先级
python manage_data_source_priority.py custom

# 创建自定义配置文件
python manage_data_source_priority.py create my_config "我的配置" default

# 导出配置
python manage_data_source_priority.py export my_config.json

# 导入配置
python manage_data_source_priority.py import my_config.json

# 查看数据源详细信息
python manage_data_source_priority.py info
```

### **方法2: API 接口**

```bash
# 获取所有配置文件
curl http://localhost:8002/api/data-sources/priority/profiles

# 获取当前配置
curl http://localhost:8002/api/data-sources/priority/current

# 切换配置文件
curl -X POST http://localhost:8002/api/data-sources/priority/switch \
  -H "Content-Type: application/json" \
  -d '{"profile_name": "akshare_first"}'

# 重新加载配置
curl -X POST http://localhost:8002/api/data-sources/priority/reload
```

### **方法3: 直接编辑配置文件**

编辑 `backend/data-service/app/datasources/priority_config.json`：

```json
{
  "current_profile": "akshare_first",
  "priority_profiles": {
    "my_custom": {
      "name": "我的自定义配置",
      "description": "根据我的需求定制",
      "priorities": {
        "a_share_basic_info": ["akshare", "tushare", "baostock"],
        "a_share_price_data": ["akshare", "baostock", "tushare"]
      }
    }
  }
}
```

## 🚀 **快速开始**

### **场景1: 我喜欢使用 AKShare 作为 A股 的主要数据源**

```bash
# 切换到 AKShare 优先配置
python manage_data_source_priority.py switch akshare_first

# 验证配置
python manage_data_source_priority.py show
```

### **场景2: 我只想使用免费数据源**

```bash
# 切换到免费配置
python manage_data_source_priority.py switch free_only

# 查看配置详情
python manage_data_source_priority.py show
```

### **场景3: 我要自定义 A股基本信息的优先级**

```bash
# 运行交互式配置工具
python manage_data_source_priority.py custom

# 按提示选择:
# 1. 选择市场: 1 (A股)
# 2. 选择数据类别: 1 (基本信息)  
# 3. 输入优先级: akshare,baostock,tushare
```

### **场景4: 我要创建自己的配置文件**

```bash
# 创建基于默认配置的自定义配置
python manage_data_source_priority.py create my_config "我的专属配置" default

# 切换到自定义配置
python manage_data_source_priority.py switch my_config

# 设置自定义优先级
python manage_data_source_priority.py custom
```

## 📊 **演示和测试**

```bash
# 运行完整演示
python priority_config_demo.py

# 测试所有数据源
python test_all_data_sources.py

# 验证配置
python validate_data_sources_config.py
```

## 🔍 **配置文件结构**

```json
{
  "version": "1.0",
  "current_profile": "当前使用的配置文件名",
  "priority_profiles": {
    "配置文件名": {
      "name": "显示名称",
      "description": "配置描述", 
      "priorities": {
        "a_share_basic_info": ["数据源1", "数据源2"],
        "a_share_price_data": ["数据源1", "数据源2"],
        "us_stock_basic_info": ["数据源1", "数据源2"]
      }
    }
  },
  "data_source_info": {
    "数据源详细信息..."
  }
}
```

## 🎯 **优先级键值对照表**

| 配置键 | 说明 |
|-------|------|
| `a_share_basic_info` | A股基本信息 |
| `a_share_price_data` | A股价格数据 |
| `a_share_fundamentals` | A股基本面数据 |
| `a_share_news` | A股新闻数据 |
| `us_stock_basic_info` | 美股基本信息 |
| `us_stock_price_data` | 美股价格数据 |
| `us_stock_fundamentals` | 美股基本面数据 |
| `us_stock_news` | 美股新闻数据 |
| `hk_stock_basic_info` | 港股基本信息 |
| `hk_stock_price_data` | 港股价格数据 |
| `hk_stock_news` | 港股新闻数据 |

## 📈 **数据源对比**

| 数据源 | 优势 | 劣势 | 适用场景 |
|-------|------|------|----------|
| **tushare** | 数据质量高、更新及时 | 需要API密钥 | 专业A股分析 |
| **akshare** | 免费、多市场、开源 | 稳定性一般 | 个人学习、快速原型 |
| **finnhub** | 美股专业、实时性好 | 需要API密钥、主要支持美股 | 专业美股分析 |
| **baostock** | 免费、历史数据丰富 | 只支持A股、实时性一般 | A股历史分析 |
| **yfinance** | 免费、全球市场 | 频率限制严格 | 全球股票基础分析 |

## 💡 **最佳实践**

### **1. 根据使用场景选择配置**
- **学习研究**: 使用 `free_only` 或 `akshare_first`
- **专业分析**: 使用 `professional` 或 `default`
- **快速原型**: 使用 `speed_first`

### **2. 合理设置优先级**
- 将最可靠的数据源放在第一位
- 将免费数据源作为备选
- 考虑API频率限制

### **3. 定期检查和调整**
- 监控数据源的可用性和质量
- 根据实际使用情况调整优先级
- 备份重要的配置文件

### **4. 团队协作**
- 导出配置文件分享给团队成员
- 建立统一的配置标准
- 文档化自定义配置的原因

## 🔧 **故障排除**

### **常见问题**

1. **配置切换不生效**
   ```bash
   # 重新加载配置
   python manage_data_source_priority.py show
   # 或通过API
   curl -X POST http://localhost:8002/api/data-sources/priority/reload
   ```

2. **配置文件损坏**
   ```bash
   # 删除配置文件，系统会自动创建默认配置
   rm backend/data-service/app/datasources/priority_config.json
   ```

3. **自定义配置丢失**
   ```bash
   # 导出配置备份
   python manage_data_source_priority.py export backup_config.json
   ```

## 🎉 **总结**

现在您可以：

✅ **灵活配置**: 根据个人喜好调整数据源优先级  
✅ **动态切换**: 运行时切换不同的配置文件  
✅ **自定义设置**: 针对特定需求设置优先级  
✅ **便捷管理**: 使用CLI工具或API接口管理  
✅ **配置共享**: 导出配置文件与他人分享  

**特别适合喜欢 AKShare 的用户** - 只需一条命令即可切换到 AKShare 优先配置！

```bash
python manage_data_source_priority.py switch akshare_first
```

享受完全可控的数据源管理体验！🚀
