#!/usr/bin/env python3
"""
TradingAgents 后端微服务测试脚本
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import os
import sys

# 添加backend目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MicroservicesTester:
    """微服务测试器"""
    
    def __init__(self):
        self.base_urls = {
            'api_gateway': 'http://localhost:8000',
            'analysis_engine': 'http://localhost:8001', 
            'data_service': 'http://localhost:8002',
            'task_scheduler': 'http://localhost:8003',
            'llm_service': 'http://localhost:8004',
            'memory_service': 'http://localhost:8006',
            'agent_service': 'http://localhost:8008'
        }
        
        self.test_stocks = ['000001', '600519', '000002']
        self.results = []
        
    async def run_all_tests(self):
        """运行所有测试"""
        logger.info("🚀 开始后端微服务测试...")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # 1. 健康检查测试
            await self.test_health_checks()
            
            # 2. 数据服务测试
            await self.test_data_service()
            
            # 3. LLM服务测试
            await self.test_llm_service()
            
            # 4. 分析引擎测试
            await self.test_analysis_engine()
            
            # 5. API网关测试
            await self.test_api_gateway()
            
            # 6. 集成测试
            await self.test_integration()
        
        # 生成测试报告
        self.generate_report()
    
    async def test_health_checks(self):
        """测试所有服务的健康检查"""
        logger.info("📋 TC001: 系统健康检查测试")
        
        for service_name, base_url in self.base_urls.items():
            try:
                start_time = time.time()
                async with self.session.get(f"{base_url}/health", timeout=10) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        self.record_result(
                            f"Health-{service_name}",
                            True,
                            f"服务正常 ({response_time:.2f}s)",
                            {"response_time": response_time, "data": data}
                        )
                        logger.info(f"✅ {service_name} 健康检查通过")
                    else:
                        self.record_result(
                            f"Health-{service_name}",
                            False,
                            f"状态码: {response.status}",
                            {"status": response.status}
                        )
                        logger.error(f"❌ {service_name} 健康检查失败")
                        
            except Exception as e:
                self.record_result(
                    f"Health-{service_name}",
                    False,
                    f"连接失败: {str(e)}",
                    {"error": str(e)}
                )
                logger.error(f"❌ {service_name} 连接失败: {e}")
    
    async def test_data_service(self):
        """测试数据服务功能"""
        logger.info("📊 TC002: 数据服务测试")
        
        for stock in self.test_stocks:
            # 测试股票信息查询
            await self.test_stock_info(stock)
            
            # 测试缓存机制
            await self.test_cache_mechanism(stock)
    
    async def test_stock_info(self, symbol: str):
        """测试股票信息查询"""
        try:
            url = f"{self.base_urls['data_service']}/api/stock/info/{symbol}"
            start_time = time.time()
            
            async with self.session.get(url, timeout=15) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # 验证数据格式
                    required_fields = ['symbol', 'name', 'market', 'industry']
                    missing_fields = [field for field in required_fields 
                                    if field not in data.get('data', {})]
                    
                    if not missing_fields and data['data']['name'] != '未知股票':
                        self.record_result(
                            f"StockInfo-{symbol}",
                            True,
                            f"数据完整 ({response_time:.2f}s)",
                            {"response_time": response_time, "stock_name": data['data']['name']}
                        )
                        logger.info(f"✅ {symbol} 股票信息查询成功: {data['data']['name']}")
                    else:
                        self.record_result(
                            f"StockInfo-{symbol}",
                            False,
                            f"数据不完整: {missing_fields}",
                            {"missing_fields": missing_fields, "data": data}
                        )
                        logger.warning(f"⚠️ {symbol} 股票信息不完整")
                else:
                    self.record_result(
                        f"StockInfo-{symbol}",
                        False,
                        f"状态码: {response.status}",
                        {"status": response.status}
                    )
                    
        except Exception as e:
            self.record_result(
                f"StockInfo-{symbol}",
                False,
                f"请求失败: {str(e)}",
                {"error": str(e)}
            )
            logger.error(f"❌ {symbol} 股票信息查询失败: {e}")
    
    async def test_cache_mechanism(self, symbol: str):
        """测试缓存机制"""
        try:
            url = f"{self.base_urls['data_service']}/api/stock/info/{symbol}"
            
            # 第一次请求（可能从缓存或数据源）
            start_time = time.time()
            async with self.session.get(url) as response:
                first_time = time.time() - start_time
                first_data = await response.json()
            
            # 第二次请求（应该从缓存）
            start_time = time.time()
            async with self.session.get(url) as response:
                second_time = time.time() - start_time
                second_data = await response.json()
            
            # 强制刷新请求
            start_time = time.time()
            async with self.session.get(f"{url}?force_refresh=true") as response:
                refresh_time = time.time() - start_time
                refresh_data = await response.json()
            
            # 验证缓存一致性（主要关注数据一致性）
            data_consistent = first_data['data'] == second_data['data']  # 数据应该一致

            if data_consistent:
                self.record_result(
                    f"Cache-{symbol}",
                    True,
                    f"缓存正常 (首次:{first_time:.2f}s, 缓存:{second_time:.2f}s, 刷新:{refresh_time:.2f}s)",
                    {
                        "first_time": first_time,
                        "second_time": second_time,
                        "refresh_time": refresh_time,
                        "data_consistent": data_consistent
                    }
                )
                logger.info(f"✅ {symbol} 缓存机制正常")
            else:
                self.record_result(
                    f"Cache-{symbol}",
                    False,
                    f"缓存数据不一致",
                    {
                        "first_time": first_time,
                        "second_time": second_time,
                        "refresh_time": refresh_time,
                        "data_consistent": data_consistent
                    }
                )
                logger.warning(f"⚠️ {symbol} 缓存数据不一致")
                
        except Exception as e:
            self.record_result(
                f"Cache-{symbol}",
                False,
                f"测试失败: {str(e)}",
                {"error": str(e)}
            )
            logger.error(f"❌ {symbol} 缓存测试失败: {e}")
    
    async def test_llm_service(self):
        """测试LLM服务"""
        logger.info("🤖 TC003: LLM服务测试")
        
        # 测试模型列表
        await self.test_llm_models()
        
        # 测试聊天完成
        await self.test_llm_chat()
        
        # 测试使用统计
        await self.test_llm_usage()
    
    async def test_llm_models(self):
        """测试LLM模型列表"""
        try:
            url = f"{self.base_urls['llm_service']}/api/v1/models"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    # LLM服务返回的是 {"data": [...]} 格式
                    models = data.get('data', [])

                    if models and isinstance(models, list):
                        self.record_result(
                            "LLM-Models",
                            True,
                            f"发现 {len(models)} 个模型",
                            {"models": models}
                        )
                        logger.info(f"✅ LLM模型列表获取成功: {len(models)}个模型")
                    else:
                        self.record_result(
                            "LLM-Models",
                            False,
                            "未发现可用模型",
                            {"data": data}
                        )
                else:
                    self.record_result(
                        "LLM-Models",
                        False,
                        f"状态码: {response.status}",
                        {"status": response.status}
                    )
                    
        except Exception as e:
            self.record_result(
                "LLM-Models",
                False,
                f"请求失败: {str(e)}",
                {"error": str(e)}
            )
            logger.error(f"❌ LLM模型列表获取失败: {e}")
    
    async def test_llm_chat(self):
        """测试LLM聊天功能"""
        try:
            url = f"{self.base_urls['llm_service']}/api/v1/chat/completions"
            payload = {
                "messages": [
                    {"role": "user", "content": "请简单介绍一下股票投资的基本概念"}
                ],
                "model": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 100
            }
            
            start_time = time.time()
            async with self.session.post(url, json=payload, timeout=30) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()

                    # 检查OpenAI格式的响应
                    if 'choices' in data and len(data['choices']) > 0 and 'message' in data['choices'][0]:
                        content = data['choices'][0]['message'].get('content', '')
                        self.record_result(
                            "LLM-Chat",
                            True,
                            f"聊天成功 ({response_time:.2f}s)",
                            {"response_time": response_time, "response_length": len(content), "model": data.get('model')}
                        )
                        logger.info(f"✅ LLM聊天功能正常")
                    else:
                        self.record_result(
                            "LLM-Chat",
                            False,
                            "响应格式异常",
                            {"data": data}
                        )
                else:
                    self.record_result(
                        "LLM-Chat",
                        False,
                        f"状态码: {response.status}",
                        {"status": response.status}
                    )
                    
        except Exception as e:
            self.record_result(
                "LLM-Chat",
                False,
                f"请求失败: {str(e)}",
                {"error": str(e)}
            )
            logger.error(f"❌ LLM聊天测试失败: {e}")
    
    async def test_llm_usage(self):
        """测试LLM使用统计"""
        try:
            url = f"{self.base_urls['llm_service']}/api/v1/usage/stats"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    self.record_result(
                        "LLM-Usage",
                        True,
                        "使用统计获取成功",
                        {"data": data}
                    )
                    logger.info(f"✅ LLM使用统计正常")
                else:
                    self.record_result(
                        "LLM-Usage",
                        False,
                        f"状态码: {response.status}",
                        {"status": response.status}
                    )
                    
        except Exception as e:
            self.record_result(
                "LLM-Usage",
                False,
                f"请求失败: {str(e)}",
                {"error": str(e)}
            )
            logger.error(f"❌ LLM使用统计测试失败: {e}")
    
    async def test_analysis_engine(self):
        """测试分析引擎"""
        logger.info("🔍 TC004: 分析引擎测试")
        
        # 测试启动分析
        analysis_id = await self.test_start_analysis()
        
        if analysis_id:
            # 测试查询进度
            await self.test_analysis_progress(analysis_id)
            
            # 等待分析完成并获取结果
            await self.test_analysis_result(analysis_id)
    
    async def test_start_analysis(self) -> Optional[str]:
        """测试启动分析"""
        try:
            url = f"{self.base_urls['analysis_engine']}/api/analysis/start"
            payload = {
                "stock_code": "000001",
                "market_type": "A股",
                "llm_provider": "dashscope"
            }
            
            async with self.session.post(url, json=payload, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    analysis_id = data.get('data', {}).get('analysis_id')
                    
                    if analysis_id:
                        self.record_result(
                            "Analysis-Start",
                            True,
                            f"分析启动成功: {analysis_id}",
                            {"analysis_id": analysis_id}
                        )
                        logger.info(f"✅ 分析启动成功: {analysis_id}")
                        return analysis_id
                    else:
                        self.record_result(
                            "Analysis-Start",
                            False,
                            "未返回分析ID",
                            {"data": data}
                        )
                else:
                    self.record_result(
                        "Analysis-Start",
                        False,
                        f"状态码: {response.status}",
                        {"status": response.status}
                    )
                    
        except Exception as e:
            self.record_result(
                "Analysis-Start",
                False,
                f"请求失败: {str(e)}",
                {"error": str(e)}
            )
            logger.error(f"❌ 分析启动失败: {e}")
        
        return None
    
    async def test_analysis_progress(self, analysis_id: str):
        """测试分析进度查询"""
        try:
            url = f"{self.base_urls['analysis_engine']}/api/analysis/{analysis_id}/progress"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    progress = data.get('data', {}).get('progress', 0)
                    
                    self.record_result(
                        "Analysis-Progress",
                        True,
                        f"进度查询成功: {progress}%",
                        {"progress": progress, "data": data}
                    )
                    logger.info(f"✅ 分析进度查询成功: {progress}%")
                else:
                    self.record_result(
                        "Analysis-Progress",
                        False,
                        f"状态码: {response.status}",
                        {"status": response.status}
                    )
                    
        except Exception as e:
            self.record_result(
                "Analysis-Progress",
                False,
                f"请求失败: {str(e)}",
                {"error": str(e)}
            )
            logger.error(f"❌ 分析进度查询失败: {e}")
    
    async def test_analysis_result(self, analysis_id: str):
        """测试分析结果获取"""
        try:
            # 等待分析完成（最多等待30秒）
            for i in range(30):
                url = f"{self.base_urls['analysis_engine']}/api/analysis/{analysis_id}/result"
                async with self.session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()

                        # 检查分析是否完成：有success=True且有分析结果数据
                        if (data.get('success') and
                            data.get('data', {}).get('recommendation') and
                            data.get('data', {}).get('reasoning')):
                            self.record_result(
                                "Analysis-Result",
                                True,
                                "分析结果获取成功",
                                {"data": data}
                            )
                            logger.info(f"✅ 分析结果获取成功")
                            return
                        elif not data.get('success'):
                            self.record_result(
                                "Analysis-Result",
                                False,
                                "分析失败",
                                {"data": data}
                            )
                            logger.error(f"❌ 分析失败")
                            return
                
                await asyncio.sleep(1)  # 等待1秒后重试
            
            # 超时
            self.record_result(
                "Analysis-Result",
                False,
                "分析超时（30秒）",
                {"timeout": True}
            )
            logger.warning(f"⚠️ 分析超时")
            
        except Exception as e:
            self.record_result(
                "Analysis-Result",
                False,
                f"请求失败: {str(e)}",
                {"error": str(e)}
            )
            logger.error(f"❌ 分析结果获取失败: {e}")
    
    async def test_api_gateway(self):
        """测试API网关"""
        logger.info("🌐 TC005: API网关测试")
        
        # 测试通过网关访问股票信息
        for stock in self.test_stocks[:1]:  # 只测试一个股票
            await self.test_gateway_stock_info(stock)
    
    async def test_gateway_stock_info(self, symbol: str):
        """测试通过网关访问股票信息"""
        try:
            # 测试普通请求
            url = f"{self.base_urls['api_gateway']}/api/stock/info/{symbol}"
            async with self.session.get(url, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # 测试强制刷新
                    refresh_url = f"{url}?force_refresh=true"
                    async with self.session.get(refresh_url, timeout=15) as refresh_response:
                        if refresh_response.status == 200:
                            refresh_data = await refresh_response.json()
                            
                            self.record_result(
                                f"Gateway-{symbol}",
                                True,
                                "网关路由正常",
                                {
                                    "normal_request": data['data']['name'],
                                    "refresh_request": refresh_data['data']['name']
                                }
                            )
                            logger.info(f"✅ 网关路由测试成功: {symbol}")
                        else:
                            self.record_result(
                                f"Gateway-{symbol}",
                                False,
                                f"强制刷新失败: {refresh_response.status}",
                                {"status": refresh_response.status}
                            )
                else:
                    self.record_result(
                        f"Gateway-{symbol}",
                        False,
                        f"状态码: {response.status}",
                        {"status": response.status}
                    )
                    
        except Exception as e:
            self.record_result(
                f"Gateway-{symbol}",
                False,
                f"请求失败: {str(e)}",
                {"error": str(e)}
            )
            logger.error(f"❌ 网关测试失败: {e}")
    
    async def test_integration(self):
        """集成测试"""
        logger.info("🔗 TC006: 集成测试")
        
        # 测试完整的分析流程（通过网关）
        await self.test_full_analysis_workflow()
    
    async def test_full_analysis_workflow(self):
        """测试完整分析工作流"""
        try:
            # 1. 通过网关获取股票信息
            stock_url = f"{self.base_urls['api_gateway']}/api/stock/info/000001"
            async with self.session.get(stock_url, timeout=15) as response:
                if response.status != 200:
                    raise Exception(f"股票信息获取失败: {response.status}")
                stock_data = await response.json()
            
            # 2. 通过网关启动分析
            analysis_url = f"{self.base_urls['api_gateway']}/api/analysis/start"
            payload = {
                "stock_code": "000001",
                "market_type": "A股",
                "llm_provider": "dashscope"
            }
            
            async with self.session.post(analysis_url, json=payload, timeout=15) as response:
                if response.status == 200:
                    analysis_data = await response.json()
                    analysis_id = analysis_data.get('data', {}).get('analysis_id')
                    
                    if analysis_id:
                        self.record_result(
                            "Integration-Workflow",
                            True,
                            f"完整工作流测试成功: {analysis_id}",
                            {
                                "stock_name": stock_data['data']['name'],
                                "analysis_id": analysis_id
                            }
                        )
                        logger.info(f"✅ 完整工作流测试成功")
                    else:
                        self.record_result(
                            "Integration-Workflow",
                            False,
                            "分析启动失败",
                            {"data": analysis_data}
                        )
                else:
                    self.record_result(
                        "Integration-Workflow",
                        False,
                        f"分析启动状态码: {response.status}",
                        {"status": response.status}
                    )
                    
        except Exception as e:
            self.record_result(
                "Integration-Workflow",
                False,
                f"工作流测试失败: {str(e)}",
                {"error": str(e)}
            )
            logger.error(f"❌ 完整工作流测试失败: {e}")
    
    def record_result(self, test_name: str, passed: bool, message: str, details: Dict[str, Any]):
        """记录测试结果"""
        self.results.append({
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_report(self):
        """生成测试报告"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['passed'])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "pass_rate": f"{pass_rate:.1f}%",
                "test_time": datetime.now().isoformat()
            },
            "test_results": self.results
        }
        
        # 确保报告目录存在
        report_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "test")
        os.makedirs(report_dir, exist_ok=True)

        # 保存报告到文件
        report_file = os.path.join(report_dir, f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 打印摘要
        logger.info("📊 测试报告摘要:")
        logger.info(f"   总测试数: {total_tests}")
        logger.info(f"   通过数: {passed_tests}")
        logger.info(f"   失败数: {failed_tests}")
        logger.info(f"   通过率: {pass_rate:.1f}%")
        logger.info(f"   报告文件: {report_file}")
        
        # 打印失败的测试
        if failed_tests > 0:
            logger.info("❌ 失败的测试:")
            for result in self.results:
                if not result['passed']:
                    logger.info(f"   - {result['test_name']}: {result['message']}")

async def main():
    """主函数"""
    tester = MicroservicesTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        exit(1)
