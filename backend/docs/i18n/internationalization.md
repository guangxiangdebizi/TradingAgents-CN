# 🌍 TradingAgents 国际化支持

## 📋 **概述**

TradingAgents 现在支持完整的**国际化（i18n）功能**！系统可以根据用户的语言偏好自动调整界面语言、API响应消息和数据格式。

## ✨ **支持的语言**

- 🇨🇳 **简体中文** (zh-CN) - 默认语言
- 🇹🇼 **繁体中文** (zh-TW)
- 🇺🇸 **美式英语** (en-US) - 回退语言
- 🇬🇧 **英式英语** (en-GB)
- 🇯🇵 **日语** (ja-JP)
- 🇰🇷 **韩语** (ko-KR)

## 🔧 **核心功能**

### **1. 自动语言检测**
- ✅ **HTTP头检测**: 从 `Accept-Language` 头自动检测用户语言
- ✅ **查询参数**: 支持 `?lang=zh-CN` 或 `?language=en-US`
- ✅ **自定义头部**: 支持 `X-Language` 头
- ✅ **Cookie支持**: 从 `language` Cookie 读取语言偏好
- ✅ **智能回退**: 不支持的语言自动回退到默认语言

### **2. API响应国际化**
- ✅ **消息翻译**: 所有API响应消息自动翻译
- ✅ **错误信息**: 错误消息根据语言显示
- ✅ **数据本地化**: 股票数据字段名和格式本地化
- ✅ **响应头**: 自动添加 `Content-Language` 头

### **3. 数据格式本地化**
- ✅ **货币格式**: 根据语言格式化货币显示
- ✅ **数字格式**: 中文使用万/亿，英文使用K/M/B
- ✅ **百分比格式**: 本地化百分比显示
- ✅ **时间格式**: 相对时间的本地化显示

## 🚀 **使用方法**

### **1. API调用时指定语言**

#### **通过查询参数**
```bash
# 获取中文响应
curl "http://localhost:8002/api/stock/info/000858?lang=zh-CN"

# 获取英文响应  
curl "http://localhost:8002/api/stock/info/000858?lang=en-US"

# 获取日文响应
curl "http://localhost:8002/api/stock/info/000858?lang=ja-JP"
```

#### **通过HTTP头**
```bash
# 使用Accept-Language头
curl -H "Accept-Language: en-US,en;q=0.9" \
     "http://localhost:8002/api/stock/info/000858"

# 使用自定义X-Language头
curl -H "X-Language: ja-JP" \
     "http://localhost:8002/api/stock/info/000858"
```

### **2. 语言管理API**

#### **获取支持的语言列表**
```bash
curl "http://localhost:8002/api/i18n/languages"
```

响应示例：
```json
{
  "success": true,
  "message": "获取语言列表成功",
  "data": [
    {"code": "zh-CN", "name": "简体中文"},
    {"code": "en-US", "name": "English (US)"},
    {"code": "ja-JP", "name": "日本語"}
  ]
}
```

#### **获取当前语言**
```bash
curl "http://localhost:8002/api/i18n/current"
```

#### **设置语言**
```bash
curl -X POST "http://localhost:8002/api/i18n/set-language" \
     -H "Content-Type: application/json" \
     -d '{"language": "en-US"}'
```

#### **获取翻译统计**
```bash
curl "http://localhost:8002/api/i18n/stats"
```

### **3. 在代码中使用国际化**

#### **基础翻译**
```python
from backend.shared.i18n import get_i18n_manager, _

# 获取管理器
i18n = get_i18n_manager()

# 设置语言
i18n.set_language("en-US")

# 翻译文本
message = _("api.success.stock_info")
# 或者
message = i18n.translate("api.success.stock_info")

# 带参数的翻译
message = _("time.minutes_ago", minutes=5)
```

#### **创建国际化响应**
```python
from backend.shared.i18n.middleware import i18n_response

# 成功响应
return i18n_response.success_response("api.success.stock_info", data)

# 错误响应
return i18n_response.error_response("api.error.stock_not_found")
```

#### **数据本地化**
```python
from backend.shared.i18n.utils import localize_stock_data

# 本地化股票数据
localized_data = localize_stock_data(stock_data)
```

## 📁 **文件结构**

```
backend/shared/i18n/
├── __init__.py              # 模块入口
├── config.py                # 国际化配置
├── manager.py               # 国际化管理器
├── middleware.py            # FastAPI中间件
├── utils.py                 # 工具函数
└── translations/            # 翻译文件
    ├── zh-CN.json          # 简体中文
    ├── zh-TW.json          # 繁体中文
    ├── en-US.json          # 美式英语
    ├── en-GB.json          # 英式英语
    ├── ja-JP.json          # 日语
    └── ko-KR.json          # 韩语
```

## 🔧 **配置选项**

