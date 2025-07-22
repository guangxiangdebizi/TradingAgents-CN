# 🔧 Backend 工具

## 📋 工具目录

### 🌐 数据源工具 (data-sources/)
- `manage_priority.py` - 数据源优先级管理
- `priority_config_demo.py` - 优先级配置演示
- `validate_config.py` - 数据源配置验证

### 🐛 调试工具 (debugging/)
- `debug_data_service_internal.py` - 数据服务内部调试
- `debug_data_sync.py` - 数据同步调试
- `diagnose_data_sources.py` - 数据源诊断
- `mongodb_data_viewer.py` - MongoDB数据查看器

### ⚙️ 设置工具 (setup/)
- `setup_api_keys.py` - API密钥配置助手

### ✅ 验证工具 (validation/)
- `validate_json_config.py` - JSON配置文件验证

## 🚀 使用方法

```bash
# 配置API密钥
python tools/setup/setup_api_keys.py

# 管理数据源优先级
python tools/data-sources/manage_priority.py

# 诊断数据源问题
python tools/debugging/diagnose_data_sources.py

# 验证配置文件
python tools/validation/validate_json_config.py
```
