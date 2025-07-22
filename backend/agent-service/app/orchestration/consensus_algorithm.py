"""
共识算法
负责智能体间的共识达成和决策整合
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import statistics

from backend.shared.logging_config import get_logger

logger = get_logger("agent-service.consensus_algorithm")


class ConsensusMethod(Enum):
    """共识方法枚举"""
    MAJORITY_VOTE = "majority_vote"          # 多数投票
    WEIGHTED_VOTE = "weighted_vote"          # 加权投票
    CONFIDENCE_WEIGHTED = "confidence_weighted"  # 置信度加权
    EXPERT_PRIORITY = "expert_priority"      # 专家优先
    HYBRID = "hybrid"                        # 混合方法


class ConsensusAlgorithm:
    """共识算法"""
    
    def __init__(self, agent_manager, state_manager):
        self.agent_manager = agent_manager
        self.state_manager = state_manager
        
        # 智能体权重配置
        self.agent_weights = {
            "fundamentals_analyst": 1.2,
            "market_analyst": 1.1,
            "news_analyst": 0.9,
            "social_media_analyst": 0.7,
            "bull_researcher": 1.0,
            "bear_researcher": 1.0,
            "research_manager": 1.5,
            "risk_manager": 1.3,
            "trader": 1.0
        }
        
        # 共识阈值
        self.consensus_thresholds = {
            "strong_consensus": 0.8,
            "moderate_consensus": 0.6,
            "weak_consensus": 0.4
        }
        
        logger.info("🏗️ 共识算法初始化")
    
    async def initialize(self):
        """初始化共识算法"""
        try:
            logger.info("✅ 共识算法初始化完成")
        except Exception as e:
            logger.error(f"❌ 共识算法初始化失败: {e}")
            raise
    
    async def reach_consensus(
        self,
        agent_results: Dict[str, Any],
        method: ConsensusMethod = ConsensusMethod.HYBRID,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """达成共识"""
        try:
            logger.info(f"🤝 开始共识算法: {method.value} - {len(agent_results)}个结果")
            
            if not agent_results:
                return self._create_empty_consensus()
            
            # 预处理结果
            processed_results = await self._preprocess_results(agent_results)
            
            # 根据方法选择共识算法
            if method == ConsensusMethod.MAJORITY_VOTE:
                consensus = await self._majority_vote_consensus(processed_results)
            elif method == ConsensusMethod.WEIGHTED_VOTE:
                consensus = await self._weighted_vote_consensus(processed_results)
            elif method == ConsensusMethod.CONFIDENCE_WEIGHTED:
                consensus = await self._confidence_weighted_consensus(processed_results)
            elif method == ConsensusMethod.EXPERT_PRIORITY:
                consensus = await self._expert_priority_consensus(processed_results)
            else:  # HYBRID
                consensus = await self._hybrid_consensus(processed_results)
            
            # 后处理和验证
            final_consensus = await self._postprocess_consensus(consensus, processed_results, context)
            
            logger.info(f"✅ 共识达成: {final_consensus.get('recommendation', 'unknown')}")
            return final_consensus
            
        except Exception as e:
            logger.error(f"❌ 共识算法失败: {e}")
            return self._create_error_consensus(str(e))
    
    async def _preprocess_results(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """预处理智能体结果"""
        try:
            processed = {}
            
            for agent_id, result in agent_results.items():
                if not result or result.get("status") != "success":
                    continue
                
                # 提取关键信息
                agent_data = result.get("result", {})
                
                processed_result = {
                    "agent_id": agent_id,
                    "agent_type": result.get("agent_type", "unknown"),
                    "recommendation": self._extract_recommendation(agent_data),
                    "confidence": self._extract_confidence(agent_data),
                    "reasoning": self._extract_reasoning(agent_data),
                    "risk_level": self._extract_risk_level(agent_data),
                    "key_factors": self._extract_key_factors(agent_data),
                    "timestamp": result.get("timestamp", datetime.now().isoformat())
                }
                
                processed[agent_id] = processed_result
            
            logger.debug(f"📋 预处理完成: {len(processed)}个有效结果")
            return processed
            
        except Exception as e:
            logger.error(f"❌ 预处理结果失败: {e}")
            return {}
    
    def _extract_recommendation(self, agent_data: Dict[str, Any]) -> str:
        """提取投资建议"""
        # 尝试多种可能的字段名
        for field in ["recommendation", "investment_recommendation", "trading_signal", "decision"]:
            if field in agent_data:
                rec_data = agent_data[field]
                if isinstance(rec_data, dict):
                    return rec_data.get("recommendation", "hold")
                elif isinstance(rec_data, str):
                    return rec_data
        
        # 从分析报告中推断
        report = agent_data.get("analysis_report", "")
        if "买入" in report or "buy" in report.lower():
            return "buy"
        elif "卖出" in report or "sell" in report.lower():
            return "sell"
        
        return "hold"
    
    def _extract_confidence(self, agent_data: Dict[str, Any]) -> float:
        """提取置信度"""
        # 尝试多种可能的字段名
        for field in ["confidence_score", "confidence", "certainty"]:
            if field in agent_data:
                confidence = agent_data[field]
                if isinstance(confidence, (int, float)):
                    return max(0.0, min(1.0, float(confidence)))
        
        # 从投资建议中提取
        rec_data = agent_data.get("investment_recommendation", {})
        if isinstance(rec_data, dict):
            confidence = rec_data.get("confidence", 0.5)
            if isinstance(confidence, str):
                confidence_map = {"高": 0.8, "中": 0.6, "低": 0.4}
                return confidence_map.get(confidence, 0.5)
            return float(confidence) if isinstance(confidence, (int, float)) else 0.5
        
        return 0.5
    
    def _extract_reasoning(self, agent_data: Dict[str, Any]) -> str:
        """提取推理过程"""
        for field in ["reasoning", "analysis_report", "summary", "conclusion"]:
            if field in agent_data:
                reasoning = agent_data[field]
                if isinstance(reasoning, str):
                    return reasoning
                elif isinstance(reasoning, dict):
                    return reasoning.get("reasoning", "")
        
        return "无推理信息"
    
    def _extract_risk_level(self, agent_data: Dict[str, Any]) -> str:
        """提取风险水平"""
        for field in ["risk_level", "risk_assessment", "risk"]:
            if field in agent_data:
                risk = agent_data[field]
                if isinstance(risk, str):
                    return risk
                elif isinstance(risk, dict):
                    return risk.get("level", "medium")
        
        return "medium"
    
    def _extract_key_factors(self, agent_data: Dict[str, Any]) -> List[str]:
        """提取关键因素"""
        factors = []
        
        for field in ["key_factors", "factors", "highlights", "strengths", "risks"]:
            if field in agent_data:
                data = agent_data[field]
                if isinstance(data, list):
                    factors.extend([str(item) for item in data])
                elif isinstance(data, str):
                    factors.append(data)
        
        return factors[:5]  # 限制数量
    
    async def _majority_vote_consensus(self, processed_results: Dict[str, Any]) -> Dict[str, Any]:
        """多数投票共识"""
        try:
            recommendations = [result["recommendation"] for result in processed_results.values()]
            
            if not recommendations:
                return self._create_empty_consensus()
            
            # 统计投票
            vote_counts = {}
            for rec in recommendations:
                vote_counts[rec] = vote_counts.get(rec, 0) + 1
            
            # 找出最多票数的建议
            max_votes = max(vote_counts.values())
            winners = [rec for rec, votes in vote_counts.items() if votes == max_votes]
            
            # 如果有平票，选择更保守的选项
            if len(winners) > 1:
                priority = ["sell", "hold", "buy"]
                for option in priority:
                    if option in winners:
                        final_recommendation = option
                        break
                else:
                    final_recommendation = winners[0]
            else:
                final_recommendation = winners[0]
            
            # 计算共识强度
            consensus_strength = max_votes / len(recommendations)
            
            return {
                "method": "majority_vote",
                "recommendation": final_recommendation,
                "consensus_strength": consensus_strength,
                "vote_distribution": vote_counts,
                "total_votes": len(recommendations)
            }
            
        except Exception as e:
            logger.error(f"❌ 多数投票共识失败: {e}")
            return self._create_error_consensus(str(e))
    
    async def _weighted_vote_consensus(self, processed_results: Dict[str, Any]) -> Dict[str, Any]:
        """加权投票共识"""
        try:
            weighted_votes = {}
            total_weight = 0
            
            for result in processed_results.values():
                agent_type = result["agent_type"]
                recommendation = result["recommendation"]
                weight = self.agent_weights.get(agent_type, 1.0)
                
                weighted_votes[recommendation] = weighted_votes.get(recommendation, 0) + weight
                total_weight += weight
            
            if total_weight == 0:
                return self._create_empty_consensus()
            
            # 找出加权得分最高的建议
            max_weight = max(weighted_votes.values())
            final_recommendation = max(weighted_votes, key=weighted_votes.get)
            
            # 计算共识强度
            consensus_strength = max_weight / total_weight
            
            return {
                "method": "weighted_vote",
                "recommendation": final_recommendation,
                "consensus_strength": consensus_strength,
                "weighted_distribution": weighted_votes,
                "total_weight": total_weight
            }
            
        except Exception as e:
            logger.error(f"❌ 加权投票共识失败: {e}")
            return self._create_error_consensus(str(e))
    
    async def _confidence_weighted_consensus(self, processed_results: Dict[str, Any]) -> Dict[str, Any]:
        """置信度加权共识"""
        try:
            confidence_weighted_votes = {}
            total_confidence = 0
            
            for result in processed_results.values():
                recommendation = result["recommendation"]
                confidence = result["confidence"]
                
                confidence_weighted_votes[recommendation] = confidence_weighted_votes.get(recommendation, 0) + confidence
                total_confidence += confidence
            
            if total_confidence == 0:
                return self._create_empty_consensus()
            
            # 找出置信度加权得分最高的建议
            max_confidence = max(confidence_weighted_votes.values())
            final_recommendation = max(confidence_weighted_votes, key=confidence_weighted_votes.get)
            
            # 计算共识强度
            consensus_strength = max_confidence / total_confidence
            
            # 计算平均置信度
            avg_confidence = total_confidence / len(processed_results)
            
            return {
                "method": "confidence_weighted",
                "recommendation": final_recommendation,
                "consensus_strength": consensus_strength,
                "average_confidence": avg_confidence,
                "confidence_distribution": confidence_weighted_votes
            }
            
        except Exception as e:
            logger.error(f"❌ 置信度加权共识失败: {e}")
            return self._create_error_consensus(str(e))
    
    async def _expert_priority_consensus(self, processed_results: Dict[str, Any]) -> Dict[str, Any]:
        """专家优先共识"""
        try:
            # 定义专家优先级
            expert_priority = {
                "research_manager": 1,
                "risk_manager": 2,
                "fundamentals_analyst": 3,
                "market_analyst": 4,
                "trader": 5
            }
            
            # 按优先级排序
            sorted_results = []
            for result in processed_results.values():
                agent_type = result["agent_type"]
                priority = expert_priority.get(agent_type, 999)
                sorted_results.append((priority, result))
            
            sorted_results.sort(key=lambda x: x[0])
            
            if not sorted_results:
                return self._create_empty_consensus()
            
            # 使用最高优先级专家的建议
            top_expert_result = sorted_results[0][1]
            final_recommendation = top_expert_result["recommendation"]
            
            # 计算支持度（其他专家的一致性）
            support_count = sum(1 for _, result in sorted_results[1:] 
                              if result["recommendation"] == final_recommendation)
            support_ratio = support_count / max(1, len(sorted_results) - 1)
            
            return {
                "method": "expert_priority",
                "recommendation": final_recommendation,
                "consensus_strength": top_expert_result["confidence"],
                "expert_support_ratio": support_ratio,
                "top_expert": top_expert_result["agent_type"],
                "expert_confidence": top_expert_result["confidence"]
            }
            
        except Exception as e:
            logger.error(f"❌ 专家优先共识失败: {e}")
            return self._create_error_consensus(str(e))
    
    async def _hybrid_consensus(self, processed_results: Dict[str, Any]) -> Dict[str, Any]:
        """混合共识算法"""
        try:
            # 运行多种共识算法
            majority_result = await self._majority_vote_consensus(processed_results)
            weighted_result = await self._weighted_vote_consensus(processed_results)
            confidence_result = await self._confidence_weighted_consensus(processed_results)
            expert_result = await self._expert_priority_consensus(processed_results)
            
            # 收集所有建议
            all_recommendations = [
                majority_result.get("recommendation"),
                weighted_result.get("recommendation"),
                confidence_result.get("recommendation"),
                expert_result.get("recommendation")
            ]
            
            # 统计一致性
            rec_counts = {}
            for rec in all_recommendations:
                if rec:
                    rec_counts[rec] = rec_counts.get(rec, 0) + 1
            
            if not rec_counts:
                return self._create_empty_consensus()
            
            # 选择最一致的建议
            max_count = max(rec_counts.values())
            final_recommendation = max(rec_counts, key=rec_counts.get)
            
            # 计算综合置信度
            method_weights = {
                "majority": 0.2,
                "weighted": 0.3,
                "confidence": 0.3,
                "expert": 0.2
            }
            
            weighted_confidence = (
                majority_result.get("consensus_strength", 0) * method_weights["majority"] +
                weighted_result.get("consensus_strength", 0) * method_weights["weighted"] +
                confidence_result.get("consensus_strength", 0) * method_weights["confidence"] +
                expert_result.get("consensus_strength", 0) * method_weights["expert"]
            )
            
            return {
                "method": "hybrid",
                "recommendation": final_recommendation,
                "consensus_strength": weighted_confidence,
                "method_agreement": max_count / 4,
                "individual_results": {
                    "majority_vote": majority_result,
                    "weighted_vote": weighted_result,
                    "confidence_weighted": confidence_result,
                    "expert_priority": expert_result
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 混合共识失败: {e}")
            return self._create_error_consensus(str(e))
    
    async def _postprocess_consensus(
        self, 
        consensus: Dict[str, Any], 
        processed_results: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """后处理共识结果"""
        try:
            # 添加元数据
            consensus.update({
                "consensus_id": f"consensus_{datetime.now().timestamp()}",
                "timestamp": datetime.now().isoformat(),
                "participating_agents": list(processed_results.keys()),
                "total_participants": len(processed_results),
                "context": context or {}
            })
            
            # 分类共识强度
            strength = consensus.get("consensus_strength", 0)
            if strength >= self.consensus_thresholds["strong_consensus"]:
                consensus["consensus_level"] = "strong"
            elif strength >= self.consensus_thresholds["moderate_consensus"]:
                consensus["consensus_level"] = "moderate"
            elif strength >= self.consensus_thresholds["weak_consensus"]:
                consensus["consensus_level"] = "weak"
            else:
                consensus["consensus_level"] = "no_consensus"
            
            # 添加风险评估
            consensus["risk_assessment"] = await self._assess_consensus_risk(processed_results)
            
            # 添加关键因素汇总
            consensus["key_factors"] = await self._aggregate_key_factors(processed_results)
            
            return consensus
            
        except Exception as e:
            logger.error(f"❌ 后处理共识失败: {e}")
            return consensus
    
    async def _assess_consensus_risk(self, processed_results: Dict[str, Any]) -> Dict[str, Any]:
        """评估共识风险"""
        try:
            risk_levels = [result["risk_level"] for result in processed_results.values()]
            
            # 统计风险分布
            risk_counts = {}
            for risk in risk_levels:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
            
            # 计算平均风险
            risk_scores = {"low": 1, "medium": 2, "high": 3}
            total_score = sum(risk_scores.get(risk, 2) for risk in risk_levels)
            avg_risk_score = total_score / len(risk_levels) if risk_levels else 2
            
            if avg_risk_score <= 1.5:
                overall_risk = "low"
            elif avg_risk_score <= 2.5:
                overall_risk = "medium"
            else:
                overall_risk = "high"
            
            return {
                "overall_risk": overall_risk,
                "risk_distribution": risk_counts,
                "average_risk_score": avg_risk_score
            }
            
        except Exception as e:
            logger.error(f"❌ 评估共识风险失败: {e}")
            return {"overall_risk": "medium", "error": str(e)}
    
    async def _aggregate_key_factors(self, processed_results: Dict[str, Any]) -> List[str]:
        """聚合关键因素"""
        try:
            all_factors = []
            for result in processed_results.values():
                all_factors.extend(result.get("key_factors", []))
            
            # 统计因素频次
            factor_counts = {}
            for factor in all_factors:
                factor_counts[factor] = factor_counts.get(factor, 0) + 1
            
            # 返回最常提及的因素
            sorted_factors = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)
            return [factor for factor, count in sorted_factors[:10]]
            
        except Exception as e:
            logger.error(f"❌ 聚合关键因素失败: {e}")
            return []
    
    def _create_empty_consensus(self) -> Dict[str, Any]:
        """创建空共识"""
        return {
            "method": "none",
            "recommendation": "hold",
            "consensus_strength": 0.0,
            "consensus_level": "no_consensus",
            "message": "无有效结果进行共识"
        }
    
    def _create_error_consensus(self, error: str) -> Dict[str, Any]:
        """创建错误共识"""
        return {
            "method": "error",
            "recommendation": "hold",
            "consensus_strength": 0.0,
            "consensus_level": "no_consensus",
            "error": error,
            "message": "共识算法执行失败"
        }
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            return True
        except Exception as e:
            logger.error(f"❌ 共识算法健康检查失败: {e}")
            return False
    
    async def cleanup(self):
        """清理资源"""
        try:
            logger.info("✅ 共识算法清理完成")
        except Exception as e:
            logger.error(f"❌ 共识算法清理失败: {e}")
