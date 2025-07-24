#!/usr/bin/env python3
"""
CLI客户端配置管理
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field

class CLIConfig(BaseModel):
    """CLI配置模型"""
    
    # 服务配置
    backend_url: str = Field(default="http://localhost:8000", description="Backend服务URL")
    api_timeout: int = Field(default=300, description="API超时时间(秒)")
    
    # 分析配置
    default_analysis_type: str = Field(default="comprehensive", description="默认分析类型")
    max_debate_rounds: int = Field(default=3, description="最大辩论轮数")
    max_risk_rounds: int = Field(default=2, description="最大风险分析轮数")
    
    # 界面配置
    auto_refresh: bool = Field(default=True, description="自动刷新状态")
    refresh_interval: int = Field(default=2, description="刷新间隔(秒)")
    max_wait_time: int = Field(default=300, description="最大等待时间(秒)")
    show_progress: bool = Field(default=True, description="显示进度条")
    
    # 显示配置
    max_content_length: int = Field(default=500, description="最大内容显示长度")
    show_detailed_reports: bool = Field(default=False, description="默认显示详细报告")
    color_output: bool = Field(default=True, description="彩色输出")
    
    # 历史配置
    save_history: bool = Field(default=True, description="保存分析历史")
    max_history_items: int = Field(default=100, description="最大历史记录数")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file) if config_file else Path.home() / ".trading_cli_config.json"
        self.config = self.load_config()
    
    def load_config(self) -> CLIConfig:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return CLIConfig(**data)
            except Exception as e:
                print(f"⚠️ 配置文件加载失败，使用默认配置: {e}")
                return CLIConfig()
        else:
            # 创建默认配置文件
            config = CLIConfig()
            self.save_config(config)
            return config
    
    def save_config(self, config: Optional[CLIConfig] = None):
        """保存配置"""
        if config is None:
            config = self.config
        
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config.dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 配置文件保存失败: {e}")
    
    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self.save_config()
    
    def get_config(self) -> CLIConfig:
        """获取配置"""
        return self.config
    
    def reset_config(self):
        """重置为默认配置"""
        self.config = CLIConfig()
        self.save_config()

class HistoryManager:
    """历史记录管理器"""
    
    def __init__(self, history_file: Optional[str] = None):
        self.history_file = Path(history_file) if history_file else Path.home() / ".trading_cli_history.json"
        self.history = self.load_history()
    
    def load_history(self) -> List[Dict[str, Any]]:
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def save_history(self):
        """保存历史记录"""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 历史记录保存失败: {e}")
    
    def add_analysis(self, symbol: str, analysis_id: str, status: str = "started"):
        """添加分析记录"""
        record = {
            "symbol": symbol,
            "analysis_id": analysis_id,
            "status": status,
            "start_time": datetime.now().isoformat(),
            "end_time": None
        }
        
        self.history.insert(0, record)
        
        # 限制历史记录数量
        max_items = 100  # 可以从配置中获取
        if len(self.history) > max_items:
            self.history = self.history[:max_items]
        
        self.save_history()
    
    def update_analysis(self, analysis_id: str, status: str, result: Optional[Dict] = None):
        """更新分析记录"""
        for record in self.history:
            if record["analysis_id"] == analysis_id:
                record["status"] = status
                record["end_time"] = datetime.now().isoformat()
                if result:
                    record["result"] = result
                break
        
        self.save_history()
    
    def get_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的分析记录"""
        return self.history[:limit]
    
    def get_analysis_by_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """根据股票代码获取分析记录"""
        return [record for record in self.history if record["symbol"] == symbol]

