#!/usr/bin/env python3
"""
数据源优先级管理器 - 支持动态配置和个性化设置
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from .base import DataSourceType, MarketType, DataCategory

logger = logging.getLogger(__name__)

class PriorityManager:
    """数据源优先级管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_file()
        self.config_data = {}
        self.load_config()
    
    def _get_default_config_file(self) -> str:
        """获取默认配置文件路径"""
        current_dir = Path(__file__).parent
        return str(current_dir / "priority_config.json")
    
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                logger.info(f"✅ 加载优先级配置: {self.config_file}")
                return True
            else:
                logger.warning(f"⚠️ 配置文件不存在: {self.config_file}")
                self._create_default_config()
                return False
        except Exception as e:
            logger.error(f"❌ 加载配置文件失败: {e}")
            self._create_default_config()
            return False
    
    def _create_default_config(self):
        """创建默认配置"""
        self.config_data = {
            "version": "1.0",
            "current_profile": "default",
            "priority_profiles": {
                "default": {
                    "name": "默认配置",
                    "priorities": {
                        "a_share_basic_info": ["tushare", "akshare", "baostock"],
                        "a_share_price_data": ["tushare", "akshare", "baostock"],
                        "a_share_fundamentals": ["tushare", "akshare", "baostock"],
                        "a_share_news": ["akshare"],
                        "us_stock_basic_info": ["alpha_vantage", "twelve_data", "iex_cloud", "finnhub", "yfinance", "akshare"],
                        "us_stock_price_data": ["alpha_vantage", "twelve_data", "iex_cloud", "finnhub", "yfinance", "akshare"],
                        "us_stock_fundamentals": ["alpha_vantage", "twelve_data", "iex_cloud", "finnhub", "yfinance"],
                        "us_stock_news": ["twelve_data", "iex_cloud", "finnhub", "akshare"],
                        "hk_stock_basic_info": ["akshare", "yfinance"],
                        "hk_stock_price_data": ["akshare", "yfinance"],
                        "hk_stock_news": ["akshare"]
                    }
                }
            }
        }
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ 保存优先级配置: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"❌ 保存配置文件失败: {e}")
            return False
    
    def get_current_profile(self) -> str:
        """获取当前使用的配置文件"""
        return self.config_data.get("current_profile", "default")
    
    def set_current_profile(self, profile_name: str) -> bool:
        """设置当前使用的配置文件"""
        if profile_name in self.config_data.get("priority_profiles", {}):
            self.config_data["current_profile"] = profile_name
            return self.save_config()
        else:
            logger.error(f"❌ 配置文件不存在: {profile_name}")
            return False
    
    def get_available_profiles(self) -> Dict[str, Dict[str, Any]]:
        """获取所有可用的配置文件"""
        profiles = self.config_data.get("priority_profiles", {})
        result = {}
        for name, profile in profiles.items():
            result[name] = {
                "name": profile.get("name", name),
                "description": profile.get("description", ""),
                "is_current": name == self.get_current_profile()
            }
        return result
    
    def get_priority_config(self) -> Dict[str, List[DataSourceType]]:
        """获取当前的优先级配置"""
        current_profile = self.get_current_profile()
        profiles = self.config_data.get("priority_profiles", {})
        
        if current_profile not in profiles:
            logger.warning(f"⚠️ 当前配置文件不存在: {current_profile}，使用默认配置")
            current_profile = "default"
        
        priorities = profiles.get(current_profile, {}).get("priorities", {})
        
        # 转换为标准格式
        result = {}
        for key, source_names in priorities.items():
            try:
                # 转换数据源名称为枚举
                source_types = []
                for name in source_names:
                    source_type = DataSourceType(name.lower())
                    source_types.append(source_type)
                result[key] = source_types
            except ValueError as e:
                logger.warning(f"⚠️ 无效的数据源名称: {name} in {key}")
                continue
        
        # 应用自定义覆盖
        custom_overrides = self.config_data.get("custom_overrides", {})
        if custom_overrides.get("enabled", False):
            overrides = custom_overrides.get("overrides", {})
            for key, source_names in overrides.items():
                try:
                    source_types = [DataSourceType(name.lower()) for name in source_names]
                    result[key] = source_types
                    logger.info(f"✅ 应用自定义覆盖: {key}")
                except ValueError:
                    logger.warning(f"⚠️ 无效的自定义覆盖: {key}")
        
        return result
    
    def set_priority_for_category(self, market: MarketType, category: DataCategory, 
                                 sources: List[str]) -> bool:
        """设置特定类别的数据源优先级"""
        key = f"{market.value}_{category.value}"
        
        # 验证数据源名称
        try:
            for source in sources:
                DataSourceType(source.lower())
        except ValueError as e:
            logger.error(f"❌ 无效的数据源名称: {e}")
            return False
        
        # 获取当前配置文件
        current_profile = self.get_current_profile()
        profiles = self.config_data.get("priority_profiles", {})
        
        if current_profile not in profiles:
            logger.error(f"❌ 当前配置文件不存在: {current_profile}")
            return False
        
        # 更新优先级
        profiles[current_profile]["priorities"][key] = sources
        
        # 保存配置
        return self.save_config()
    
    def create_custom_profile(self, profile_name: str, description: str, 
                            base_profile: str = "default") -> bool:
        """创建自定义配置文件"""
        profiles = self.config_data.get("priority_profiles", {})
        
        if profile_name in profiles:
            logger.error(f"❌ 配置文件已存在: {profile_name}")
            return False
        
        # 基于现有配置创建新配置
        if base_profile in profiles:
            base_config = profiles[base_profile]["priorities"].copy()
        else:
            logger.warning(f"⚠️ 基础配置不存在: {base_profile}，使用默认配置")
            base_config = profiles.get("default", {}).get("priorities", {})
        
        # 创建新配置
        profiles[profile_name] = {
            "name": profile_name,
            "description": description,
            "priorities": base_config
        }
        
        return self.save_config()
    
    def delete_profile(self, profile_name: str) -> bool:
        """删除配置文件"""
        if profile_name == "default":
            logger.error("❌ 不能删除默认配置文件")
            return False
        
        profiles = self.config_data.get("priority_profiles", {})
        
        if profile_name not in profiles:
            logger.error(f"❌ 配置文件不存在: {profile_name}")
            return False
        
        # 如果删除的是当前配置，切换到默认配置
        if self.get_current_profile() == profile_name:
            self.config_data["current_profile"] = "default"
        
        # 删除配置
        del profiles[profile_name]
        
        return self.save_config()
    
    def get_data_source_info(self) -> Dict[str, Dict[str, Any]]:
        """获取数据源信息"""
        return self.config_data.get("data_source_info", {})
    
    def export_config(self, export_file: str) -> bool:
        """导出配置到文件"""
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ 导出配置到: {export_file}")
            return True
        except Exception as e:
            logger.error(f"❌ 导出配置失败: {e}")
            return False
    
    def import_config(self, import_file: str) -> bool:
        """从文件导入配置"""
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # 验证配置格式
            if not self._validate_config(imported_data):
                logger.error("❌ 导入的配置格式无效")
                return False
            
            self.config_data = imported_data
            return self.save_config()
        except Exception as e:
            logger.error(f"❌ 导入配置失败: {e}")
            return False
    
    def _validate_config(self, config_data: Dict[str, Any]) -> bool:
        """验证配置格式"""
        required_keys = ["priority_profiles", "current_profile"]
        for key in required_keys:
            if key not in config_data:
                return False
        
        # 验证配置文件格式
        profiles = config_data.get("priority_profiles", {})
        for profile_name, profile in profiles.items():
            if "priorities" not in profile:
                return False
        
        return True


# 全局优先级管理器实例
_priority_manager: Optional[PriorityManager] = None

def get_priority_manager() -> PriorityManager:
    """获取优先级管理器实例（单例模式）"""
    global _priority_manager
    if _priority_manager is None:
        _priority_manager = PriorityManager()
    return _priority_manager

def init_priority_manager(config_file: Optional[str] = None) -> PriorityManager:
    """初始化优先级管理器"""
    global _priority_manager
    _priority_manager = PriorityManager(config_file)
    logger.info("✅ 优先级管理器初始化完成")
    return _priority_manager
