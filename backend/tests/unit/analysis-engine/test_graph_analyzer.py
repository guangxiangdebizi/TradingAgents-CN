#!/usr/bin/env python3
"""
图分析器测试
测试工具链和分析图的功能
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.analysis_engine.app.analysis.graph_analyzer import GraphAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GraphAnalyzerTester:
    """图分析器测试器"""
    
    def __init__(self):
        self.analyzer = GraphAnalyzer()
    
    async def test_initialization(self):
        """测试初始化"""
        print("🔧 测试图分析器初始化")
        print("-" * 40)
        
        try:
            await self.analyzer.initialize()
            print("✅ 图分析器初始化成功")
            return True
        except Exception as e:
            print(f"❌ 图分析器初始化失败: {e}")
            return False
    
    async def test_tools(self):
        """测试工具链"""
        print("\n🛠️ 测试工具链")
        print("-" * 40)
        
        try:
            # 获取可用工具
            tools = await self.analyzer.get_available_tools()
            print(f"✅ 获取到{len(tools)}个工具:")
            
            for tool in tools:
                print(f"  📄 {tool['name']}: {tool['description']}")
            
            # 测试工具调用
            print(f"\n🔧 测试工具调用...")
            
            # 测试获取股票数据
            result = await self.analyzer.call_tool(
                "get_stock_data",
                {"symbol": "AAPL", "period": "1y"}
            )
            
            if result.get("success"):
                print("✅ 股票数据获取成功")
                print(f"  📊 数据: {result.get('result', {}).get('data', {})}")
            else:
                print(f"❌ 股票数据获取失败: {result.get('error')}")
            
            # 测试技术指标计算
            result = await self.analyzer.call_tool(
                "calculate_technical_indicators",
                {
                    "data": {"prices": [150, 151, 149, 152, 148, 153, 150, 155, 152, 157]},
                    "indicators": ["RSI", "MACD", "MA"]
                }
            )
            
            if result.get("success"):
                print("✅ 技术指标计算成功")
                indicators = result.get('result', {}).get('indicators', {})
                print(f"  📈 RSI: {indicators.get('rsi', {})}")
                print(f"  📊 MACD: {indicators.get('macd', {})}")
            else:
                print(f"❌ 技术指标计算失败: {result.get('error')}")
            
            return True
            
        except Exception as e:
            print(f"❌ 工具链测试失败: {e}")
            return False
    
    async def test_agents(self):
        """测试智能体"""
        print("\n🤖 测试智能体")
        print("-" * 40)
        
        try:
            # 获取可用智能体
            agents = await self.analyzer.get_available_agents()
            print(f"✅ 获取到{len(agents)}个智能体:")
            
            for agent in agents:
                print(f"  🤖 {agent['agent_type']}: {agent['description']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 智能体测试失败: {e}")
            return False
    
    async def test_fundamentals_analysis(self):
        """测试基本面分析"""
        print("\n📊 测试基本面分析")
        print("-" * 40)
        
        try:
            result = await self.analyzer.analyze_stock(
                symbol="AAPL",
                analysis_type="fundamentals",
                parameters={
                    "enable_fundamentals": True,
                    "enable_technical": False,
                    "enable_news": False,
                    "enable_debate": False
                }
            )
            
            if result.get("success"):
                print("✅ 基本面分析成功")
                reports = result.get("reports", {})
                fundamentals = reports.get("fundamentals")
                if fundamentals:
                    print(f"📄 基本面报告: {fundamentals[:200]}...")
                else:
                    print("⚠️ 未生成基本面报告")
            else:
                print(f"❌ 基本面分析失败: {result.get('error')}")
            
            return result.get("success", False)
            
        except Exception as e:
            print(f"❌ 基本面分析测试失败: {e}")
            return False
    
    async def test_technical_analysis(self):
        """测试技术分析"""
        print("\n📈 测试技术分析")
        print("-" * 40)
        
        try:
            result = await self.analyzer.analyze_stock(
                symbol="TSLA",
                analysis_type="technical",
                parameters={
                    "enable_fundamentals": False,
                    "enable_technical": True,
                    "enable_news": False,
                    "enable_debate": False
                }
            )
            
            if result.get("success"):
                print("✅ 技术分析成功")
                reports = result.get("reports", {})
                technical = reports.get("technical")
                if technical:
                    print(f"📄 技术分析报告: {technical[:200]}...")
                else:
                    print("⚠️ 未生成技术分析报告")
            else:
                print(f"❌ 技术分析失败: {result.get('error')}")
            
            return result.get("success", False)
            
        except Exception as e:
            print(f"❌ 技术分析测试失败: {e}")
            return False
    
    async def test_comprehensive_analysis(self):
        """测试综合分析"""
        print("\n🔍 测试综合分析")
        print("-" * 40)
        
        try:
            result = await self.analyzer.analyze_stock(
                symbol="NVDA",
                analysis_type="comprehensive",
                parameters={
                    "enable_fundamentals": True,
                    "enable_technical": True,
                    "enable_news": True,
                    "enable_debate": True,
                    "enable_risk_assessment": True
                }
            )
            
            if result.get("success"):
                print("✅ 综合分析成功")
                reports = result.get("reports", {})
                
                # 显示各种报告
                for report_type, content in reports.items():
                    if content:
                        print(f"📄 {report_type}: {content[:100]}...")
                
                # 显示元数据
                metadata = result.get("metadata", {})
                completed_steps = metadata.get("completed_steps", [])
                print(f"✅ 完成步骤: {completed_steps}")
                
                errors = metadata.get("errors", [])
                if errors:
                    print(f"⚠️ 错误: {errors}")
                
            else:
                print(f"❌ 综合分析失败: {result.get('error')}")
            
            return result.get("success", False)
            
        except Exception as e:
            print(f"❌ 综合分析测试失败: {e}")
            return False
    
    async def test_cleanup(self):
        """测试清理"""
        print("\n🧹 测试资源清理")
        print("-" * 40)
        
        try:
            await self.analyzer.cleanup()
            print("✅ 资源清理成功")
            return True
        except Exception as e:
            print(f"❌ 资源清理失败: {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 图分析器完整测试")
        print("=" * 60)
        
        tests = [
            ("初始化测试", self.test_initialization()),
            ("工具链测试", self.test_tools()),
            ("智能体测试", self.test_agents()),
            ("基本面分析测试", self.test_fundamentals_analysis()),
            ("技术分析测试", self.test_technical_analysis()),
            ("综合分析测试", self.test_comprehensive_analysis()),
            ("资源清理测试", self.test_cleanup())
        ]
        
        results = {}
        
        for test_name, test_coro in tests:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                result = await test_coro
                results[test_name] = result
                
                if result:
                    print(f"✅ {test_name} 通过")
                else:
                    print(f"❌ {test_name} 失败")
                    
            except Exception as e:
                print(f"❌ {test_name} 异常: {e}")
                results[test_name] = False
        
        # 显示测试汇总
        print(f"\n🎯 测试汇总")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            emoji = "✅" if result else "❌"
            print(f"{emoji} {test_name}")
        
        print(f"\n📊 通过率: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 所有测试通过！图分析器工作正常")
        else:
            print("⚠️ 部分测试失败，请检查配置")

async def main():
    """主函数"""
    tester = GraphAnalyzerTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