class PresetManager:
    """预设配置管理器"""
    
    def __init__(self):
        self.presets = {
            "quick": {
                "analysis_type": "quick",
                "max_debate_rounds": 1,
                "max_risk_rounds": 1,
                "auto_refresh": True,
                "refresh_interval": 1
            },
            "standard": {
                "analysis_type": "comprehensive",
                "max_debate_rounds": 3,
                "max_risk_rounds": 2,
                "auto_refresh": True,
                "refresh_interval": 2
            },
            "detailed": {
                "analysis_type": "comprehensive",
                "max_debate_rounds": 5,
                "max_risk_rounds": 3,
                "auto_refresh": True,
                "refresh_interval": 3,
                "show_detailed_reports": True
            },
            "silent": {
                "analysis_type": "comprehensive",
                "max_debate_rounds": 3,
                "max_risk_rounds": 2,
                "auto_refresh": False,
                "show_progress": False,
                "color_output": False
            }
        }
    
    def get_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """获取预设配置"""
        return self.presets.get(name)
    
    def list_presets(self) -> List[str]:
        """列出所有预设"""
        return list(self.presets.keys())
    
    def apply_preset(self, config_manager: ConfigManager, preset_name: str) -> bool:
        """应用预设配置"""
        preset = self.get_preset(preset_name)
        if preset:
            config_manager.update_config(**preset)
            return True
        return False

# 环境变量配置
def load_env_config() -> Dict[str, Any]:
    """从环境变量加载配置"""
    env_config = {}
    
    # 服务配置
    if backend_url := os.getenv("TRADING_CLI_BACKEND_URL"):
        env_config["backend_url"] = backend_url
    
    if api_timeout := os.getenv("TRADING_CLI_API_TIMEOUT"):
        try:
            env_config["api_timeout"] = int(api_timeout)
        except ValueError:
            pass
    
    # 分析配置
    if analysis_type := os.getenv("TRADING_CLI_ANALYSIS_TYPE"):
        env_config["default_analysis_type"] = analysis_type
    
    if max_debate_rounds := os.getenv("TRADING_CLI_MAX_DEBATE_ROUNDS"):
        try:
            env_config["max_debate_rounds"] = int(max_debate_rounds)
        except ValueError:
            pass
    
    # 界面配置
    if auto_refresh := os.getenv("TRADING_CLI_AUTO_REFRESH"):
        env_config["auto_refresh"] = auto_refresh.lower() in ("true", "1", "yes")
    
    if refresh_interval := os.getenv("TRADING_CLI_REFRESH_INTERVAL"):
        try:
            env_config["refresh_interval"] = int(refresh_interval)
        except ValueError:
            pass
    
    # 日志配置
    if log_level := os.getenv("TRADING_CLI_LOG_LEVEL"):
        env_config["log_level"] = log_level.upper()
    
    if log_file := os.getenv("TRADING_CLI_LOG_FILE"):
        env_config["log_file"] = log_file
    
    return env_config

# 配置验证
def validate_config(config: CLIConfig) -> List[str]:
    """验证配置"""
    errors = []
    
    # 验证URL格式
    if not config.backend_url.startswith(("http://", "https://")):
        errors.append("backend_url必须以http://或https://开头")
    
    # 验证数值范围
    if config.api_timeout <= 0:
        errors.append("api_timeout必须大于0")
    
    if config.max_debate_rounds <= 0:
        errors.append("max_debate_rounds必须大于0")
    
    if config.max_risk_rounds <= 0:
        errors.append("max_risk_rounds必须大于0")
    
    if config.refresh_interval <= 0:
        errors.append("refresh_interval必须大于0")
    
    if config.max_wait_time <= 0:
        errors.append("max_wait_time必须大于0")
    
    # 验证日志级别
    valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if config.log_level.upper() not in valid_log_levels:
        errors.append(f"log_level必须是以下之一: {', '.join(valid_log_levels)}")
    
    return errors

# 配置迁移
def migrate_config(old_config: Dict[str, Any]) -> CLIConfig:
    """迁移旧版本配置"""
    # 处理配置字段名变更
    field_mapping = {
        "server_url": "backend_url",
        "timeout": "api_timeout",
        "analysis_mode": "default_analysis_type"
    }
    
    migrated = {}
    for old_key, value in old_config.items():
        new_key = field_mapping.get(old_key, old_key)
        migrated[new_key] = value
    
    try:
        return CLIConfig(**migrated)
    except Exception:
        # 如果迁移失败，返回默认配置
        return CLIConfig()

if __name__ == "__main__":
    # 测试配置管理
    config_manager = ConfigManager()
    print("当前配置:", config_manager.get_config().dict())
    
    # 测试预设
    preset_manager = PresetManager()
    print("可用预设:", preset_manager.list_presets())
    
    # 测试历史记录
    history_manager = HistoryManager()
    print("历史记录数量:", len(history_manager.history))
