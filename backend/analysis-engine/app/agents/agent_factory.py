"""
智能体工厂
负责创建和管理各种分析师智能体
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class AgentFactory:
    """智能体工厂类"""
    
    def __init__(self, llm_service_url: str = "http://localhost:8004"):
        self.llm_service_url = llm_service_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.agents: Dict[str, BaseAgent] = {}
        self.initialized = False
    
    async def initialize(self):
        """初始化智能体工厂"""
        try:
            logger.info("🤖 初始化智能体工厂...")
            
            # 创建HTTP会话
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=120)
            )
            
            # 测试LLM服务连接
            await self._test_llm_service()
            
            # 注册智能体
            await self._register_agents()
            
            self.initialized = True
            logger.info(f"✅ 智能体工厂初始化完成，注册{len(self.agents)}个智能体")
            
        except Exception as e:
            logger.error(f"❌ 智能体工厂初始化失败: {e}")
            raise
    
    async def _test_llm_service(self):
        """测试LLM服务连接"""
        try:
            if self.session:
                async with self.session.get(f"{self.llm_service_url}/health") as response:
                    if response.status == 200:
                        logger.info("✅ LLM服务连接正常")
                    else:
                        logger.warning(f"⚠️ LLM服务响应异常: {response.status}")
        except Exception as e:
            logger.warning(f"⚠️ LLM服务连接失败: {e}")
    
    async def _register_agents(self):
        """注册智能体"""
        
        # 基本面分析师
        self.agents["fundamentals_analyst"] = BaseAgent(
            agent_type="fundamentals_analyst",
            task_type="fundamentals_analysis",
            description="专业的基本面分析师，负责财务分析和估值评估"
        )
        
        # 技术分析师
        self.agents["technical_analyst"] = BaseAgent(
            agent_type="technical_analyst",
            task_type="technical_analysis",
            description="专业的技术分析师，负责价格趋势和技术指标分析"
        )
        
        # 新闻分析师
        self.agents["news_analyst"] = BaseAgent(
            agent_type="news_analyst",
            task_type="news_analysis",
            description="专业的新闻分析师，负责新闻和情绪分析"
        )
        
        # 看涨研究员
        self.agents["bull_researcher"] = BaseAgent(
            agent_type="bull_researcher",
            task_type="bull_analysis",
            description="看涨研究员，负责构建看涨投资案例"
        )
        
        # 看跌研究员
        self.agents["bear_researcher"] = BaseAgent(
            agent_type="bear_researcher",
            task_type="bear_analysis",
            description="看跌研究员，负责识别投资风险和看跌因素"
        )
        
        # 风险管理师
        self.agents["risk_manager"] = BaseAgent(
            agent_type="risk_manager",
            task_type="risk_management",
            description="风险管理师，负责风险评估和控制建议"
        )
        
        # 研究主管
        self.agents["research_manager"] = BaseAgent(
            agent_type="research_manager",
            task_type="research_management",
            description="研究主管，负责综合决策和投资建议"
        )
        
        logger.info(f"📝 注册了{len(self.agents)}个智能体")
    
    async def call_agent(self, agent_type: str, **kwargs) -> Dict[str, Any]:
        """调用智能体"""
        if not self.initialized:
            raise RuntimeError("智能体工厂未初始化")
        
        if agent_type not in self.agents:
            raise ValueError(f"智能体类型不存在: {agent_type}")
        
        agent = self.agents[agent_type]
        
        try:
            logger.info(f"🤖 调用智能体: {agent_type}")
            start_time = datetime.now()
            
            # 准备请求数据
            request_data = await self._prepare_agent_request(agent, **kwargs)
            
            # 调用LLM服务
            result = await self._call_llm_service(request_data)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✅ 智能体调用完成: {agent_type} ({duration:.2f}s)")
            
            # 处理响应
            return await self._process_agent_response(agent_type, result, duration)
            
        except Exception as e:
            logger.error(f"❌ 智能体调用失败: {agent_type} - {e}")
            return {
                "success": False,
                "agent_type": agent_type,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _prepare_agent_request(self, agent: BaseAgent, **kwargs) -> Dict[str, Any]:
        """准备智能体请求"""
        
        # 构建用户消息
        user_message = await self._build_user_message(agent.agent_type, **kwargs)
        
        # 准备请求数据
        request_data = {
            "model": "deepseek-chat",  # 默认使用DeepSeek
            "task_type": agent.task_type,
            "messages": [
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 1500,
            "temperature": 0.1,
            "user_id": f"analysis_engine_{agent.agent_type}"
        }
        
        return request_data
    
    async def _build_user_message(self, agent_type: str, **kwargs) -> str:
        """构建用户消息"""
        
        symbol = kwargs.get("symbol", "UNKNOWN")
        company_name = kwargs.get("company_name", symbol)
        current_date = kwargs.get("current_date", datetime.now().strftime("%Y-%m-%d"))
        
        if agent_type == "fundamentals_analyst":
            return f"请对 {symbol} ({company_name}) 进行全面的基本面分析。当前日期：{current_date}"
        
        elif agent_type == "technical_analyst":
            return f"请对 {symbol} ({company_name}) 进行详细的技术分析。当前日期：{current_date}"
        
        elif agent_type == "news_analyst":
            return f"请分析 {symbol} ({company_name}) 的最新新闻和市场情绪。当前日期：{current_date}"
        
        elif agent_type == "bull_researcher":
            bear_argument = kwargs.get("bear_argument", "")
            context = f"看跌观点：{bear_argument}" if bear_argument else ""
            return f"请为 {symbol} ({company_name}) 构建强有力的看涨投资案例。{context} 当前日期：{current_date}"
        
        elif agent_type == "bear_researcher":
            bull_argument = kwargs.get("bull_argument", "")
            context = f"看涨观点：{bull_argument}" if bull_argument else ""
            return f"请为 {symbol} ({company_name}) 分析投资风险和看跌因素。{context} 当前日期：{current_date}"
        
        elif agent_type == "risk_manager":
            return f"请对 {symbol} ({company_name}) 进行全面的风险管理分析。当前日期：{current_date}"
        
        elif agent_type == "research_manager":
            # 综合所有报告
            reports = []
            if kwargs.get("fundamentals_report"):
                reports.append(f"基本面报告：{kwargs['fundamentals_report']}")
            if kwargs.get("technical_report"):
                reports.append(f"技术面报告：{kwargs['technical_report']}")
            if kwargs.get("bull_analysis"):
                reports.append(f"看涨分析：{kwargs['bull_analysis']}")
            if kwargs.get("bear_analysis"):
                reports.append(f"看跌分析：{kwargs['bear_analysis']}")
            if kwargs.get("risk_assessment"):
                reports.append(f"风险评估：{kwargs['risk_assessment']}")
            
            context = "\n\n".join(reports) if reports else "暂无详细报告"
            
            return f"请综合分析 {symbol} ({company_name}) 的投资价值并做出最终决策。\n\n{context}\n\n当前日期：{current_date}"
        
        else:
            return f"请分析 {symbol} ({company_name})。当前日期：{current_date}"
    
    async def _call_llm_service(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """调用LLM服务 - 现在通过Agent Service"""
        if not self.session:
            raise RuntimeError("HTTP会话未初始化")

        # 映射Analysis Engine的智能体类型到Agent Service的智能体类型
        agent_type_mapping = {
            "technical_analyst": "market_analyst",
            "fundamentals_analyst": "fundamentals_analyst",
            "news_analyst": "news_analyst",
            "bull_researcher": "bull_researcher",
            "bear_researcher": "bear_researcher",
            "risk_manager": "risk_manager",
            "research_manager": "research_manager"
        }

        original_agent_type = request_data.get("user_id", "").replace("analysis_engine_", "")
        mapped_agent_type = agent_type_mapping.get(original_agent_type, original_agent_type)

        # 将请求转换为Agent Service格式
        agent_service_request = {
            "agent_type": mapped_agent_type,
            "task_type": "technical_analysis" if mapped_agent_type == "market_analyst" else request_data.get("task_type", "analysis"),
            "data": {
                "symbol": self._extract_symbol_from_messages(request_data.get("messages", [])),
                "market": "CN",
                "messages": request_data.get("messages", []),
                "model": request_data.get("model", "deepseek-chat"),
                "temperature": request_data.get("temperature", 0.1),
                "max_tokens": request_data.get("max_tokens", 1500)
            }
        }

        logger.info(f"🔍 AgentFactory调用Agent Service: {agent_service_request['agent_type']}")

        try:
            # 调用Agent Service
            async with self.session.post(
                "http://localhost:8008/api/v1/agents/execute",
                json=agent_service_request
            ) as response:
                logger.info(f"🔍 Agent Service响应状态: {response.status}")

                if response.status == 200:
                    agent_response = await response.json()
                    logger.info(f"🔍 Agent Service响应: {agent_response}")

                    # 转换Agent Service响应为LLM Service格式
                    if agent_response.get("status") == "completed":
                        return {
                            "choices": [{
                                "message": {
                                    "role": "assistant",
                                    "content": agent_response.get("result", "")
                                }
                            }],
                            "model": agent_response.get("agent_type", "unknown"),
                            "usage": {
                                "total_tokens": 0
                            }
                        }
                    else:
                        raise Exception(f"Agent Service任务失败: {agent_response.get('error', 'Unknown error')}")
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Agent Service错误: {response.status} - {error_text}")
                    raise Exception(f"Agent Service错误: {response.status} - {error_text}")

        except Exception as e:
            logger.error(f"❌ Agent Service调用失败，回退到LLM Service: {e}")

            # 回退到原始LLM Service
            async with self.session.post(
                f"{self.llm_service_url}/api/v1/chat/completions",
                json=request_data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"LLM服务错误: {response.status} - {error_text}")

    def _extract_symbol_from_messages(self, messages: List[Dict[str, Any]]) -> str:
        """从消息中提取股票代码"""
        for message in messages:
            content = message.get("content", "")
            # 简单的正则表达式匹配股票代码
            import re
            match = re.search(r'\b(\d{6})\b', content)
            if match:
                return match.group(1)
        return "000001"  # 默认值

    async def _process_agent_response(self, agent_type: str, llm_response: Dict[str, Any],
                                    duration: float) -> Dict[str, Any]:
        """处理智能体响应"""

        if not llm_response.get("choices"):
            return {
                "success": False,
                "agent_type": agent_type,
                "error": "LLM服务无响应",
                "timestamp": datetime.now().isoformat()
            }

        content = llm_response["choices"][0]["message"]["content"]
        model_used = llm_response.get("model", "unknown")

        # 将LLM响应转换为LangChain AIMessage对象
        from langchain_core.messages import AIMessage
        ai_message = AIMessage(content=content)

        # 根据智能体类型处理响应
        result = {
            "success": True,
            "agent_type": agent_type,
            "model_used": model_used,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "messages": [ai_message]  # 使用AIMessage对象而不是字典
        }
        
        if agent_type in ["fundamentals_analyst", "technical_analyst", "news_analyst"]:
            result["report"] = content
            if agent_type == "news_analyst":
                result["sentiment"] = self._extract_sentiment(content)
        
        elif agent_type in ["bull_researcher", "bear_researcher"]:
            result["analysis"] = content
        
        elif agent_type == "risk_manager":
            result["assessment"] = content
        
        elif agent_type == "research_manager":
            result["recommendation"] = content
            result["plan"] = self._extract_investment_plan(content)
        
        else:
            result["content"] = content
        
        return result
    
    def _extract_sentiment(self, content: str) -> str:
        """从新闻分析中提取情绪"""
        # 简化的情绪提取逻辑
        content_lower = content.lower()
        
        positive_words = ["积极", "乐观", "看好", "利好", "上涨", "增长"]
        negative_words = ["消极", "悲观", "看空", "利空", "下跌", "下降"]
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return "积极"
        elif negative_count > positive_count:
            return "消极"
        else:
            return "中性"
    
    def _extract_investment_plan(self, content: str) -> str:
        """从研究主管报告中提取投资计划"""
        # 简化的投资计划提取逻辑
        lines = content.split('\n')
        plan_lines = []
        
        for line in lines:
            if any(keyword in line for keyword in ["建议", "策略", "计划", "操作", "目标"]):
                plan_lines.append(line.strip())
        
        return '\n'.join(plan_lines) if plan_lines else "请参考完整分析报告"
    
    async def get_available_agents(self) -> List[Dict[str, Any]]:
        """获取可用智能体列表"""
        agents_list = []
        
        for agent_type, agent in self.agents.items():
            agents_list.append({
                "agent_type": agent_type,
                "task_type": agent.task_type,
                "description": agent.description
            })
        
        return agents_list
    
    async def reload(self):
        """重新加载智能体工厂"""
        logger.info("🔄 重新加载智能体工厂...")
        
        # 重新测试连接
        await self._test_llm_service()
        
        logger.info("✅ 智能体工厂重新加载完成")
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理智能体工厂资源...")
        
        if self.session:
            await self.session.close()
            self.session = None
        
        self.agents.clear()
        self.initialized = False
        
        logger.info("✅ 智能体工厂资源清理完成")
