#!/usr/bin/env python3
"""
LLM Service 测试
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class LLMServiceTester:
    """LLM Service 测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
    
    async def test_health_check(self):
        """测试健康检查"""
        print("🏥 测试健康检查")
        print("-" * 40)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ 服务状态: {data.get('status')}")
                        
                        dependencies = data.get('dependencies', {})
                        for dep, status in dependencies.items():
                            emoji = "✅" if "connected" in status or "healthy" in status else "❌"
                            print(f"  {emoji} {dep}: {status}")
                        
                        return True
                    else:
                        print(f"❌ HTTP错误: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False
    
    async def test_list_models(self):
        """测试模型列表"""
        print("\n🤖 测试模型列表")
        print("-" * 40)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/models", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get('data', [])
                        
                        print(f"📊 可用模型数量: {len(models)}")
                        
                        for model in models:
                            status_emoji = "✅" if model.get('status') == 'healthy' else "❌"
                            print(f"  {status_emoji} {model.get('id')} ({model.get('provider')})")
                            print(f"    最大Token: {model.get('max_tokens')}")
                            print(f"    支持流式: {model.get('supports_streaming')}")
                            print(f"    擅长: {', '.join(model.get('strengths', []))}")
                        
                        return len(models) > 0
                    else:
                        print(f"❌ HTTP错误: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    
    async def test_chat_completion(self, model: str = "auto", task_type: str = "financial_analysis"):
        """测试聊天完成"""
        print(f"\n💬 测试聊天完成 (模型: {model}, 任务: {task_type})")
        print("-" * 40)
        
        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "你是一个专业的股票分析师"},
                    {"role": "user", "content": "请简单分析一下苹果公司(AAPL)的投资价值"}
                ],
                "task_type": task_type,
                "max_tokens": 500,
                "temperature": 0.1,
                "user_id": "test_user"
            }
            
            start_time = datetime.now()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/chat/completions",
                    json=payload,
                    timeout=60
                ) as response:
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    
                    print(f"⏱️ 响应时间: {duration:.2f}秒")
                    print(f"📡 HTTP状态: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        print(f"✅ 请求成功")
                        print(f"🤖 使用模型: {data.get('model')}")
                        
                        choices = data.get('choices', [])
                        if choices:
                            content = choices[0].get('message', {}).get('content', '')
                            print(f"💭 回复内容: {content[:100]}...")
                        
                        usage = data.get('usage', {})
                        print(f"📊 Token使用:")
                        print(f"  输入: {usage.get('prompt_tokens', 0)}")
                        print(f"  输出: {usage.get('completion_tokens', 0)}")
                        print(f"  总计: {usage.get('total_tokens', 0)}")
                        
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ HTTP错误: {response.status}")
                        print(f"📄 错误内容: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    
    async def test_usage_stats(self):
        """测试使用统计"""
        print(f"\n📊 测试使用统计")
        print("-" * 40)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/v1/usage/stats",
                    params={"days": 1},
                    timeout=10
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success'):
                            stats = data.get('data', {})
                            total = stats.get('total', {})
                            
                            print(f"✅ 统计获取成功")
                            print(f"📈 总请求数: {total.get('requests', 0)}")
                            print(f"🔢 总Token数: {total.get('tokens', 0)}")
                            print(f"💰 总成本: ${total.get('cost', 0):.6f}")
                            
                            models = stats.get('models', {})
                            if models:
                                print(f"🤖 模型使用:")
                                for model, model_stats in models.items():
                                    print(f"  {model}: {model_stats.get('requests', 0)} 次请求")
                            
                            return True
                        else:
                            print(f"❌ 统计获取失败")
                            return False
                    else:
                        print(f"❌ HTTP错误: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    
    async def test_different_task_types(self):
        """测试不同任务类型的路由"""
        print(f"\n🎯 测试任务类型路由")
        print("-" * 40)
        
        task_types = [
            "financial_analysis",
            "code_generation", 
            "data_extraction",
            "reasoning",
            "general"
        ]
        
        results = {}
        
        for task_type in task_types:
            try:
                print(f"\n🔍 测试任务类型: {task_type}")
                
                payload = {
                    "model": "auto",
                    "messages": [
                        {"role": "user", "content": f"这是一个{task_type}任务的测试"}
                    ],
                    "task_type": task_type,
                    "max_tokens": 50,
                    "user_id": "test_user"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/api/v1/chat/completions",
                        json=payload,
                        timeout=30
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            selected_model = data.get('model', 'unknown')
                            results[task_type] = selected_model
                            print(f"  ✅ 选择模型: {selected_model}")
                        else:
                            results[task_type] = "failed"
                            print(f"  ❌ 失败: HTTP {response.status}")
                
                # 避免频率限制
                await asyncio.sleep(1)
                
            except Exception as e:
                results[task_type] = f"error: {str(e)}"
                print(f"  ❌ 异常: {e}")
        
        print(f"\n📊 路由结果汇总:")
        for task_type, result in results.items():
            print(f"  {task_type}: {result}")
        
        return len([r for r in results.values() if r not in ["failed", "error"]]) > 0
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 LLM Service 完整测试")
        print("=" * 60)
        
        tests = [
            ("健康检查", self.test_health_check()),
            ("模型列表", self.test_list_models()),
            ("聊天完成", self.test_chat_completion()),
            ("使用统计", self.test_usage_stats()),
            ("任务路由", self.test_different_task_types())
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
            print("🎉 所有测试通过！LLM Service 工作正常")
        else:
            print("⚠️ 部分测试失败，请检查服务配置")

async def main():
    """主函数"""
    tester = LLMServiceTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
