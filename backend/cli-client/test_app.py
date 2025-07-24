#!/usr/bin/env python3
"""
测试新的app模块结构
"""

import sys
from pathlib import Path

def test_imports():
    """测试导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试基础模块
        from rich.console import Console
        print("✅ rich.console")
        
        from rich.table import Table
        print("✅ rich.table")
        
        from rich.panel import Panel
        print("✅ rich.panel")
        
        # 测试app模块
        from app.core import AnalystType, DEFAULT_CONFIG, CLIUserInterface
        print("✅ app.core")
        
        from app.ui import display_welcome, create_question_box
        print("✅ app.ui")
        
        from app.interactions import select_market
        print("✅ app.interactions")
        
        print("\n✅ 所有模块导入成功!")
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_ui():
    """测试UI组件"""
    print("\n🎨 测试UI组件...")
    
    try:
        from app.ui import display_welcome
        from app.core import ui
        
        # 测试欢迎界面
        print("显示欢迎界面:")
        display_welcome()
        
        # 测试UI管理器
        print("\n测试UI管理器:")
        ui.show_success("UI测试成功!")
        ui.show_warning("这是警告消息")
        ui.show_error("这是错误消息")
        
        print("\n✅ UI组件测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ UI测试失败: {e}")
        return False

def test_config():
    """测试配置"""
    print("\n⚙️ 测试配置...")
    
    try:
        from app.core import DEFAULT_CONFIG, AnalystType
        
        print(f"默认配置: {DEFAULT_CONFIG}")
        print(f"分析师类型: {[a.value for a in AnalystType]}")
        
        print("\n✅ 配置测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 TradingAgents CLI App模块测试")
    print("=" * 50)
    
    # 检查当前目录
    current_dir = Path.cwd()
    app_dir = current_dir / "app"
    
    if not app_dir.exists():
        print(f"❌ app目录不存在: {app_dir}")
        print("请确保在正确的目录中运行此脚本")
        return False
    
    print(f"✅ 当前目录: {current_dir}")
    print(f"✅ app目录存在: {app_dir}")
    
    # 运行测试
    tests = [
        ("导入测试", test_imports),
        ("UI测试", test_ui),
        ("配置测试", test_config)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}异常: {e}")
            results.append((test_name, False))
    
    # 显示结果
    print("\n" + "=" * 50)
    print("📋 测试结果摘要:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过! 可以运行: python -m app")
    else:
        print("\n⚠️ 部分测试失败，请检查依赖安装")
        print("   运行: pip install -r requirements.txt")
    
    return all_passed

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
