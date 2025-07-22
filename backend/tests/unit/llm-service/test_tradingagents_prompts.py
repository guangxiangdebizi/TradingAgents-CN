#!/usr/bin/env python3
"""
TradingAgents专用提示词测试
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class TradingAgentsPromptTester:
    """TradingAgents提示词测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
    
    async def test_fundamentals_analyst(self):
        """测试基本面分析师提示词"""
        print("📊 测试基本面分析师")
        print("-" * 40)
        
        payload = {
            "model": "deepseek-chat",
            "task_type": "fundamentals_analysis",
            "messages": [
                {
                    "role": "user", 
                    "content": "请分析五粮液(000858)的投资价值"
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1,
            "user_id": "test_user"
        }
        
        return await self._test_prompt(payload, "基本面分析师")
    
    async def test_market_analyst(self):
        """测试技术分析师提示词"""
        print("\n📈 测试技术分析师")
        print("-" * 40)
        
        payload = {
            "model": "deepseek-chat",
            "task_type": "technical_analysis",
            "messages": [
                {
                    "role": "user", 
                    "content": "请对苹果公司(AAPL)进行技术分析"
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1,
            "user_id": "test_user"
        }
        
        return await self._test_prompt(payload, "技术分析师")
    
    async def test_bull_researcher(self):
        """测试看涨研究员提示词"""
        print("\n🚀 测试看涨研究员")
        print("-" * 40)
        
        payload = {
            "model": "deepseek-chat",
            "task_type": "bull_analysis",
            "messages": [
                {
                    "role": "user", 
                    "content": "请为特斯拉(TSLA)构建看涨投资案例"
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1,
            "user_id": "test_user"
        }
        
        return await self._test_prompt(payload, "看涨研究员")
    
    async def test_bear_researcher(self):
        """测试看跌研究员提示词"""
        print("\n📉 测试看跌研究员")
        print("-" * 40)
        
        payload = {
            "model": "deepseek-chat",
            "task_type": "bear_analysis",
            "messages": [
                {
                    "role": "user", 
                    "content": "请为比亚迪(002594)分析投资风险"
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1,
            "user_id": "test_user"
        }
        
        return await self._test_prompt(payload, "看跌研究员")
    
    async def test_risk_manager(self):
        """测试风险管理师提示词"""
        print("\n🛡️ 测试风险管理师")
        print("-" * 40)
        
        payload = {
            "model": "deepseek-chat",
            "task_type": "risk_management",
            "messages": [
                {
                    "role": "user", 
                    "content": "请对茅台(600519)进行风险管理分析"
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1,
            "user_id": "test_user"
        }
        
        return await self._test_prompt(payload, "风险管理师")
    
    async def test_research_manager(self):
        """测试研究主管提示词"""
        print("\n👔 测试研究主管")
        print("-" * 40)
        
        payload = {
            "model": "deepseek-chat",
            "task_type": "research_management",
            "messages": [
                {
                    "role": "user", 
                    "content": "请综合分析宁德时代(300750)的投资价值并做出最终决策"
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.1,
            "user_id": "test_user"
        }
        
        return await self._test_prompt(payload, "研究主管")
    
    async def _test_prompt(self, payload: dict, role_name: str):
        """执行提示词测试"""
        try:
            start_time = datetime.now()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/chat/completions",
                    json=payload,
                    timeout=120
                ) as response:
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    
                    print(f"⏱️ 响应时间: {duration:.2f}秒")
                    print(f"📡 HTTP状态: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('choices'):
                            content = data['choices'][0]['message']['content']
                            model_used = data.get('model', 'unknown')
                            
                            print(f"✅ {role_name}测试成功")
                            print(f"🤖 使用模型: {model_used}")
                            print(f"📝 回复长度: {len(content)} 字符")
                            
                            # 检查关键词
                            keywords = self._get_role_keywords(payload['task_type'])
                            found_keywords = [kw for kw in keywords if kw in content]
                            
                            print(f"🔍 关键词匹配: {len(found_keywords)}/{len(keywords)}")
                            if found_keywords:
                                print(f"  ✅ 匹配: {', '.join(found_keywords[:3])}...")
                            
                            # 显示部分内容
                            print(f"📄 内容预览: {content[:200]}...")
                            
                            return True
                        else:
                            print(f"❌ {role_name}测试失败: 无回复内容")
                            return False
                    else:
                        error_text = await response.text()
                        print(f"❌ {role_name}测试失败: HTTP {response.status}")
                        print(f"📄 错误: {error_text[:200]}...")
                        return False
                        
        except Exception as e:
            print(f"❌ {role_name}测试异常: {e}")
            return False
    
    def _get_role_keywords(self, task_type: str) -> list:
        """获取角色相关的关键词"""
        keywords_map = {
            "fundamentals_analysis": ["基本面", "财务", "估值", "ROE", "PE", "投资建议"],
            "technical_analysis": ["技术", "趋势", "MACD", "RSI", "支撑", "阻力"],
            "bull_analysis": ["看涨", "增长", "机会", "优势", "买入", "目标价"],
            "bear_analysis": ["看跌", "风险", "挑战", "卖出", "减持", "担忧"],
            "risk_management": ["风险", "控制", "仓位", "止损", "波动", "VaR"],
            "research_management": ["综合", "决策", "建议", "权重", "情景", "策略"]
        }
        return keywords_map.get(task_type, [])
    
    async def test_prompt_template_selection(self):
        """测试提示词模板选择"""
        print("\n🎯 测试提示词模板选择")
        print("-" * 40)
        
        try:
            # 获取模板列表
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/prompts/templates", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        templates = data.get('data', [])
                        
                        # 统计TradingAgents模板
                        ta_templates = [t for t in templates if 'tradingagents' in t.get('id', '')]
                        
                        print(f"✅ 获取模板成功")
                        print(f"📊 总模板数: {len(templates)}")
                        print(f"🎯 TradingAgents模板: {len(ta_templates)}")
                        
                        # 显示TradingAgents模板
                        for template in ta_templates:
                            task_type = template.get('task_type', 'unknown')
                            name = template.get('name', 'unknown')
                            print(f"  📄 {task_type}: {name}")
                        
                        return len(ta_templates) >= 5  # 至少应该有5个TradingAgents模板
                    else:
                        print(f"❌ 获取模板失败: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            return False
    
    async def test_different_models(self):
        """测试不同模型的提示词效果"""
        print("\n🤖 测试不同模型")
        print("-" * 40)
        
        models = ["deepseek-chat", "gpt-4", "qwen-plus"]
        task_type = "fundamentals_analysis"
        
        results = {}
        
        for model in models:
            try:
                print(f"\n🔍 测试模型: {model}")
                
                payload = {
                    "model": model,
                    "task_type": task_type,
                    "messages": [
                        {
                            "role": "user", 
                            "content": "请分析腾讯控股(00700)的投资价值"
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.1,
                    "user_id": "test_user"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/api/v1/chat/completions",
                        json=payload,
                        timeout=60
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            actual_model = data.get('model', 'unknown')
                            results[model] = actual_model
                            print(f"  ✅ 请求模型: {model} -> 实际模型: {actual_model}")
                        else:
                            results[model] = f"HTTP {response.status}"
                            print(f"  ❌ 失败: HTTP {response.status}")
                
                # 避免频率限制
                await asyncio.sleep(2)
                
            except Exception as e:
                results[model] = f"异常: {str(e)}"
                print(f"  ❌ 异常: {e}")
        
        print(f"\n📊 模型测试汇总:")
        for model, result in results.items():
            print(f"  {model}: {result}")
        
        return len([r for r in results.values() if "异常" not in str(r) and "HTTP" not in str(r)]) > 0
    
    async def run_all_tests(self):
        """运行所有TradingAgents提示词测试"""
        print("🧪 TradingAgents提示词完整测试")
        print("=" * 60)
        
        tests = [
            ("提示词模板选择", self.test_prompt_template_selection()),
            ("基本面分析师", self.test_fundamentals_analyst()),
            ("技术分析师", self.test_market_analyst()),
            ("看涨研究员", self.test_bull_researcher()),
            ("看跌研究员", self.test_bear_researcher()),
            ("风险管理师", self.test_risk_manager()),
            ("研究主管", self.test_research_manager()),
            ("不同模型测试", self.test_different_models())
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
            print("🎉 所有测试通过！TradingAgents提示词系统工作正常")
        else:
            print("⚠️ 部分测试失败，请检查提示词配置")

async def main():
    """主函数"""
    tester = TradingAgentsPromptTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
