#!/usr/bin/env python3
"""
快速测试CLI是否正常工作
"""

import sys
import asyncio
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.core import BackendClient, ui
    from app.ui import display_welcome
    print("✅ 导入app模块成功")
except ImportError as e:
    print(f"❌ 导入app模块失败: {e}")
    try:
        # 尝试导入旧版本
        from trading_cli import BackendClient, display_welcome, ui
        print("✅ 导入旧版模块成功")
    except ImportError as e2:
        print(f"❌ 导入模块失败: {e2}")
        print("请先安装依赖: pip install -r requirements.txt")
        sys.exit(1)

async def test_backend_connection():
    """测试API Gateway连接"""
    print("\n🔍 测试API Gateway连接...")

    try:
        async with BackendClient("http://localhost:8000") as client:
            health = await client.health_check()
            
            if health.get("success"):
                print("✅ API Gateway连接正常")
                return True
            else:
                print(f"❌ API Gateway连接失败: {health.get('error', 'Unknown error')}")
                return False
                
    except Exception as e:
        print(f"❌ 连接测试异常: {e}")
        return False

def test_ui_components():
    """测试UI组件"""
    print("\n🎨 测试UI组件...")
    
    try:
        # 测试欢迎界面
        print("测试欢迎界面...")
        display_welcome()
        
        # 测试UI管理器
        print("\n测试UI管理器...")
        ui.show_success("UI组件测试成功")
        ui.show_warning("这是一个警告消息")
        ui.show_error("这是一个错误消息")
        ui.show_progress("这是一个进度消息")
        
        print("✅ UI组件测试通过")
        return True
        
    except Exception as e:
        print(f"❌ UI组件测试失败: {e}")
        return False

def test_imports():
    """测试所有必要的导入"""
    print("\n📦 测试导入...")
    
    required_modules = [
        'rich.console',
        'rich.table', 
        'rich.panel',
        'rich.progress',
        'rich.prompt',
        'aiohttp',
        'typer',
        'loguru'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ 缺少依赖: {', '.join(failed_imports)}")
        print("请运行: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ 所有依赖导入成功")
        return True

async def main():
    """主测试函数"""
    print("🚀 TradingAgents CLI 快速测试")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        return False
    
    # 测试UI组件
    if not test_ui_components():
        return False
    
    # 测试API Gateway连接
    backend_ok = await test_backend_connection()

    print("\n" + "=" * 50)
    print("📋 测试结果摘要:")
    print(f"  导入测试: ✅")
    print(f"  UI组件测试: ✅")
    print(f"  API Gateway连接: {'✅' if backend_ok else '❌'}")

    if not backend_ok:
        print("\n⚠️ API Gateway服务未运行，但CLI可以正常启动")
        print("   请确保API Gateway服务在运行后再进行分析")
    
    print("\n🎉 CLI基本功能测试完成!")
    print("   可以运行: python trading_cli.py")
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
