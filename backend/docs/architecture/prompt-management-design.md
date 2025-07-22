# 🎯 提示词管理系统设计

## 📍 **设计背景**

不同的大模型有不同的特点和优势，需要针对性的提示词优化：

- **DeepSeek**: 中文理解强，适合金融分析和代码生成
- **OpenAI GPT**: 英文表达好，逻辑推理强
- **阿里百炼**: 中文原生，本土化场景优秀
- **Google Gemini**: 多模态能力强
- **Claude**: 安全性高，长文本处理好

## 🏗️ **架构设计**

### **目录结构**
```
backend/llm-service/app/prompts/
├── 📄 prompt_manager.py          # 提示词管理器
├── 📁 templates/                 # 提示词模板目录
│   ├── 📄 model_mappings.yaml    # 模型映射配置
│   ├── 📁 deepseek/              # DeepSeek专用模板
│   │   ├── 📄 financial_analysis.yaml
│   │   └── 📄 code_generation.yaml
│   ├── 📁 openai/                # OpenAI专用模板
│   │   ├── 📄 financial_analysis.yaml
│   │   └── 📄 code_generation.yaml
│   ├── 📁 qwen/                  # 阿里百炼模板
│   ├── 📁 gemini/                # Google Gemini模板
│   ├── 📁 claude/                # Claude模板
│   └── 📁 general/               # 通用模板
│       └── 📄 general.yaml
└── 📁 __init__.py
```

### **核心组件**

#### **1. PromptTemplate 类**
```python
class PromptTemplate:
    def __init__(self, template_data):
        self.id = template_data.get("id")
        self.model_type = template_data.get("model_type")
        self.task_type = template_data.get("task_type")
        self.language = template_data.get("language")
        self.system_prompt = template_data.get("system_prompt")
        self.user_prompt_template = template_data.get("user_prompt_template")
        self.variables = template_data.get("variables", [])
    
    def format_prompt(self, variables: Dict) -> Tuple[str, str]:
        """格式化提示词，返回(system_prompt, user_prompt)"""
```

#### **2. PromptManager 类**
```python
class PromptManager:
    async def load_templates(self):
        """从YAML文件加载所有模板"""
    
    def get_prompt_template(self, model: str, task_type: str, language: str):
        """获取指定模型和任务的提示词模板"""
    
    def format_messages(self, model: str, task_type: str, variables: Dict):
        """格式化为标准消息格式"""
```

## 📝 **模板格式规范**

### **YAML模板结构**
```yaml
# 模板基本信息
id: "deepseek_financial_analysis_zh"
name: "DeepSeek金融分析模板"
description: "针对DeepSeek模型优化的中文金融分析提示词"
version: "1.0"
language: "zh"
task_type: "financial_analysis"
model_type: "deepseek"

# 系统提示词
system_prompt: |
  你是一位资深的股票分析师，拥有15年的金融市场经验...
  
  ## 你的专业能力：
  - 📊 技术分析：熟练运用各种技术指标
  - 📈 基本面分析：深入理解财务报表
  ...

# 用户提示词模板
user_prompt_template: |
  请对 **{symbol}** ({company_name}) 进行全面的投资分析。
  
  ## 可用数据：
  {stock_data}
  
  ## 分析要求：
  1. 📊 基本面分析
  2. 📈 技术面分析
  ...

# 变量定义
variables:
  - name: "symbol"
    type: "string"
    description: "股票代码"
    required: true
  - name: "company_name"
    type: "string"
    description: "公司名称"
    required: true

# 示例
examples:
  - variables:
      symbol: "AAPL"
      company_name: "苹果公司"
    expected_output: |
      # AAPL 投资分析报告...
```

## 🎯 **智能路由策略**

### **1. 模型映射配置**
```yaml
# model_mappings.yaml
deepseek-chat:
  financial_analysis: "deepseek_financial_analysis_zh"
  code_generation: "deepseek_code_generation_zh"
  general: "general_assistant_zh"

gpt-4:
  financial_analysis: "openai_financial_analysis_zh"
  code_generation: "openai_code_generation_en"
  general: "general_assistant_zh"
```

