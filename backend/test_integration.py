"""
集成测试脚本
测试Analysis Engine与Agent Service的集成
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional


class IntegrationTester:
    """集成测试器"""
    
    def __init__(self):
        self.analysis_engine_url = "http://localhost:8000"
        self.agent_service_url = "http://localhost:8002"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def test_services_health(self):
        """测试服务健康状态"""
        print("🏥 测试服务健康状态...")
        
        # 测试Analysis Engine
        try:
            async with self.session.get(f"{self.analysis_engine_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Analysis Engine: {data.get('status', 'unknown')}")
                    
                    # 显示依赖状态
                    dependencies = data.get('dependencies', {})
                    for dep, status in dependencies.items():
                        status_icon = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
                        print(f"      {status_icon} {dep}: {status}")
                else:
                    print(f"   ❌ Analysis Engine: HTTP {response.status}")
        except Exception as e:
            print(f"   ❌ Analysis Engine: 连接失败 - {e}")
        
        # 测试Agent Service
        try:
            async with self.session.get(f"{self.agent_service_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Agent Service: {data.get('status', 'unknown')}")
                    
                    # 显示组件状态
                    components = data.get('components', {})
                    for comp, status in components.items():
                        status_icon = "✅" if status else "❌"
                        print(f"      {status_icon} {comp}: {'healthy' if status else 'unhealthy'}")
                else:
                    print(f"   ❌ Agent Service: HTTP {response.status}")
        except Exception as e:
            print(f"   ❌ Agent Service: 连接失败 - {e}")
    
    async def test_analysis_capabilities(self):
        """测试分析能力"""
        print("\n🔍 测试分析能力...")
        
        try:
            async with self.session.get(f"{self.analysis_engine_url}/capabilities") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        capabilities = data.get('data', {})
                        print("   📊 可用分析能力:")
                        for capability, available in capabilities.items():
                            status_icon = "✅" if available else "❌"
                            print(f"      {status_icon} {capability}: {'可用' if available else '不可用'}")
                    else:
                        print(f"   ❌ 获取能力失败: {data.get('message')}")
                else:
                    print(f"   ❌ HTTP {response.status}")
        except Exception as e:
            print(f"   ❌ 测试分析能力失败: {e}")
    
    async def test_agent_service_direct(self):
        """直接测试Agent Service"""
        print("\n🤖 直接测试Agent Service...")
        
        # 测试工作流定义
        try:
            async with self.session.get(f"{self.agent_service_url}/api/v1/workflows/definitions") as response:
                if response.status == 200:
                    data = await response.json()
                    definitions = data.get('definitions', {})
                    print(f"   📋 可用工作流: {len(definitions)}个")
                    for workflow_id, definition in definitions.items():
                        print(f"      - {workflow_id}: {definition.get('name')} ({definition.get('steps_count')}步骤)")
                else:
                    print(f"   ❌ 获取工作流定义失败: HTTP {response.status}")
        except Exception as e:
            print(f"   ❌ 测试工作流定义失败: {e}")
        
        # 测试系统指标
        try:
            async with self.session.get(f"{self.agent_service_url}/api/v1/monitoring/system/metrics") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   📊 系统指标:")
                    print(f"      - CPU使用率: {data.get('cpu_usage', 0):.1f}%")
                    print(f"      - 内存使用率: {data.get('memory_usage', 0):.1f}%")
                    print(f"      - 活跃任务: {data.get('tasks', {}).get('active', 0)}")
                else:
                    print(f"   ❌ 获取系统指标失败: HTTP {response.status}")
        except Exception as e:
            print(f"   ❌ 测试系统指标失败: {e}")
    
    async def test_integrated_analysis(self, stock_code: str = "000001"):
        """测试集成分析"""
        print(f"\n📈 测试集成分析: {stock_code}")
        
        # 准备分析请求
        analysis_request = {
            "stock_code": stock_code,
            "market_type": "A股",
            "analysis_date": datetime.now().isoformat(),
            "research_depth": 3,
            "market_analyst": True,
            "fundamental_analyst": True,
            "news_analyst": False,
            "social_analyst": False
        }
        
        try:
            # 启动分析
            async with self.session.post(
                f"{self.analysis_engine_url}/api/analysis/start",
                json=analysis_request
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        analysis_id = data.get('data', {}).get('analysis_id')
                        analysis_type = data.get('data', {}).get('analysis_type')
                        print(f"   🚀 分析已启动: {analysis_id}")
                        print(f"   📊 分析类型: {analysis_type}")
                        
                        # 监控分析进度
                        await self._monitor_analysis_progress(analysis_id)
                        
                        # 获取分析结果
                        await self._get_analysis_result(analysis_id)
                        
                    else:
                        print(f"   ❌ 启动分析失败: {data.get('message')}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ HTTP {response.status}: {error_text}")
        except Exception as e:
            print(f"   ❌ 测试集成分析失败: {e}")
    
    async def _monitor_analysis_progress(self, analysis_id: str):
        """监控分析进度"""
        print("   📊 监控分析进度...")
        
        max_wait_time = 300  # 5分钟
        poll_interval = 5    # 5秒
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                async with self.session.get(
                    f"{self.analysis_engine_url}/api/analysis/{analysis_id}/progress"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success'):
                            progress_data = data.get('data', {})
                            status = progress_data.get('status')
                            percentage = progress_data.get('progress_percentage', 0)
                            current_step = progress_data.get('current_step', '')
                            current_task = progress_data.get('current_task', '')
                            
                            print(f"      📈 {percentage}% - {current_step}: {current_task}")
                            
                            if status in ['completed', 'failed', 'cancelled']:
                                if status == 'completed':
                                    print("   ✅ 分析完成!")
                                else:
                                    error_msg = progress_data.get('error_message', '')
                                    print(f"   ❌ 分析{status}: {error_msg}")
                                return
                    else:
                        print(f"      ❌ 获取进度失败: HTTP {response.status}")
                        return
                        
            except Exception as e:
                print(f"      ❌ 监控进度失败: {e}")
                return
            
            await asyncio.sleep(poll_interval)
        
        print("   ⏰ 分析超时")
    
    async def _get_analysis_result(self, analysis_id: str):
        """获取分析结果"""
        print("   📋 获取分析结果...")
        
        try:
            async with self.session.get(
                f"{self.analysis_engine_url}/api/analysis/{analysis_id}/result"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        result = data.get('data', {})
                        print(f"      📊 股票代码: {result.get('stock_code')}")
                        print(f"      📈 投资建议: {result.get('recommendation')}")
                        print(f"      🎯 置信度: {result.get('confidence')}")
                        print(f"      ⚠️ 风险评分: {result.get('risk_score')}")
                        print(f"      💭 分析推理: {result.get('reasoning', '')[:100]}...")
                        
                        # 显示分析配置
                        analysis_config = result.get('analysis_config', {})
                        analysis_type = analysis_config.get('analysis_type', 'unknown')
                        agent_service_used = analysis_config.get('agent_service_used', False)
                        print(f"      🔧 分析类型: {analysis_type}")
                        print(f"      🤖 使用Agent Service: {'是' if agent_service_used else '否'}")
                    else:
                        print(f"      ❌ 获取结果失败: {data.get('message')}")
                elif response.status == 404:
                    print("      ⚠️ 分析结果不存在")
                else:
                    print(f"      ❌ HTTP {response.status}")
        except Exception as e:
            print(f"      ❌ 获取分析结果失败: {e}")
    
    async def test_workflow_direct(self):
        """直接测试工作流"""
        print("\n🔄 直接测试工作流...")
        
        # 准备工作流上下文
        context = {
            "symbol": "000001",
            "company_name": "平安银行",
            "market": "CN",
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "test_mode": True
        }
        
        try:
            # 启动快速分析工作流
            payload = {
                "workflow_id": "quick_analysis_v2",
                "context": context
            }
            
            async with self.session.post(
                f"{self.agent_service_url}/api/v1/workflows/start",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    execution_id = data.get('execution_id')
                    print(f"   🚀 工作流已启动: {execution_id}")
                    
                    # 监控工作流状态
                    await self._monitor_workflow_status(execution_id)
                else:
                    error_text = await response.text()
                    print(f"   ❌ 启动工作流失败: HTTP {response.status} - {error_text}")
        except Exception as e:
            print(f"   ❌ 测试工作流失败: {e}")
    
    async def _monitor_workflow_status(self, execution_id: str):
        """监控工作流状态"""
        print("   📊 监控工作流状态...")
        
        max_wait_time = 180  # 3分钟
        poll_interval = 5    # 5秒
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                async with self.session.get(
                    f"{self.agent_service_url}/api/v1/workflows/executions/{execution_id}/status"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        status = data.get('status')
                        current_step_index = data.get('current_step_index', 0)
                        completed_steps = data.get('completed_steps', [])
                        failed_steps = data.get('failed_steps', [])
                        
                        print(f"      🔄 状态: {status}, 步骤: {current_step_index}, 完成: {len(completed_steps)}, 失败: {len(failed_steps)}")
                        
                        if status in ['completed', 'failed', 'cancelled']:
                            if status == 'completed':
                                print("   ✅ 工作流完成!")
                                final_result = data.get('final_result', {})
                                if final_result:
                                    print(f"      📊 最终结果: {json.dumps(final_result, ensure_ascii=False, indent=2)[:200]}...")
                            else:
                                error = data.get('error', '')
                                print(f"   ❌ 工作流{status}: {error}")
                            return
                    else:
                        print(f"      ❌ 获取工作流状态失败: HTTP {response.status}")
                        return
                        
            except Exception as e:
                print(f"      ❌ 监控工作流失败: {e}")
                return
            
            await asyncio.sleep(poll_interval)
        
        print("   ⏰ 工作流监控超时")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始集成测试...")
        print("=" * 60)
        
        # 测试服务健康状态
        await self.test_services_health()
        
        # 测试分析能力
        await self.test_analysis_capabilities()
        
        # 直接测试Agent Service
        await self.test_agent_service_direct()
        
        # 测试集成分析
        await self.test_integrated_analysis("000001")
        
        # 直接测试工作流
        await self.test_workflow_direct()
        
        print("\n" + "=" * 60)
        print("✅ 集成测试完成!")


async def main():
    """主函数"""
    async with IntegrationTester() as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
