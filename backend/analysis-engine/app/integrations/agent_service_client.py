"""
Agent Service客户端
用于与Agent Service进行集成的客户端
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from backend.shared.utils.logger import get_service_logger
from backend.shared.utils.config import get_service_config

logger = get_service_logger("analysis-engine.agent_client")


@dataclass
class AgentServiceConfig:
    """Agent Service配置"""
    base_url: str = "http://localhost:8002"
    timeout: int = 300
    max_retries: int = 3
    retry_delay: int = 5


class AgentServiceClient:
    """Agent Service客户端"""
    
    def __init__(self, config: Optional[AgentServiceConfig] = None):
        self.config = config or AgentServiceConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info(f"🔗 Agent Service客户端初始化: {self.config.base_url}")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()
    
    async def connect(self):
        """建立连接"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.info("🔗 Agent Service连接已建立")
    
    async def disconnect(self):
        """断开连接"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("🔗 Agent Service连接已断开")
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.session:
                await self.connect()
            
            async with self.session.get(f"{self.config.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("status") == "healthy"
                return False
                
        except Exception as e:
            logger.error(f"❌ Agent Service健康检查失败: {e}")
            return False
    
    async def start_comprehensive_analysis(
        self,
        stock_code: str,
        company_name: str,
        market: str = "CN",
        analysis_date: Optional[str] = None
    ) -> Optional[str]:
        """启动综合分析工作流"""
        try:
            if not self.session:
                await self.connect()
            
            # 准备工作流上下文
            context = {
                "symbol": stock_code,
                "company_name": company_name,
                "market": market,
                "analysis_date": analysis_date or datetime.now().strftime("%Y-%m-%d"),
                "analysis_type": "comprehensive",
                "source": "analysis_engine"
            }
            
            # 启动综合分析工作流
            payload = {
                "workflow_id": "comprehensive_analysis_v2",
                "context": context
            }
            
            async with self.session.post(
                f"{self.config.base_url}/api/v1/workflows/start",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    execution_id = data.get("execution_id")
                    logger.info(f"🚀 启动综合分析工作流: {execution_id}")
                    return execution_id
                else:
                    error_text = await response.text()
                    logger.error(f"❌ 启动工作流失败: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 启动综合分析失败: {e}")
            return None
    
    async def start_quick_analysis(
        self,
        stock_code: str,
        company_name: str,
        market: str = "CN",
        analysis_date: Optional[str] = None
    ) -> Optional[str]:
        """启动快速分析工作流"""
        try:
            if not self.session:
                await self.connect()
            
            # 准备工作流上下文
            context = {
                "symbol": stock_code,
                "company_name": company_name,
                "market": market,
                "analysis_date": analysis_date or datetime.now().strftime("%Y-%m-%d"),
                "analysis_type": "quick",
                "source": "analysis_engine"
            }
            
            # 启动快速分析工作流
            payload = {
                "workflow_id": "quick_analysis_v2",
                "context": context
            }
            
            async with self.session.post(
                f"{self.config.base_url}/api/v1/workflows/start",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    execution_id = data.get("execution_id")
                    logger.info(f"🚀 启动快速分析工作流: {execution_id}")
                    return execution_id
                else:
                    error_text = await response.text()
                    logger.error(f"❌ 启动工作流失败: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 启动快速分析失败: {e}")
            return None
    
    async def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """获取工作流执行状态"""
        try:
            if not self.session:
                await self.connect()
            
            async with self.session.get(
                f"{self.config.base_url}/api/v1/workflows/executions/{execution_id}/status"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                elif response.status == 404:
                    logger.warning(f"⚠️ 工作流执行不存在: {execution_id}")
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"❌ 获取工作流状态失败: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 获取工作流状态失败: {execution_id} - {e}")
            return None
    
    async def wait_for_completion(
        self,
        execution_id: str,
        max_wait_time: int = 300,
        poll_interval: int = 5
    ) -> Optional[Dict[str, Any]]:
        """等待工作流完成"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            while True:
                # 检查超时
                if asyncio.get_event_loop().time() - start_time > max_wait_time:
                    logger.warning(f"⏰ 工作流等待超时: {execution_id}")
                    return None
                
                # 获取状态
                status = await self.get_workflow_status(execution_id)
                if not status:
                    return None
                
                workflow_status = status.get("status", "unknown")
                
                if workflow_status == "completed":
                    logger.info(f"✅ 工作流完成: {execution_id}")
                    return status
                elif workflow_status == "failed":
                    logger.error(f"❌ 工作流失败: {execution_id}")
                    return status
                elif workflow_status == "cancelled":
                    logger.warning(f"🚫 工作流已取消: {execution_id}")
                    return status
                
                # 等待下次轮询
                await asyncio.sleep(poll_interval)
                
        except Exception as e:
            logger.error(f"❌ 等待工作流完成失败: {execution_id} - {e}")
            return None
    
    async def start_debate_analysis(
        self,
        stock_code: str,
        company_name: str,
        topic: Optional[str] = None,
        participants: Optional[List[str]] = None
    ) -> Optional[str]:
        """启动辩论分析"""
        try:
            if not self.session:
                await self.connect()
            
            # 准备辩论请求
            payload = {
                "topic": topic or f"{stock_code} 投资决策辩论",
                "participants": participants or ["bull_researcher", "bear_researcher", "neutral_debator"],
                "context": {
                    "symbol": stock_code,
                    "company_name": company_name,
                    "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                    "source": "analysis_engine"
                }
            }
            
            async with self.session.post(
                f"{self.config.base_url}/api/v1/debate/start",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    debate_id = data.get("debate_id")
                    logger.info(f"🗣️ 启动辩论分析: {debate_id}")
                    return debate_id
                else:
                    error_text = await response.text()
                    logger.error(f"❌ 启动辩论失败: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 启动辩论分析失败: {e}")
            return None
    
    async def get_debate_status(self, debate_id: str) -> Optional[Dict[str, Any]]:
        """获取辩论状态"""
        try:
            if not self.session:
                await self.connect()
            
            async with self.session.get(
                f"{self.config.base_url}/api/v1/debate/{debate_id}/status"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"❌ 获取辩论状态失败: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 获取辩论状态失败: {debate_id} - {e}")
            return None
    
    async def get_system_metrics(self) -> Optional[Dict[str, Any]]:
        """获取系统性能指标"""
        try:
            if not self.session:
                await self.connect()
            
            async with self.session.get(
                f"{self.config.base_url}/api/v1/monitoring/system/metrics"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"❌ 获取系统指标失败: {e}")
            return None
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """取消工作流执行"""
        try:
            if not self.session:
                await self.connect()
            
            async with self.session.post(
                f"{self.config.base_url}/api/v1/workflows/executions/{execution_id}/cancel"
            ) as response:
                if response.status == 200:
                    logger.info(f"🚫 工作流已取消: {execution_id}")
                    return True
                else:
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 取消工作流失败: {execution_id} - {e}")
            return False


# 全局客户端实例
_agent_service_client: Optional[AgentServiceClient] = None


async def get_agent_service_client() -> AgentServiceClient:
    """获取Agent Service客户端实例"""
    global _agent_service_client
    
    if _agent_service_client is None:
        # 从配置获取Agent Service地址
        config = get_service_config("analysis_engine")
        agent_service_config = AgentServiceConfig(
            base_url=config.get("agent_service_url", "http://localhost:8002"),
            timeout=config.get("agent_service_timeout", 300)
        )
        
        _agent_service_client = AgentServiceClient(agent_service_config)
        await _agent_service_client.connect()
    
    return _agent_service_client


async def cleanup_agent_service_client():
    """清理Agent Service客户端"""
    global _agent_service_client
    
    if _agent_service_client:
        await _agent_service_client.disconnect()
        _agent_service_client = None
