"""
基础智能体类
定义智能体的基本结构
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

@dataclass
class BaseAgent:
    """基础智能体类"""
    
    agent_type: str
    task_type: str
    description: str
    model_name: str = "deepseek-chat"
    temperature: float = 0.1
    max_tokens: int = 1500
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "agent_type": self.agent_type,
            "task_type": self.task_type,
            "description": self.description,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
