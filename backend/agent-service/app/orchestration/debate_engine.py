"""
辩论引擎
负责智能体间的辩论协调和观点整合
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from backend.shared.logging_config import get_logger

logger = get_logger("agent-service.debate_engine")


class DebateStatus(Enum):
    """辩论状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DebateEngine:
    """辩论引擎"""
    
    def __init__(self, agent_manager, state_manager, message_router):
        self.agent_manager = agent_manager
        self.state_manager = state_manager
        self.message_router = message_router
        
        # 活跃的辩论
        self.active_debates: Dict[str, Dict[str, Any]] = {}
        
        # 辩论规则
        self.debate_rules = {
            "max_rounds": 3,
            "round_timeout": 120,  # 秒
            "min_participants": 2,
            "max_participants": 5
        }
        
        logger.info("🏗️ 辩论引擎初始化")
    
    async def initialize(self):
        """初始化辩论引擎"""
        try:
            logger.info("✅ 辩论引擎初始化完成")
        except Exception as e:
            logger.error(f"❌ 辩论引擎初始化失败: {e}")
            raise
    
    async def start_debate(
        self,
        topic: str,
        participants: List[str],
        context: Dict[str, Any],
        rules: Optional[Dict[str, Any]] = None
    ) -> str:
        """启动辩论"""
        try:
            debate_id = str(uuid.uuid4())
            
            # 验证参与者
            if len(participants) < self.debate_rules["min_participants"]:
                raise ValueError(f"参与者数量不足，最少需要{self.debate_rules['min_participants']}个")
            
            if len(participants) > self.debate_rules["max_participants"]:
                raise ValueError(f"参与者数量过多，最多允许{self.debate_rules['max_participants']}个")
            
            # 合并规则
            effective_rules = {**self.debate_rules, **(rules or {})}
            
            # 创建辩论会话
            debate = {
                "debate_id": debate_id,
                "topic": topic,
                "participants": participants,
                "context": context,
                "rules": effective_rules,
                "status": DebateStatus.PENDING,
                "current_round": 0,
                "rounds": [],
                "positions": {},  # 参与者立场
                "arguments": {},  # 参与者论点
                "consensus": None,
                "started_at": datetime.now(),
                "completed_at": None
            }
            
            self.active_debates[debate_id] = debate
            
            # 保存状态
            await self.state_manager.save_workflow_state(f"debate_{debate_id}", debate)
            
            # 启动辩论执行
            asyncio.create_task(self._execute_debate(debate_id))
            
            logger.info(f"🗣️ 启动辩论: {debate_id} - {topic}")
            return debate_id
            
        except Exception as e:
            logger.error(f"❌ 启动辩论失败: {e}")
            raise
    
    async def _execute_debate(self, debate_id: str):
        """执行辩论"""
        try:
            debate = self.active_debates.get(debate_id)
            if not debate:
                raise ValueError(f"辩论不存在: {debate_id}")
            
            debate["status"] = DebateStatus.RUNNING
            
            logger.info(f"🔄 开始执行辩论: {debate_id}")
            
            # 第一轮：收集初始立场
            await self._collect_initial_positions(debate)
            
            # 多轮辩论
            max_rounds = debate["rules"]["max_rounds"]
            for round_num in range(1, max_rounds + 1):
                debate["current_round"] = round_num
                
                logger.info(f"🗣️ 辩论第{round_num}轮开始")
                
                round_result = await self._execute_debate_round(debate, round_num)
                debate["rounds"].append(round_result)
                
                # 检查是否达成共识
                if await self._check_consensus(debate):
                    logger.info(f"🤝 辩论达成共识，提前结束")
                    break
                
                # 更新状态
                await self.state_manager.save_workflow_state(f"debate_{debate_id}", debate)
            
            # 生成最终共识
            debate["consensus"] = await self._generate_final_consensus(debate)
            debate["status"] = DebateStatus.COMPLETED
            debate["completed_at"] = datetime.now()
            
            # 最终状态保存
            await self.state_manager.save_workflow_state(f"debate_{debate_id}", debate)
            
            logger.info(f"✅ 辩论完成: {debate_id}")
            
        except Exception as e:
            logger.error(f"❌ 执行辩论失败: {debate_id} - {e}")
            if debate_id in self.active_debates:
                self.active_debates[debate_id]["status"] = DebateStatus.FAILED
    
    async def _collect_initial_positions(self, debate: Dict[str, Any]):
        """收集初始立场"""
        try:
            participants = debate["participants"]
            context = debate["context"]
            topic = debate["topic"]
            
            logger.info(f"📋 收集初始立场: {len(participants)}个参与者")
            
            # 并行收集各参与者的初始立场
            tasks = []
            for participant in participants:
                task = self._get_participant_position(participant, topic, context)
                tasks.append(task)
            
            positions = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            for i, position in enumerate(positions):
                participant = participants[i]
                if isinstance(position, Exception):
                    logger.error(f"❌ 获取{participant}立场失败: {position}")
                    debate["positions"][participant] = {
                        "stance": "neutral",
                        "confidence": 0.0,
                        "reasoning": f"获取立场失败: {str(position)}"
                    }
                else:
                    debate["positions"][participant] = position
            
        except Exception as e:
            logger.error(f"❌ 收集初始立场失败: {e}")
            raise
    
    async def _get_participant_position(self, participant: str, topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取参与者立场"""
        try:
            # 这里应该调用智能体获取立场
            # 暂时返回模拟结果
            await asyncio.sleep(0.1)  # 模拟思考时间
            
            # 根据参与者类型确定倾向
            if "bull" in participant.lower():
                stance = "bullish"
                confidence = 0.8
                reasoning = "基于乐观预期的看涨立场"
            elif "bear" in participant.lower():
                stance = "bearish"
                confidence = 0.8
                reasoning = "基于风险考虑的看跌立场"
            else:
                stance = "neutral"
                confidence = 0.6
                reasoning = "基于客观分析的中性立场"
            
            return {
                "participant": participant,
                "stance": stance,
                "confidence": confidence,
                "reasoning": reasoning,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 获取参与者立场失败: {participant} - {e}")
            raise
    
    async def _execute_debate_round(self, debate: Dict[str, Any], round_num: int) -> Dict[str, Any]:
        """执行辩论轮次"""
        try:
            participants = debate["participants"]
            context = debate["context"]
            previous_rounds = debate["rounds"]
            
            logger.info(f"🗣️ 执行辩论第{round_num}轮")
            
            round_result = {
                "round_number": round_num,
                "arguments": {},
                "rebuttals": {},
                "round_consensus": None,
                "started_at": datetime.now(),
                "completed_at": None
            }
            
            # 收集本轮论点
            for participant in participants:
                argument = await self._get_participant_argument(
                    participant, debate, previous_rounds
                )
                round_result["arguments"][participant] = argument
            
            # 收集反驳意见
            for participant in participants:
                rebuttal = await self._get_participant_rebuttal(
                    participant, debate, round_result["arguments"]
                )
                round_result["rebuttals"][participant] = rebuttal
            
            # 评估本轮共识
            round_result["round_consensus"] = await self._evaluate_round_consensus(round_result)
            round_result["completed_at"] = datetime.now()
            
            return round_result
            
        except Exception as e:
            logger.error(f"❌ 执行辩论轮次失败: {round_num} - {e}")
            return {
                "round_number": round_num,
                "status": "failed",
                "error": str(e)
            }
    
    async def _get_participant_argument(
        self, 
        participant: str, 
        debate: Dict[str, Any], 
        previous_rounds: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """获取参与者论点"""
        try:
            # 模拟获取论点
            await asyncio.sleep(0.1)
            
            position = debate["positions"].get(participant, {})
            stance = position.get("stance", "neutral")
            
            # 根据立场生成论点
            if stance == "bullish":
                argument = "基于强劲的基本面和技术指标，建议买入"
                evidence = ["财务数据良好", "技术指标向好", "市场情绪积极"]
            elif stance == "bearish":
                argument = "基于风险因素和市场不确定性，建议谨慎"
                evidence = ["估值偏高", "技术指标疲软", "宏观风险增加"]
            else:
                argument = "基于当前信息，建议保持观望"
                evidence = ["信息不足", "市场混合信号", "需要更多数据"]
            
            return {
                "participant": participant,
                "argument": argument,
                "evidence": evidence,
                "confidence": position.get("confidence", 0.5),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 获取参与者论点失败: {participant} - {e}")
            return {
                "participant": participant,
                "argument": "无法生成论点",
                "evidence": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _get_participant_rebuttal(
        self, 
        participant: str, 
        debate: Dict[str, Any], 
        round_arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """获取参与者反驳"""
        try:
            # 模拟反驳生成
            await asyncio.sleep(0.1)
            
            # 简化的反驳逻辑
            other_arguments = {k: v for k, v in round_arguments.items() if k != participant}
            
            rebuttals = []
            for other_participant, other_argument in other_arguments.items():
                rebuttal = f"对{other_participant}的观点，我认为需要考虑..."
                rebuttals.append({
                    "target": other_participant,
                    "rebuttal": rebuttal,
                    "strength": 0.6
                })
            
            return {
                "participant": participant,
                "rebuttals": rebuttals,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 获取参与者反驳失败: {participant} - {e}")
            return {
                "participant": participant,
                "rebuttals": [],
                "error": str(e)
            }
    
    async def _evaluate_round_consensus(self, round_result: Dict[str, Any]) -> Dict[str, Any]:
        """评估轮次共识"""
        try:
            arguments = round_result.get("arguments", {})
            
            # 统计立场分布
            stance_counts = {"bullish": 0, "bearish": 0, "neutral": 0}
            total_confidence = 0
            
            for participant, argument in arguments.items():
                # 简化的立场识别
                if "买入" in argument.get("argument", ""):
                    stance_counts["bullish"] += 1
                elif "卖出" in argument.get("argument", "") or "谨慎" in argument.get("argument", ""):
                    stance_counts["bearish"] += 1
                else:
                    stance_counts["neutral"] += 1
                
                total_confidence += argument.get("confidence", 0.5)
            
            # 计算共识度
            total_participants = len(arguments)
            if total_participants > 0:
                max_stance_count = max(stance_counts.values())
                consensus_ratio = max_stance_count / total_participants
                avg_confidence = total_confidence / total_participants
                
                # 确定主导立场
                dominant_stance = max(stance_counts, key=stance_counts.get)
                
                return {
                    "dominant_stance": dominant_stance,
                    "consensus_ratio": consensus_ratio,
                    "average_confidence": avg_confidence,
                    "stance_distribution": stance_counts,
                    "consensus_strength": consensus_ratio * avg_confidence
                }
            
            return {
                "dominant_stance": "neutral",
                "consensus_ratio": 0.0,
                "average_confidence": 0.0,
                "stance_distribution": stance_counts,
                "consensus_strength": 0.0
            }
            
        except Exception as e:
            logger.error(f"❌ 评估轮次共识失败: {e}")
            return {"error": str(e)}
    
    async def _check_consensus(self, debate: Dict[str, Any]) -> bool:
        """检查是否达成共识"""
        try:
            if not debate["rounds"]:
                return False
            
            latest_round = debate["rounds"][-1]
            round_consensus = latest_round.get("round_consensus", {})
            
            # 如果共识强度超过阈值，认为达成共识
            consensus_strength = round_consensus.get("consensus_strength", 0.0)
            return consensus_strength > 0.7
            
        except Exception as e:
            logger.error(f"❌ 检查共识失败: {e}")
            return False
    
    async def _generate_final_consensus(self, debate: Dict[str, Any]) -> Dict[str, Any]:
        """生成最终共识"""
        try:
            rounds = debate["rounds"]
            if not rounds:
                return {"consensus": "无法达成共识", "confidence": 0.0}
            
            # 分析所有轮次的共识趋势
            stance_evolution = []
            confidence_evolution = []
            
            for round_result in rounds:
                round_consensus = round_result.get("round_consensus", {})
                stance_evolution.append(round_consensus.get("dominant_stance", "neutral"))
                confidence_evolution.append(round_consensus.get("consensus_strength", 0.0))
            
            # 确定最终共识
            if confidence_evolution:
                final_confidence = max(confidence_evolution)
                best_round_index = confidence_evolution.index(final_confidence)
                final_stance = stance_evolution[best_round_index]
            else:
                final_stance = "neutral"
                final_confidence = 0.0
            
            # 生成共识描述
            if final_stance == "bullish":
                consensus_description = "经过充分辩论，倾向于看涨观点"
            elif final_stance == "bearish":
                consensus_description = "经过充分辩论，倾向于看跌观点"
            else:
                consensus_description = "经过充分辩论，保持中性观点"
            
            return {
                "final_stance": final_stance,
                "consensus_description": consensus_description,
                "confidence": final_confidence,
                "rounds_analyzed": len(rounds),
                "consensus_evolution": {
                    "stance_evolution": stance_evolution,
                    "confidence_evolution": confidence_evolution
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 生成最终共识失败: {e}")
            return {
                "final_stance": "neutral",
                "consensus_description": "共识生成失败",
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def get_debate_status(self, debate_id: str) -> Optional[Dict[str, Any]]:
        """获取辩论状态"""
        try:
            debate = self.active_debates.get(debate_id)
            if debate:
                return {
                    "debate_id": debate_id,
                    "status": debate["status"].value,
                    "current_round": debate["current_round"],
                    "total_rounds": len(debate["rounds"]),
                    "participants": debate["participants"],
                    "started_at": debate["started_at"].isoformat(),
                    "completed_at": debate["completed_at"].isoformat() if debate["completed_at"] else None
                }
            
            # 从状态管理器获取
            return await self.state_manager.get_workflow_state(f"debate_{debate_id}")
            
        except Exception as e:
            logger.error(f"❌ 获取辩论状态失败: {debate_id} - {e}")
            return None
    
    async def cancel_debate(self, debate_id: str) -> bool:
        """取消辩论"""
        try:
            if debate_id in self.active_debates:
                self.active_debates[debate_id]["status"] = DebateStatus.CANCELLED
                await self.state_manager.save_workflow_state(
                    f"debate_{debate_id}", 
                    self.active_debates[debate_id]
                )
                logger.info(f"🚫 取消辩论: {debate_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ 取消辩论失败: {debate_id} - {e}")
            return False
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            return True
        except Exception as e:
            logger.error(f"❌ 辩论引擎健康检查失败: {e}")
            return False
    
    async def cleanup(self):
        """清理资源"""
        try:
            # 取消所有活跃的辩论
            for debate_id in list(self.active_debates.keys()):
                await self.cancel_debate(debate_id)
            
            self.active_debates.clear()
            
            logger.info("✅ 辩论引擎清理完成")
            
        except Exception as e:
            logger.error(f"❌ 辩论引擎清理失败: {e}")
