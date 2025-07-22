#!/usr/bin/env python3
"""
数据源优先级配置管理工具
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.data_service.app.datasources.priority_manager import get_priority_manager
from backend.data_service.app.datasources.base import MarketType, DataCategory

class PriorityConfigCLI:
    """优先级配置命令行工具"""
    
    def __init__(self):
        self.priority_manager = get_priority_manager()
    
    def show_current_config(self):
        """显示当前配置"""
        print("📊 当前数据源优先级配置")
        print("=" * 50)
        
        current_profile = self.priority_manager.get_current_profile()
        print(f"🎯 当前配置文件: {current_profile}")
        
        config = self.priority_manager.get_priority_config()
        
        # 按市场分组显示
        markets = {
            "A股": ["a_share_basic_info", "a_share_price_data", "a_share_fundamentals", "a_share_news"],
            "美股": ["us_stock_basic_info", "us_stock_price_data", "us_stock_fundamentals", "us_stock_news"],
            "港股": ["hk_stock_basic_info", "hk_stock_price_data", "hk_stock_news"]
        }
        
        for market_name, categories in markets.items():
            print(f"\n📈 {market_name}:")
            for category in categories:
                if category in config:
                    sources = [s.value for s in config[category]]
                    category_display = category.replace("_", " ").title()
                    print(f"   {category_display}: {' → '.join(sources)}")
    
    def list_profiles(self):
        """列出所有配置文件"""
        print("📋 可用的优先级配置文件")
        print("=" * 50)
        
        profiles = self.priority_manager.get_available_profiles()
        
        for name, info in profiles.items():
            status = "✅ 当前" if info["is_current"] else "  "
            print(f"{status} {name}: {info['name']}")
            if info.get("description"):
                print(f"     {info['description']}")
    
    def switch_profile(self, profile_name: str):
        """切换配置文件"""
        print(f"🔄 切换到配置文件: {profile_name}")
        
        if self.priority_manager.set_current_profile(profile_name):
            print(f"✅ 成功切换到: {profile_name}")
            self.show_current_config()
        else:
            print(f"❌ 切换失败，配置文件不存在: {profile_name}")
    
    def create_profile(self, profile_name: str, description: str, base_profile: str = "default"):
        """创建新的配置文件"""
        print(f"📝 创建新配置文件: {profile_name}")
        
        if self.priority_manager.create_custom_profile(profile_name, description, base_profile):
            print(f"✅ 成功创建配置文件: {profile_name}")
        else:
            print(f"❌ 创建失败，配置文件可能已存在")
    
    def set_custom_priority(self):
        """交互式设置自定义优先级"""
        print("🎯 设置自定义数据源优先级")
        print("=" * 50)
        
        # 选择市场
        markets = {
            "1": ("A股", MarketType.A_SHARE),
            "2": ("美股", MarketType.US_STOCK),
            "3": ("港股", MarketType.HK_STOCK)
        }
        
        print("请选择市场:")
        for key, (name, _) in markets.items():
            print(f"  {key}. {name}")
        
        market_choice = input("请输入选择 (1-3): ").strip()
        if market_choice not in markets:
            print("❌ 无效选择")
            return
        
        market_name, market_type = markets[market_choice]
        
        # 选择数据类别
        categories = {
            "1": ("基本信息", DataCategory.BASIC_INFO),
            "2": ("价格数据", DataCategory.PRICE_DATA),
            "3": ("基本面数据", DataCategory.FUNDAMENTALS),
            "4": ("新闻数据", DataCategory.NEWS)
        }
        
        print(f"\n请选择 {market_name} 的数据类别:")
        for key, (name, _) in categories.items():
            print(f"  {key}. {name}")
        
        category_choice = input("请输入选择 (1-4): ").strip()
        if category_choice not in categories:
            print("❌ 无效选择")
            return
        
        category_name, category_type = categories[category_choice]
        
        # 显示可用数据源
        available_sources = {
            "tushare": "Tushare (专业A股)",
            "akshare": "AKShare (免费多市场)",
            "finnhub": "FinnHub (专业美股)",
            "baostock": "BaoStock (免费A股)",
            "yfinance": "Yahoo Finance (免费全球)"
        }
        
        print(f"\n可用的数据源:")
        for source, desc in available_sources.items():
            print(f"  - {source}: {desc}")
        
        print(f"\n请输入 {market_name} {category_name} 的数据源优先级")
        print("格式: source1,source2,source3 (用逗号分隔，按优先级排序)")
        print("示例: akshare,tushare,baostock")
        
        sources_input = input("请输入: ").strip()
        if not sources_input:
            print("❌ 输入为空")
            return
        
        sources = [s.strip().lower() for s in sources_input.split(",")]
        
        # 验证数据源
        invalid_sources = [s for s in sources if s not in available_sources]
        if invalid_sources:
            print(f"❌ 无效的数据源: {', '.join(invalid_sources)}")
            return
        
        # 设置优先级
        if self.priority_manager.set_priority_for_category(market_type, category_type, sources):
            print(f"✅ 成功设置 {market_name} {category_name} 优先级: {' → '.join(sources)}")
        else:
            print("❌ 设置失败")
    
    def export_config(self, export_file: str):
        """导出配置"""
        print(f"📤 导出配置到: {export_file}")
        
        if self.priority_manager.export_config(export_file):
            print(f"✅ 导出成功: {export_file}")
        else:
            print("❌ 导出失败")
    
    def import_config(self, import_file: str):
        """导入配置"""
        print(f"📥 从文件导入配置: {import_file}")
        
        if self.priority_manager.import_config(import_file):
            print(f"✅ 导入成功: {import_file}")
            self.show_current_config()
        else:
            print("❌ 导入失败")
    
    def show_data_source_info(self):
        """显示数据源信息"""
        print("📊 数据源详细信息")
        print("=" * 50)
        
        info = self.priority_manager.get_data_source_info()
        
        for source, details in info.items():
            print(f"\n📈 {details.get('name', source)}:")
            print(f"   描述: {details.get('description', 'N/A')}")
            print(f"   需要API密钥: {'是' if details.get('requires_api_key') else '否'}")
            print(f"   支持市场: {', '.join(details.get('markets', []))}")
            print(f"   优势: {', '.join(details.get('strengths', []))}")
            print(f"   限制: {', '.join(details.get('limitations', []))}")

def main():
    """主函数"""
    cli = PriorityConfigCLI()
    
    if len(sys.argv) < 2:
        print("🔧 TradingAgents 数据源优先级配置管理工具")
        print("=" * 50)
        print("使用方法:")
        print("  python manage_data_source_priority.py <命令> [参数]")
        print("")
        print("可用命令:")
        print("  show              - 显示当前配置")
        print("  list              - 列出所有配置文件")
        print("  switch <profile>  - 切换配置文件")
        print("  create <name> <desc> [base] - 创建新配置文件")
        print("  custom            - 交互式设置自定义优先级")
        print("  export <file>     - 导出配置到文件")
        print("  import <file>     - 从文件导入配置")
        print("  info              - 显示数据源信息")
        print("")
        print("示例:")
        print("  python manage_data_source_priority.py show")
        print("  python manage_data_source_priority.py switch akshare_first")
        print("  python manage_data_source_priority.py create my_config '我的配置' default")
        return
    
    command = sys.argv[1].lower()
    
    if command == "show":
        cli.show_current_config()
    elif command == "list":
        cli.list_profiles()
    elif command == "switch":
        if len(sys.argv) < 3:
            print("❌ 请指定配置文件名")
            return
        cli.switch_profile(sys.argv[2])
    elif command == "create":
        if len(sys.argv) < 4:
            print("❌ 请指定配置文件名和描述")
            return
        name = sys.argv[2]
        description = sys.argv[3]
        base = sys.argv[4] if len(sys.argv) > 4 else "default"
        cli.create_profile(name, description, base)
    elif command == "custom":
        cli.set_custom_priority()
    elif command == "export":
        if len(sys.argv) < 3:
            print("❌ 请指定导出文件名")
            return
        cli.export_config(sys.argv[2])
    elif command == "import":
        if len(sys.argv) < 3:
            print("❌ 请指定导入文件名")
            return
        cli.import_config(sys.argv[2])
    elif command == "info":
        cli.show_data_source_info()
    else:
        print(f"❌ 未知命令: {command}")

if __name__ == "__main__":
    main()
