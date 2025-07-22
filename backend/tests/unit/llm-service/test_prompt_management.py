#!/usr/bin/env python3
"""
提示词管理测试
"""

import asyncio
import aiohttp
import json

class PromptManagementTester:
    """提示词管理测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
    
    async def test_prompt_templates_list(self):
        """测试提示词模板列表"""
        print("📋 测试提示词模板列表")
        print("-" * 40)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/prompts/templates", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success'):
                            templates = data.get('data', [])
                            total = data.get('total', 0)
                            
                            print(f"✅ 获取成功，共{total}个模板")
                            
                            # 按模型类型分组显示
                            by_model = {}
                            for template in templates:
                                model_type = template.get('model_type', 'unknown')
                                if model_type not in by_model:
                                    by_model[model_type] = []
                                by_model[model_type].append(template)
                            
                            for model_type, model_templates in by_model.items():
                                print(f"\n🤖 {model_type} 模型:")
                                for template in model_templates:
                                    task_type = template.get('task_type', 'unknown')
                                    language = template.get('language', 'unknown')
                                    print(f"  📄 {template.get('name')} ({task_type}, {language})")
                            
                            return True
                        else:
                            print(f"❌ API失败: {data.get('message', 'N/A')}")
                            return False
                    else:
                        print(f"❌ HTTP错误: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    
    async def test_prompt_stats(self):
        """测试提示词统计"""
        print("\n📊 测试提示词统计")
        print("-" * 40)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/prompts/stats", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success'):
                            stats = data.get('data', {})
                            
                            print(f"✅ 统计获取成功")
                            print(f"📊 总模板数: {stats.get('total_templates', 0)}")
                            print(f"🕐 最后加载: {stats.get('last_reload', 'N/A')}")
                            
                            # 按模型类型统计
                            by_model = stats.get('by_model_type', {})
                            if by_model:
                                print(f"\n🤖 按模型类型:")
                                for model_type, count in by_model.items():
                                    print(f"  {model_type}: {count} 个")
                            
                            # 按任务类型统计
                            by_task = stats.get('by_task_type', {})
                            if by_task:
                                print(f"\n🎯 按任务类型:")
                                for task_type, count in by_task.items():
                                    print(f"  {task_type}: {count} 个")
                            
                            # 按语言统计
                            by_language = stats.get('by_language', {})
                            if by_language:
                                print(f"\n🌍 按语言:")
                                for language, count in by_language.items():
                                    print(f"  {language}: {count} 个")
                            
                            return True
                        else:
                            print(f"❌ API失败: {data.get('message', 'N/A')}")
                            return False
                    else:
                        print(f"❌ HTTP错误: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    
    async def test_prompt_enhanced_chat(self):
        """测试使用提示词模板的聊天"""
        print("\n💬 测试提示词增强聊天")
        print("-" * 40)
        
        test_cases = [
            {
                "name": "金融分析任务",
                "model": "auto",
                "task_type": "financial_analysis",
                "messages": [{"role": "user", "content": "分析AAPL股票的投资价值"}]
            },
            {
                "name": "代码生成任务",
                "model": "deepseek-coder",
                "task_type": "code_generation", 
                "messages": [{"role": "user", "content": "写一个计算股票移动平均线的Python函数"}]
            },
            {
                "name": "通用任务",
                "model": "auto",
                "task_type": "general",
                "messages": [{"role": "user", "content": "什么是人工智能？"}]
            }
        ]
        
        results = {}
        
        for test_case in test_cases:
            try:
                print(f"\n🔍 测试: {test_case['name']}")
                
                payload = {
                    "model": test_case["model"],
                    "messages": test_case["messages"],
                    "task_type": test_case["task_type"],
                    "max_tokens": 200,
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
                            
                            model_used = data.get('model', 'unknown')
                            choices = data.get('choices', [])
                            
                            if choices:
                                content = choices[0].get('message', {}).get('content', '')
                                print(f"  ✅ 成功 (模型: {model_used})")
                                print(f"  📝 回复: {content[:100]}...")
                                results[test_case['name']] = True
                            else:
                                print(f"  ❌ 无回复内容")
                                results[test_case['name']] = False
                        else:
                            error_text = await response.text()
                            print(f"  ❌ HTTP错误: {response.status}")
                            print(f"  📄 错误: {error_text[:100]}...")
                            results[test_case['name']] = False
                
                # 避免频率限制
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"  ❌ 异常: {e}")
                results[test_case['name']] = False
        
        # 显示测试结果
        print(f"\n📊 测试结果汇总:")
        for test_name, success in results.items():
            emoji = "✅" if success else "❌"
            print(f"  {emoji} {test_name}")
        
        return all(results.values())
    
    async def test_reload_prompts(self):
        """测试重新加载提示词"""
        print("\n🔄 测试重新加载提示词")
        print("-" * 40)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/v1/admin/reload-prompts", timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('success'):
                            message = data.get('message', '')
                            stats = data.get('stats', {})
                            
                            print(f"✅ {message}")
                            print(f"📊 总模板数: {stats.get('total_templates', 0)}")
                            
                            return True
                        else:
                            print(f"❌ 重新加载失败: {data.get('message', 'N/A')}")
                            return False
                    else:
                        error_text = await response.text()
                        print(f"❌ HTTP错误: {response.status}")
                        print(f"📄 错误: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 提示词管理完整测试")
        print("=" * 60)
        
        tests = [
            ("提示词模板列表", self.test_prompt_templates_list()),
            ("提示词统计", self.test_prompt_stats()),
            ("提示词增强聊天", self.test_prompt_enhanced_chat()),
            ("重新加载提示词", self.test_reload_prompts())
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
            print("🎉 所有测试通过！提示词管理系统工作正常")
        else:
            print("⚠️ 部分测试失败，请检查提示词配置")

async def main():
    """主函数"""
    tester = PromptManagementTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
