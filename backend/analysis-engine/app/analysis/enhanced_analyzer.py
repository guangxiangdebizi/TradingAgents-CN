"""
增强分析器
集成Agent Service的多智能体分析能力
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from backend.shared.utils.logger import get_service_logger
from backend.shared.models.analysis import AnalysisRequest, AnalysisResult, AnalysisStatus
from ..integrations.agent_service_client import get_agent_service_client
from .independent_analyzer import IndependentAnalyzer

logger = get_service_logger("analysis-engine.enhanced_analyzer")


class EnhancedAnalyzer:
    """增强分析器 - 集成Agent Service的多智能体分析"""
    
    def __init__(self):
        self.independent_analyzer = IndependentAnalyzer()
        self.agent_client = None
        
        logger.info("🚀 增强分析器初始化")
    
    async def initialize(self):
        """初始化分析器"""
        try:
            # 获取Agent Service客户端
            self.agent_client = await get_agent_service_client()
            
            # 检查Agent Service健康状态
            if await self.agent_client.health_check():
                logger.info("✅ Agent Service连接正常")
            else:
                logger.warning("⚠️ Agent Service连接异常，将使用独立分析器")
                self.agent_client = None
            
        except Exception as e:
            logger.error(f"❌ 初始化Agent Service客户端失败: {e}")
            self.agent_client = None
    
    async def analyze_stock(
        self,
        request: AnalysisRequest,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """分析股票 - 智能选择分析方式"""
        try:
            # 根据请求参数决定分析策略
            analysis_strategy = self._determine_analysis_strategy(request)
            
            logger.info(f"📊 开始{analysis_strategy}分析: {request.stock_code}")
            
            if analysis_strategy == "multi_agent" and self.agent_client:
                return await self._multi_agent_analysis(request, progress_callback)
            elif analysis_strategy == "debate" and self.agent_client:
                return await self._debate_analysis(request, progress_callback)
            elif analysis_strategy == "workflow" and self.agent_client:
                return await self._workflow_analysis(request, progress_callback)
            else:
                # 回退到独立分析
                logger.info("📋 使用独立分析器")
                return await self._independent_analysis(request, progress_callback)
                
        except Exception as e:
            logger.error(f"❌ 股票分析失败: {e}")
            # 回退到独立分析
            return await self._independent_analysis(request, progress_callback)
    
    def _determine_analysis_strategy(self, request: AnalysisRequest) -> str:
        """确定分析策略"""
        # 根据分析师选择和研究深度确定策略
        selected_analysts = sum([
            request.market_analyst,
            request.social_analyst,
            request.news_analyst,
            request.fundamental_analyst
        ])
        
        if request.research_depth >= 4 and selected_analysts >= 3:
            return "workflow"  # 使用工作流进行深度分析
        elif request.research_depth >= 3 and selected_analysts >= 2:
            return "multi_agent"  # 使用多智能体协作
        elif selected_analysts >= 2:
            return "debate"  # 使用辩论模式
        else:
            return "independent"  # 使用独立分析
    
    async def _workflow_analysis(
        self,
        request: AnalysisRequest,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """工作流分析"""
        try:
            if progress_callback:
                await progress_callback(10, "启动工作流分析", "准备多智能体协作")
            
            # 启动综合分析工作流
            execution_id = await self.agent_client.start_comprehensive_analysis(
                stock_code=request.stock_code,
                company_name=request.stock_code,  # 简化处理
                market=self._get_market_code(request.market_type),
                analysis_date=request.analysis_date.strftime("%Y-%m-%d")
            )
            
            if not execution_id:
                raise Exception("启动工作流失败")
            
            if progress_callback:
                await progress_callback(30, "工作流执行中", f"执行ID: {execution_id}")
            
            # 等待工作流完成
            result = await self.agent_client.wait_for_completion(
                execution_id, max_wait_time=300, poll_interval=10
            )
            
            if not result:
                raise Exception("工作流执行超时或失败")
            
            if progress_callback:
                await progress_callback(90, "处理分析结果", "聚合多智能体分析结果")
            
            # 转换结果格式
            return self._convert_workflow_result(result, request)
            
        except Exception as e:
            logger.error(f"❌ 工作流分析失败: {e}")
            raise
    
    async def _multi_agent_analysis(
        self,
        request: AnalysisRequest,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """多智能体协作分析"""
        try:
            if progress_callback:
                await progress_callback(10, "启动多智能体分析", "准备智能体协作")
            
            # 启动快速分析工作流
            execution_id = await self.agent_client.start_quick_analysis(
                stock_code=request.stock_code,
                company_name=request.stock_code,
                market=self._get_market_code(request.market_type),
                analysis_date=request.analysis_date.strftime("%Y-%m-%d")
            )
            
            if not execution_id:
                raise Exception("启动多智能体分析失败")
            
            if progress_callback:
                await progress_callback(40, "智能体协作中", f"执行ID: {execution_id}")
            
            # 等待完成
            result = await self.agent_client.wait_for_completion(
                execution_id, max_wait_time=180, poll_interval=5
            )
            
            if not result:
                raise Exception("多智能体分析超时或失败")
            
            if progress_callback:
                await progress_callback(90, "处理分析结果", "聚合智能体分析结果")
            
            return self._convert_workflow_result(result, request)
            
        except Exception as e:
            logger.error(f"❌ 多智能体分析失败: {e}")
            raise
    
    async def _debate_analysis(
        self,
        request: AnalysisRequest,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """辩论分析"""
        try:
            if progress_callback:
                await progress_callback(10, "启动辩论分析", "准备智能体辩论")
            
            # 启动辩论
            debate_id = await self.agent_client.start_debate_analysis(
                stock_code=request.stock_code,
                company_name=request.stock_code,
                topic=f"{request.stock_code} 投资决策辩论"
            )
            
            if not debate_id:
                raise Exception("启动辩论失败")
            
            if progress_callback:
                await progress_callback(40, "智能体辩论中", f"辩论ID: {debate_id}")
            
            # 等待辩论完成
            max_wait = 120
            poll_interval = 5
            start_time = asyncio.get_event_loop().time()
            
            while True:
                if asyncio.get_event_loop().time() - start_time > max_wait:
                    raise Exception("辩论超时")
                
                status = await self.agent_client.get_debate_status(debate_id)
                if not status:
                    raise Exception("获取辩论状态失败")
                
                debate_status = status.get("status", "unknown")
                if debate_status == "completed":
                    break
                elif debate_status == "failed":
                    raise Exception("辩论失败")
                
                await asyncio.sleep(poll_interval)
            
            if progress_callback:
                await progress_callback(90, "处理辩论结果", "聚合辩论结论")
            
            return self._convert_debate_result(status, request)
            
        except Exception as e:
            logger.error(f"❌ 辩论分析失败: {e}")
            raise
    
    async def _independent_analysis(
        self,
        request: AnalysisRequest,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """独立分析 - 回退方案"""
        try:
            if progress_callback:
                await progress_callback(10, "启动独立分析", "使用传统分析方法")
            
            # 使用原有的独立分析器
            trade_date = request.analysis_date.strftime("%Y-%m-%d") if request.analysis_date else None
            result = await self.independent_analyzer.analyze_stock(
                request.stock_code,
                trade_date
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 独立分析失败: {e}")
            raise
    
    def _get_market_code(self, market_type) -> str:
        """获取市场代码"""
        market_mapping = {
            "A股": "CN",
            "美股": "US", 
            "港股": "HK"
        }
        return market_mapping.get(market_type, "CN")
    
    def _convert_workflow_result(self, workflow_result: Dict[str, Any], request: AnalysisRequest) -> Dict[str, Any]:
        """转换工作流结果"""
        try:
            final_result = workflow_result.get("final_result", {})
            
            # 提取关键信息
            if isinstance(final_result, dict):
                workflow_consensus = final_result.get("workflow_consensus", {})
                recommendation = workflow_consensus.get("recommendation", "持有")
                confidence = workflow_consensus.get("consensus_strength", 0.5)
                
                # 构建分析结果
                analysis_result = {
                    "success": True,
                    "analysis_type": "multi_agent_workflow",
                    "stock_code": request.stock_code,
                    "recommendation": recommendation,
                    "confidence": f"{confidence * 100:.1f}%",
                    "risk_score": f"{(1 - confidence) * 100:.1f}%",
                    "reasoning": self._extract_reasoning(final_result),
                    "technical_analysis": json.dumps(final_result, ensure_ascii=False, indent=2),
                    "agent_results": final_result.get("step_results", {}),
                    "execution_summary": final_result.get("execution_summary", {}),
                    "timestamp": datetime.now().isoformat()
                }
                
                return analysis_result
            else:
                # 简化结果
                return {
                    "success": True,
                    "analysis_type": "multi_agent_workflow",
                    "stock_code": request.stock_code,
                    "recommendation": "持有",
                    "confidence": "50.0%",
                    "risk_score": "50.0%",
                    "reasoning": "多智能体工作流分析完成",
                    "technical_analysis": json.dumps(workflow_result, ensure_ascii=False, indent=2),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ 转换工作流结果失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_type": "multi_agent_workflow",
                "stock_code": request.stock_code
            }
    
    def _convert_debate_result(self, debate_result: Dict[str, Any], request: AnalysisRequest) -> Dict[str, Any]:
        """转换辩论结果"""
        try:
            consensus = debate_result.get("consensus", {})
            final_decision = debate_result.get("final_decision", {})
            
            recommendation = consensus.get("recommendation", "持有")
            confidence = consensus.get("confidence", 0.5)
            
            analysis_result = {
                "success": True,
                "analysis_type": "agent_debate",
                "stock_code": request.stock_code,
                "recommendation": recommendation,
                "confidence": f"{confidence * 100:.1f}%",
                "risk_score": f"{(1 - confidence) * 100:.1f}%",
                "reasoning": self._extract_debate_reasoning(debate_result),
                "technical_analysis": json.dumps(debate_result, ensure_ascii=False, indent=2),
                "debate_rounds": debate_result.get("rounds", []),
                "participants": debate_result.get("participants", []),
                "timestamp": datetime.now().isoformat()
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ 转换辩论结果失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis_type": "agent_debate",
                "stock_code": request.stock_code
            }
    
    def _extract_reasoning(self, result: Dict[str, Any]) -> str:
        """提取推理过程"""
        try:
            reasoning_parts = []
            
            # 从工作流共识中提取
            workflow_consensus = result.get("workflow_consensus", {})
            if "key_factors" in workflow_consensus:
                key_factors = workflow_consensus["key_factors"]
                if key_factors:
                    reasoning_parts.append(f"关键因素: {', '.join(key_factors[:3])}")
            
            # 从执行摘要中提取
            execution_summary = result.get("execution_summary", {})
            if execution_summary:
                completed_steps = execution_summary.get("completed_steps", 0)
                total_steps = execution_summary.get("total_steps", 0)
                reasoning_parts.append(f"完成{completed_steps}/{total_steps}个分析步骤")
            
            if reasoning_parts:
                return "; ".join(reasoning_parts)
            else:
                return "多智能体协作分析完成，综合多个专业视角得出结论"
                
        except Exception as e:
            logger.error(f"❌ 提取推理过程失败: {e}")
            return "多智能体分析完成"
    
    def _extract_debate_reasoning(self, result: Dict[str, Any]) -> str:
        """提取辩论推理过程"""
        try:
            reasoning_parts = []
            
            # 从共识中提取
            consensus = result.get("consensus", {})
            if "reasoning" in consensus:
                reasoning_parts.append(consensus["reasoning"])
            
            # 从辩论轮次中提取
            rounds = result.get("rounds", [])
            if rounds:
                reasoning_parts.append(f"经过{len(rounds)}轮辩论")
            
            # 从参与者中提取
            participants = result.get("participants", [])
            if participants:
                reasoning_parts.append(f"参与者: {', '.join(participants)}")
            
            if reasoning_parts:
                return "; ".join(reasoning_parts)
            else:
                return "智能体辩论分析完成，通过多方观点碰撞得出结论"
                
        except Exception as e:
            logger.error(f"❌ 提取辩论推理失败: {e}")
            return "智能体辩论分析完成"
    
    async def get_analysis_capabilities(self) -> Dict[str, Any]:
        """获取分析能力"""
        capabilities = {
            "independent_analysis": True,
            "multi_agent_analysis": False,
            "workflow_analysis": False,
            "debate_analysis": False,
            "agent_service_available": False
        }
        
        if self.agent_client:
            try:
                if await self.agent_client.health_check():
                    capabilities.update({
                        "multi_agent_analysis": True,
                        "workflow_analysis": True,
                        "debate_analysis": True,
                        "agent_service_available": True
                    })
            except Exception as e:
                logger.error(f"❌ 检查Agent Service能力失败: {e}")
        
        return capabilities
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.agent_client:
                await self.agent_client.disconnect()
            logger.info("✅ 增强分析器清理完成")
        except Exception as e:
            logger.error(f"❌ 增强分析器清理失败: {e}")
