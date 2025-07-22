#!/usr/bin/env python3
"""
提示词管理器
支持多模型、多任务、多语言的提示词管理
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class PromptTemplate:
    """提示词模板"""
    
    def __init__(self, template_data: Dict[str, Any]):
        self.id = template_data.get("id")
        self.name = template_data.get("name")
        self.description = template_data.get("description")
        self.version = template_data.get("version", "1.0")
        self.language = template_data.get("language", "zh")
        self.task_type = template_data.get("task_type")
        self.model_type = template_data.get("model_type", "general")
        self.system_prompt = template_data.get("system_prompt", "")
        self.user_prompt_template = template_data.get("user_prompt_template", "")
        self.variables = template_data.get("variables", [])
        self.examples = template_data.get("examples", [])
        self.created_at = template_data.get("created_at", datetime.now().isoformat())
        self.updated_at = template_data.get("updated_at", datetime.now().isoformat())
    
    def format_prompt(self, variables: Dict[str, Any] = None) -> Tuple[str, str]:
        """
        格式化提示词
        
        Returns:
            (system_prompt, user_prompt)
        """
        variables = variables or {}
        
        try:
            # 格式化系统提示词
            system_prompt = self.system_prompt.format(**variables)
            
            # 格式化用户提示词
            user_prompt = self.user_prompt_template.format(**variables)
            
            return system_prompt, user_prompt
            
        except KeyError as e:
            logger.error(f"提示词变量缺失: {e}")
            raise ValueError(f"提示词变量缺失: {e}")
    
    def validate_variables(self, variables: Dict[str, Any]) -> List[str]:
        """验证变量是否完整"""
        missing_vars = []
        for var in self.variables:
            var_name = var.get("name")
            if var.get("required", True) and var_name not in variables:
                missing_vars.append(var_name)
        return missing_vars
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "language": self.language,
            "task_type": self.task_type,
            "model_type": self.model_type,
            "system_prompt": self.system_prompt,
            "user_prompt_template": self.user_prompt_template,
            "variables": self.variables,
            "examples": self.examples,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class PromptManager:
    """提示词管理器"""
    
    def __init__(self, prompts_dir: str = None):
        self.prompts_dir = Path(prompts_dir or Path(__file__).parent / "templates")
        self.templates: Dict[str, PromptTemplate] = {}
        self.model_mappings: Dict[str, Dict[str, str]] = {}
        self._last_reload = None
        
        # 确保目录存在
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
    
    async def load_templates(self):
        """加载所有提示词模板"""
        logger.info(f"🔄 加载提示词模板: {self.prompts_dir}")
        
        try:
            # 清空现有模板
            self.templates.clear()
            
            # 加载模板文件
            template_files = list(self.prompts_dir.glob("**/*.yaml")) + list(self.prompts_dir.glob("**/*.yml"))
            
            for template_file in template_files:
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = yaml.safe_load(f)
                    
                    # 支持单个模板或多个模板
                    if isinstance(template_data, list):
                        for item in template_data:
                            template = PromptTemplate(item)
                            self.templates[template.id] = template
                    else:
                        template = PromptTemplate(template_data)
                        self.templates[template.id] = template
                    
                    logger.debug(f"✅ 加载模板: {template_file.name}")
                    
                except Exception as e:
                    logger.error(f"❌ 加载模板失败 {template_file}: {e}")
            
            # 加载模型映射配置
            await self._load_model_mappings()
            
            self._last_reload = datetime.now()
            logger.info(f"✅ 提示词模板加载完成，共{len(self.templates)}个模板")
            
        except Exception as e:
            logger.error(f"❌ 加载提示词模板失败: {e}")
    
    async def _load_model_mappings(self):
        """加载模型映射配置"""
        mapping_file = self.prompts_dir / "model_mappings.yaml"
        
        if mapping_file.exists():
            try:
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    self.model_mappings = yaml.safe_load(f) or {}
                logger.info(f"✅ 加载模型映射配置: {len(self.model_mappings)}个模型")
            except Exception as e:
                logger.error(f"❌ 加载模型映射配置失败: {e}")
                self.model_mappings = {}
        else:
            # 创建默认映射配置
            await self._create_default_model_mappings()
    
    async def _create_default_model_mappings(self):
        """创建默认模型映射配置"""
        default_mappings = {
            "deepseek-chat": {
                "financial_analysis": "deepseek_financial_analysis_zh",
                "code_generation": "deepseek_code_generation_zh",
                "data_extraction": "deepseek_data_extraction_zh",
                "reasoning": "deepseek_reasoning_zh",
                "general": "deepseek_general_zh"
            },
            "gpt-4": {
                "financial_analysis": "openai_financial_analysis_zh",
                "code_generation": "openai_code_generation_en",
                "data_extraction": "openai_data_extraction_zh",
                "reasoning": "openai_reasoning_zh",
                "general": "openai_general_zh"
            },
            "qwen-plus": {
                "financial_analysis": "qwen_financial_analysis_zh",
                "code_generation": "qwen_code_generation_zh",
                "data_extraction": "qwen_data_extraction_zh",
                "reasoning": "qwen_reasoning_zh",
                "general": "qwen_general_zh"
            }
        }
        
        mapping_file = self.prompts_dir / "model_mappings.yaml"
        with open(mapping_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_mappings, f, allow_unicode=True, default_flow_style=False)
        
        self.model_mappings = default_mappings
        logger.info("✅ 创建默认模型映射配置")
    
    def get_prompt_template(self, model: str, task_type: str, language: str = "zh") -> Optional[PromptTemplate]:
        """
        获取指定模型和任务的提示词模板
        
        Args:
            model: 模型名称
            task_type: 任务类型
            language: 语言
            
        Returns:
            提示词模板或None
        """
        # 1. 尝试从模型映射中获取特定模板ID
        model_config = self.model_mappings.get(model, {})
        template_id = model_config.get(task_type)
        
        if template_id and template_id in self.templates:
            return self.templates[template_id]
        
        # 2. 尝试通过模型类型和任务类型匹配
        model_type = self._get_model_type(model)
        for template in self.templates.values():
            if (template.model_type == model_type and 
                template.task_type == task_type and 
                template.language == language):
                return template
        
        # 3. 尝试通用模板
        for template in self.templates.values():
            if (template.model_type == "general" and 
                template.task_type == task_type and 
                template.language == language):
                return template
        
        # 4. 最后尝试通用任务模板
        for template in self.templates.values():
            if (template.task_type == "general" and 
                template.language == language):
                return template
        
        logger.warning(f"⚠️ 未找到合适的提示词模板: model={model}, task={task_type}, lang={language}")
        return None
    
    def _get_model_type(self, model: str) -> str:
        """根据模型名称推断模型类型"""
        if "deepseek" in model.lower():
            return "deepseek"
        elif "gpt" in model.lower() or "openai" in model.lower():
            return "openai"
        elif "qwen" in model.lower() or "dashscope" in model.lower():
            return "qwen"
        elif "gemini" in model.lower() or "google" in model.lower():
            return "gemini"
        elif "claude" in model.lower():
            return "claude"
        else:
            return "general"
    
    def format_messages(self, model: str, task_type: str, variables: Dict[str, Any], 
                       language: str = "zh") -> List[Dict[str, str]]:
        """
        格式化消息列表
        
        Args:
            model: 模型名称
            task_type: 任务类型
            variables: 模板变量
            language: 语言
            
        Returns:
            格式化后的消息列表
        """
        template = self.get_prompt_template(model, task_type, language)
        
        if not template:
            # 使用默认提示词
            return [
                {"role": "system", "content": "你是一个有用的AI助手。"},
                {"role": "user", "content": variables.get("user_input", "")}
            ]
        
        # 验证变量
        missing_vars = template.validate_variables(variables)
        if missing_vars:
            logger.warning(f"⚠️ 提示词变量缺失: {missing_vars}")
        
        try:
            system_prompt, user_prompt = template.format_prompt(variables)
            
            messages = []
            if system_prompt.strip():
                messages.append({"role": "system", "content": system_prompt})
            if user_prompt.strip():
                messages.append({"role": "user", "content": user_prompt})
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ 格式化提示词失败: {e}")
            # 返回默认消息
            return [
                {"role": "system", "content": "你是一个有用的AI助手。"},
                {"role": "user", "content": variables.get("user_input", "")}
            ]
    
    def list_templates(self, model_type: str = None, task_type: str = None, 
                      language: str = None) -> List[PromptTemplate]:
        """列出提示词模板"""
        templates = list(self.templates.values())
        
        if model_type:
            templates = [t for t in templates if t.model_type == model_type]
        if task_type:
            templates = [t for t in templates if t.task_type == task_type]
        if language:
            templates = [t for t in templates if t.language == language]
        
        return templates
    
    def get_template_by_id(self, template_id: str) -> Optional[PromptTemplate]:
        """根据ID获取模板"""
        return self.templates.get(template_id)
    
    async def reload_templates(self):
        """重新加载模板"""
        await self.load_templates()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            "total_templates": len(self.templates),
            "last_reload": self._last_reload.isoformat() if self._last_reload else None,
            "by_model_type": {},
            "by_task_type": {},
            "by_language": {}
        }
        
        for template in self.templates.values():
            # 按模型类型统计
            model_type = template.model_type
            stats["by_model_type"][model_type] = stats["by_model_type"].get(model_type, 0) + 1
            
            # 按任务类型统计
            task_type = template.task_type
            stats["by_task_type"][task_type] = stats["by_task_type"].get(task_type, 0) + 1
            
            # 按语言统计
            language = template.language
            stats["by_language"][language] = stats["by_language"].get(language, 0) + 1
        
        return stats

# 全局提示词管理器实例
_prompt_manager_instance: Optional[PromptManager] = None

async def get_prompt_manager() -> PromptManager:
    """获取提示词管理器实例（单例模式）"""
    global _prompt_manager_instance
    if _prompt_manager_instance is None:
        _prompt_manager_instance = PromptManager()
        await _prompt_manager_instance.load_templates()
    return _prompt_manager_instance