### **2. 选择优先级**
1. **精确匹配**: 模型名 + 任务类型 + 语言
2. **模型类型匹配**: 模型类型 + 任务类型 + 语言
3. **通用任务匹配**: 通用模型 + 任务类型 + 语言
4. **默认模板**: 通用助手模板

### **3. 自动降级**
```python
def get_prompt_template(self, model: str, task_type: str, language: str):
    # 1. 尝试精确匹配
    template_id = self.model_mappings.get(model, {}).get(task_type)
    if template_id and template_id in self.templates:
        return self.templates[template_id]
    
    # 2. 尝试模型类型匹配
    model_type = self._get_model_type(model)
    for template in self.templates.values():
        if (template.model_type == model_type and 
            template.task_type == task_type and 
            template.language == language):
            return template
    
    # 3. 使用通用模板
    return self._get_general_template(language)
```

## 🔧 **API接口**

### **1. 获取模板列表**
```http
GET /api/v1/prompts/templates?model_type=deepseek&task_type=financial_analysis
```

### **2. 获取统计信息**
```http
GET /api/v1/prompts/stats
```

### **3. 重新加载模板**
```http
POST /api/v1/admin/reload-prompts
```

### **4. 使用提示词的聊天**
```http
POST /api/v1/chat/completions
{
  "model": "deepseek-chat",
  "task_type": "financial_analysis",
  "messages": [
    {"role": "user", "content": "分析AAPL股票"}
  ]
}
```

## 🎨 **模型特化示例**

### **DeepSeek 金融分析模板**
```yaml
system_prompt: |
  你是一位资深的股票分析师，拥有15年的金融市场经验。
  
  ## 分析框架：
  1. **公司基本面**：财务健康度、盈利能力、成长性
  2. **行业地位**：市场份额、竞争优势、护城河
  3. **技术面分析**：价格趋势、支撑阻力、交易量
  ...
```

### **OpenAI 金融分析模板**
```yaml
system_prompt: |
  You are a senior financial analyst with extensive experience in equity research.
  
  ## Analysis Framework:
  1. **Company Fundamentals**: Financial health, profitability, growth
  2. **Industry Position**: Market share, competitive advantages
  3. **Technical Analysis**: Price trends, support/resistance
  ...
```

## 📊 **使用统计**

### **模板使用情况**
```json
{
  "total_templates": 15,
  "by_model_type": {
    "deepseek": 5,
    "openai": 4,
    "qwen": 3,
    "general": 3
  },
  "by_task_type": {
    "financial_analysis": 4,
    "code_generation": 4,
    "general": 7
  },
  "by_language": {
    "zh": 12,
    "en": 3
  }
}
```

## 🚀 **扩展优势**

### **1. 易于维护**
- 📝 **YAML格式**: 人类可读，易于编辑
- 🔄 **热更新**: 无需重启服务即可更新模板
- 📊 **版本管理**: 支持模板版本控制

### **2. 高度灵活**
- 🎯 **任务特化**: 针对不同任务优化提示词
- 🤖 **模型特化**: 发挥每个模型的优势
- 🌍 **多语言**: 支持中英文等多种语言

### **3. 性能优化**
- ⚡ **智能缓存**: 模板加载后缓存在内存
- 🔄 **懒加载**: 按需加载模板文件
- 📈 **批量处理**: 支持批量模板操作

### **4. 开发友好**
- 🧪 **测试支持**: 内置模板验证和测试
- 📚 **文档完整**: 详细的模板文档和示例
- 🔧 **调试工具**: 提供模板调试和预览功能

## 🎯 **最佳实践**

### **1. 模板设计原则**
- **明确角色**: 给AI明确的角色定位
- **结构化输出**: 使用markdown格式化输出
- **示例驱动**: 提供具体的输出示例
- **错误处理**: 考虑边界情况和错误处理

### **2. 变量命名规范**
- **语义化**: 使用有意义的变量名
- **类型明确**: 明确变量类型和格式
- **必填标记**: 区分必填和可选变量
- **默认值**: 为可选变量提供合理默认值

### **3. 版本管理**
- **语义版本**: 使用语义化版本号
- **变更日志**: 记录模板变更历史
- **向后兼容**: 保持API向后兼容
- **渐进升级**: 支持模板渐进式升级

这个提示词管理系统为LLM Service提供了强大的模板管理能力，让每个模型都能发挥最佳性能！🎯