### **I18nConfig 配置**
```python
from backend.shared.i18n.config import I18nConfig, SupportedLanguage

config = I18nConfig(
    default_language=SupportedLanguage.ZH_CN,  # 默认语言
    fallback_language=SupportedLanguage.EN_US, # 回退语言
    auto_detect=True,                          # 自动检测语言
    cache_translations=True                    # 缓存翻译
)
```

### **中间件配置**
```python
from backend.shared.i18n.middleware import I18nMiddleware

# 添加到FastAPI应用
app.add_middleware(I18nMiddleware, auto_detect=True)
```

## 📝 **翻译文件格式**

翻译文件使用嵌套JSON格式：

```json
{
  "api": {
    "success": {
      "stock_info": "获取股票信息成功",
      "stock_data": "获取股票数据成功"
    },
    "error": {
      "stock_not_found": "未找到股票信息",
      "invalid_symbol": "无效的股票代码"
    }
  },
  "data": {
    "stock": {
      "symbol": "股票代码",
      "name": "股票名称",
      "price": "价格"
    }
  }
}
```

支持参数化翻译：
```json
{
  "time": {
    "minutes_ago": "{minutes}分钟前",
    "hours_ago": "{hours}小时前"
  }
}
```

## 🧪 **测试国际化功能**

### **运行测试脚本**
```bash
cd backend

# 运行完整测试
python test_i18n.py

# 测试特定功能
python test_i18n.py languages    # 测试语言列表
python test_i18n.py current      # 测试当前语言
python test_i18n.py set en-US    # 测试设置语言
python test_i18n.py stats        # 测试翻译统计
python test_i18n.py localization # 测试数据本地化
```

### **测试结果示例**
```
🌍 TradingAgents 国际化功能测试
==================================================
🔍 测试 Data Service 健康状态...
✅ Data Service 健康

🌍 测试获取支持的语言列表...
✅ 支持的语言:
  🔹 zh-CN: 简体中文
  🔹 en-US: English (US)
  🔹 ja-JP: 日本語

📋 测试获取当前语言...
✅ 当前语言: zh-CN (简体中文)

🔧 测试设置语言: en-US
✅ 语言设置成功: en-US

🌐 测试 en-US 语言的API响应...
✅ API响应消息: Stock information retrieved successfully
✅ 响应语言头: en-US
```

## 🌟 **高级功能**

### **1. 自定义翻译**
```python
# 动态添加翻译
i18n.add_translation(SupportedLanguage.ZH_CN, "custom.message", "自定义消息")
i18n.add_translation(SupportedLanguage.EN_US, "custom.message", "Custom Message")
```

### **2. 格式化工具**
```python
from backend.shared.i18n.utils import (
    format_currency, format_percentage, format_volume, 
    format_relative_time, translate_market_type
)

# 格式化货币
formatted = format_currency(1000000, "CNY", SupportedLanguage.ZH_CN)
# 输出: ¥100.00万

# 格式化百分比
formatted = format_percentage(5.67, SupportedLanguage.EN_US)
# 输出: +5.67%

# 翻译市场类型
translated = translate_market_type("A股", SupportedLanguage.EN_US)
# 输出: A-Share
```

### **3. 语言检测**
```python
from backend.shared.i18n.utils import get_language_from_request_header

# 从HTTP头检测语言
lang = get_language_from_request_header("zh-CN,zh;q=0.9,en;q=0.8")
# 返回: SupportedLanguage.ZH_CN
```

## 🔄 **扩展新语言**

### **1. 添加语言枚举**
在 `config.py` 中添加新语言：
```python
class SupportedLanguage(Enum):
    # 现有语言...
    FR_FR = "fr-FR"  # 法语
    DE_DE = "de-DE"  # 德语
```

### **2. 创建翻译文件**
创建 `translations/fr-FR.json`：
```json
{
  "api": {
    "success": {
      "stock_info": "Informations sur les actions récupérées avec succès"
    }
  }
}
```

### **3. 更新语言映射**
在 `config.py` 中更新映射：
```python
LANGUAGE_MAPPING = {
    # 现有映射...
    "fr": SupportedLanguage.FR_FR,
    "fr-fr": SupportedLanguage.FR_FR,
}
```

## 🎯 **最佳实践**

1. **翻译键命名**: 使用层次化的键名，如 `api.success.stock_info`
2. **参数化翻译**: 对于动态内容使用参数，如 `{minutes}分钟前`
3. **回退机制**: 始终提供英文翻译作为回退
4. **测试覆盖**: 为每种语言编写测试用例
5. **性能优化**: 启用翻译缓存以提高性能

## 🎉 **总结**

现在 TradingAgents 具备了完整的国际化支持：

✅ **多语言支持**: 6种主要语言  
✅ **自动检测**: 智能语言检测机制  
✅ **API国际化**: 所有响应消息本地化  
✅ **数据本地化**: 数字、货币、时间格式本地化  
✅ **易于扩展**: 简单的翻译文件管理  
✅ **性能优化**: 翻译缓存和智能回退  

您的 TradingAgents 系统现在可以为全球用户提供本地化体验！🌍
