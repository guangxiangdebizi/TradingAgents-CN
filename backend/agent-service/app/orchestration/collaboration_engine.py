"""
协作引擎
负责智能体间的协作编排和任务分发
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from backend.shared.logging_config import get_logger

logger = get_logger("agent-service.collaboration_engine")


class CollaborationMode(Enum):
    """协作模式枚举"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"      # 并行执行
    PIPELINE = "pipeline"      # 流水线执行
    DEBATE = "debate"          # 辩论模式


class CollaborationEngine:
    """协作引擎"""
    
    def __init__(self, agent_manager, state_manager, message_router):
        self.agent_manager = agent_manager
        self.state_manager = state_manager
        self.message_router = message_router
        
        # 协作会话
        self.active_collaborations: Dict[str, Dict[str, Any]] = {}
        
        # 工作流定义
        self.workflow_definitions = self._initialize_workflows()
        
        logger.info("🏗️ 协作引擎初始化")
    
    async def initialize(self):
        """初始化协作引擎"""
        try:
            logger.info("✅ 协作引擎初始化完成")
        except Exception as e:
            logger.error(f"❌ 协作引擎初始化失败: {e}")
            raise
    
    def _initialize_workflows(self) -> Dict[str, Dict[str, Any]]:
        """初始化工作流定义"""
        return {
            "comprehensive_analysis": {
                "name": "综合分析工作流",
                "mode": CollaborationMode.PARALLEL,
                "steps": [
                    {
                        "name": "data_collection",
                        "agents": ["data_collector"],
                        "parallel": False
                    },
                    {
                        "name": "parallel_analysis",
                        "agents": ["fundamentals_analyst", "market_analyst", "news_analyst"],
                        "parallel": True
                    },
                    {
                        "name": "research_debate",
                        "agents": ["bull_researcher", "bear_researcher"],
                        "parallel": False,
                        "mode": "debate"
                    },
                    {
                        "name": "management_review",
                        "agents": ["research_manager", "risk_manager"],
                        "parallel": False
                    },
                    {
                        "name": "final_decision",
                        "agents": ["trader"],
                        "parallel": False
                    }
                ]
            },
            "quick_analysis": {
                "name": "快速分析工作流",
                "mode": CollaborationMode.SEQUENTIAL,
                "steps": [
                    {
                        "name": "market_analysis",
                        "agents": ["market_analyst"],
                        "parallel": False
                    },
                    {
                        "name": "risk_assessment",
                        "agents": ["risk_manager"],
                        "parallel": False
                    }
                ]
            }
        }
    
    async def start_collaboration(
        self,
        workflow_type: str,
        context: Dict[str, Any],
        participants: Optional[List[str]] = None
    ) -> str:
        """启动协作"""
        try:
            collaboration_id = str(uuid.uuid4())
            
            # 获取工作流定义
            workflow = self.workflow_definitions.get(workflow_type)
            if not workflow:
                raise ValueError(f"未知的工作流类型: {workflow_type}")
            
            # 创建协作会话
            collaboration = {
                "collaboration_id": collaboration_id,
                "workflow_type": workflow_type,
                "workflow": workflow,
                "context": context,
                "participants": participants or [],
                "status": "running",
                "current_step": 0,
                "step_results": {},
                "started_at": datetime.now(),
                "completed_at": None,
                "final_result": None
            }
            
            self.active_collaborations[collaboration_id] = collaboration
            
            # 保存状态
            await self.state_manager.save_workflow_state(collaboration_id, collaboration)
            
            # 启动执行
            asyncio.create_task(self._execute_collaboration(collaboration_id))
            
            logger.info(f"🚀 启动协作: {collaboration_id} - {workflow_type}")
            return collaboration_id
            
        except Exception as e:
            logger.error(f"❌ 启动协作失败: {e}")
            raise
    
    async def _execute_collaboration(self, collaboration_id: str):
        """执行协作"""
        try:
            collaboration = self.active_collaborations.get(collaboration_id)
            if not collaboration:
                raise ValueError(f"协作不存在: {collaboration_id}")
            
            workflow = collaboration["workflow"]
            steps = workflow["steps"]
            
            logger.info(f"🔄 开始执行协作: {collaboration_id}")
            
            # 逐步执行工作流
            for step_index, step in enumerate(steps):
                collaboration["current_step"] = step_index
                
                logger.info(f"📋 执行步骤 {step_index + 1}/{len(steps)}: {step['name']}")
                
                # 执行步骤
                step_result = await self._execute_step(collaboration, step)
                collaboration["step_results"][step["name"]] = step_result
                
                # 更新状态
                await self.state_manager.save_workflow_state(collaboration_id, collaboration)
                
                # 检查是否需要停止
                if step_result.get("status") == "failed":
                    collaboration["status"] = "failed"
                    break
            
            # 完成协作
            if collaboration["status"] == "running":
                collaboration["status"] = "completed"
                collaboration["final_result"] = await self._aggregate_results(collaboration)
            
            collaboration["completed_at"] = datetime.now()
            
            # 最终状态保存
            await self.state_manager.save_workflow_state(collaboration_id, collaboration)
            
            logger.info(f"✅ 协作完成: {collaboration_id} - {collaboration['status']}")
            
        except Exception as e:
            logger.error(f"❌ 执行协作失败: {collaboration_id} - {e}")
            if collaboration_id in self.active_collaborations:
                self.active_collaborations[collaboration_id]["status"] = "failed"
    
    async def _execute_step(self, collaboration: Dict[str, Any], step: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个步骤"""
        try:
            step_name = step["name"]
            agents = step["agents"]
            is_parallel = step.get("parallel", False)
            step_mode = step.get("mode", "normal")
            
            logger.info(f"🔧 执行步骤: {step_name} - {'并行' if is_parallel else '顺序'}")
            
            if step_mode == "debate":
                # 辩论模式
                return await self._execute_debate_step(collaboration, step)
            elif is_parallel:
                # 并行执行
                return await self._execute_parallel_step(collaboration, step)
            else:
                # 顺序执行
                return await self._execute_sequential_step(collaboration, step)
            
        except Exception as e:
            logger.error(f"❌ 执行步骤失败: {step.get('name', 'unknown')} - {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _execute_parallel_step(self, collaboration: Dict[str, Any], step: Dict[str, Any]) -> Dict[str, Any]:
        """并行执行步骤"""
        try:
            agents = step["agents"]
            context = collaboration["context"]
            
            # 创建并行任务
            tasks = []
            for agent_type in agents:
                task = self._create_agent_task(agent_type, context)
                tasks.append(task)
            
            # 等待所有任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            step_result = {
                "status": "completed",
                "agent_results": {},
                "errors": []
            }
            
            for i, result in enumerate(results):
                agent_type = agents[i]
                if isinstance(result, Exception):
                    step_result["errors"].append(f"{agent_type}: {str(result)}")
                else:
                    step_result["agent_results"][agent_type] = result
            
            # 如果有错误，标记为部分失败
            if step_result["errors"]:
                step_result["status"] = "partial_failure"
            
            return step_result
            
        except Exception as e:
            logger.error(f"❌ 并行执行失败: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _execute_sequential_step(self, collaboration: Dict[str, Any], step: Dict[str, Any]) -> Dict[str, Any]:
        """顺序执行步骤"""
        try:
            agents = step["agents"]
            context = collaboration["context"]
            
            step_result = {
                "status": "completed",
                "agent_results": {},
                "errors": []
            }
            
            # 顺序执行每个智能体
            for agent_type in agents:
                try:
                    result = await self._create_agent_task(agent_type, context)
                    step_result["agent_results"][agent_type] = result
                    
                    # 更新上下文（后续智能体可以使用前面的结果）
                    context[f"{agent_type}_result"] = result
                    
                except Exception as e:
                    error_msg = f"{agent_type}: {str(e)}"
                    step_result["errors"].append(error_msg)
                    logger.error(f"❌ 智能体执行失败: {error_msg}")
            
            # 如果有错误，标记为失败
            if step_result["errors"]:
                step_result["status"] = "failed"
            
            return step_result
            
        except Exception as e:
            logger.error(f"❌ 顺序执行失败: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _execute_debate_step(self, collaboration: Dict[str, Any], step: Dict[str, Any]) -> Dict[str, Any]:
        """执行辩论步骤"""
        try:
            # 这里应该调用辩论引擎
            # 暂时简化实现
            agents = step["agents"]
            context = collaboration["context"]
            
            step_result = {
                "status": "completed",
                "debate_result": {},
                "consensus": None
            }
            
            # 获取各方观点
            viewpoints = {}
            for agent_type in agents:
                result = await self._create_agent_task(agent_type, context)
                viewpoints[agent_type] = result
            
            step_result["debate_result"] = viewpoints
            
            # 简化的共识机制
            step_result["consensus"] = await self._simple_consensus(viewpoints)
            
            return step_result
            
        except Exception as e:
            logger.error(f"❌ 辩论执行失败: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _create_agent_task(self, agent_type: str, context: Dict[str, Any]):
        """创建智能体任务"""
        try:
            # 将字符串类型转换为AgentType枚举
            agent_type_mapping = {
                "fundamentals_analyst": "FUNDAMENTALS_ANALYST",
                "market_analyst": "MARKET_ANALYST",
                "news_analyst": "NEWS_ANALYST",
                "social_media_analyst": "SOCIAL_MEDIA_ANALYST",
                "bull_researcher": "BULL_RESEARCHER",
                "bear_researcher": "BEAR_RESEARCHER",
                "research_manager": "RESEARCH_MANAGER",
                "risk_manager": "RISK_MANAGER",
                "trader": "TRADER",
                "risky_debator": "RISKY_DEBATOR",
                "safe_debator": "SAFE_DEBATOR",
                "neutral_debator": "NEUTRAL_DEBATOR"
            }

            from ..agents.base_agent import AgentType, TaskContext

            # 获取对应的AgentType
            agent_type_enum_name = agent_type_mapping.get(agent_type)
            if not agent_type_enum_name:
                raise ValueError(f"未知的智能体类型: {agent_type}")

            agent_type_enum = getattr(AgentType, agent_type_enum_name)

            # 创建任务上下文
            task_context = TaskContext(
                task_id=f"collab_{agent_type}_{datetime.now().timestamp()}",
                symbol=context.get("symbol", "UNKNOWN"),
                company_name=context.get("company_name", "Unknown Company"),
                market=context.get("market", "US"),
                analysis_date=context.get("analysis_date", datetime.now().strftime("%Y-%m-%d")),
                parameters=context.get("parameters", {}),
                metadata={"collaboration": True, "agent_type": agent_type}
            )

            # 调用智能体管理器执行任务
            task_type = self._get_task_type_for_agent(agent_type)
            result = await self.agent_manager.execute_task(
                agent_type=agent_type_enum,
                task_type=task_type,
                context=task_context
            )

            return {
                "agent_type": agent_type,
                "agent_id": result.agent_id,
                "status": result.status,
                "result": result.result,
                "duration": result.duration,
                "timestamp": result.timestamp.isoformat()
            }

        except Exception as e:
            logger.error(f"❌ 创建智能体任务失败: {agent_type} - {e}")
            # 返回错误结果而不是抛出异常，以便协作可以继续
            return {
                "agent_type": agent_type,
                "status": "failed",
                "result": {},
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _get_task_type_for_agent(self, agent_type: str) -> str:
        """根据智能体类型获取任务类型"""
        task_mapping = {
            "fundamentals_analyst": "fundamentals_analysis",
            "market_analyst": "technical_analysis",
            "news_analyst": "news_analysis",
            "social_media_analyst": "sentiment_analysis",
            "bull_researcher": "bull_research",
            "bear_researcher": "bear_research",
            "research_manager": "research_management",
            "risk_manager": "risk_assessment",
            "trader": "trading_decision",
            "risky_debator": "debate_participation",
            "safe_debator": "debate_participation",
            "neutral_debator": "debate_participation"
        }
        return task_mapping.get(agent_type, "general_analysis")
    
    async def _simple_consensus(self, viewpoints: Dict[str, Any]) -> Dict[str, Any]:
        """简化的共识算法"""
        try:
            # 简单的投票机制
            recommendations = []
            for agent_id, result in viewpoints.items():
                if isinstance(result, dict) and "recommendation" in result:
                    recommendations.append(result["recommendation"])
                elif isinstance(result, dict) and "result" in result and isinstance(result["result"], dict):
                    # 从嵌套的result中提取recommendation
                    nested_result = result["result"]
                    if "recommendation" in nested_result:
                        recommendations.append(nested_result["recommendation"])
                    elif "investment_recommendation" in nested_result:
                        inv_rec = nested_result["investment_recommendation"]
                        if isinstance(inv_rec, dict) and "recommendation" in inv_rec:
                            recommendations.append(inv_rec["recommendation"])

            # 统计最多的建议
            if recommendations:
                consensus_recommendation = max(set(recommendations), key=recommendations.count)
                confidence = recommendations.count(consensus_recommendation) / len(recommendations)
            else:
                consensus_recommendation = "hold"
                confidence = 0.5

            return {
                "recommendation": consensus_recommendation,
                "confidence": confidence,
                "participating_agents": list(viewpoints.keys()),
                "vote_distribution": {rec: recommendations.count(rec) for rec in set(recommendations)}
            }

        except Exception as e:
            logger.error(f"❌ 共识算法失败: {e}")
            return {"recommendation": "hold", "confidence": 0.0}
    
    async def _aggregate_results(self, collaboration: Dict[str, Any]) -> Dict[str, Any]:
        """聚合最终结果"""
        try:
            step_results = collaboration["step_results"]
            
            final_result = {
                "collaboration_id": collaboration["collaboration_id"],
                "workflow_type": collaboration["workflow_type"],
                "status": collaboration["status"],
                "summary": {},
                "recommendations": [],
                "confidence_score": 0.0
            }
            
            # 聚合各步骤结果
            for step_name, step_result in step_results.items():
                if step_result.get("status") == "completed":
                    final_result["summary"][step_name] = step_result
                    
                    # 提取建议
                    if "consensus" in step_result:
                        consensus = step_result["consensus"]
                        if consensus and "recommendation" in consensus:
                            final_result["recommendations"].append(consensus["recommendation"])
            
            # 计算整体置信度
            if final_result["recommendations"]:
                final_result["confidence_score"] = 0.8  # 简化计算
            
            return final_result
            
        except Exception as e:
            logger.error(f"❌ 聚合结果失败: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def get_collaboration_status(self, collaboration_id: str) -> Optional[Dict[str, Any]]:
        """获取协作状态"""
        try:
            collaboration = self.active_collaborations.get(collaboration_id)
            if collaboration:
                return {
                    "collaboration_id": collaboration_id,
                    "status": collaboration["status"],
                    "current_step": collaboration["current_step"],
                    "progress": collaboration["current_step"] / len(collaboration["workflow"]["steps"]),
                    "started_at": collaboration["started_at"].isoformat(),
                    "completed_at": collaboration["completed_at"].isoformat() if collaboration["completed_at"] else None
                }
            
            # 从状态管理器获取
            return await self.state_manager.get_workflow_state(collaboration_id)
            
        except Exception as e:
            logger.error(f"❌ 获取协作状态失败: {collaboration_id} - {e}")
            return None
    
    async def cancel_collaboration(self, collaboration_id: str) -> bool:
        """取消协作"""
        try:
            if collaboration_id in self.active_collaborations:
                self.active_collaborations[collaboration_id]["status"] = "cancelled"
                await self.state_manager.save_workflow_state(
                    collaboration_id, 
                    self.active_collaborations[collaboration_id]
                )
                logger.info(f"🚫 取消协作: {collaboration_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ 取消协作失败: {collaboration_id} - {e}")
            return False
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 检查依赖组件
            if not await self.agent_manager.health_check():
                return False
            
            if not await self.state_manager.health_check():
                return False
            
            if not await self.message_router.health_check():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 协作引擎健康检查失败: {e}")
            return False
    
    async def cleanup(self):
        """清理资源"""
        try:
            # 取消所有活跃的协作
            for collaboration_id in list(self.active_collaborations.keys()):
                await self.cancel_collaboration(collaboration_id)
            
            self.active_collaborations.clear()
            
            logger.info("✅ 协作引擎清理完成")
            
        except Exception as e:
            logger.error(f"❌ 协作引擎清理失败: {e}")
