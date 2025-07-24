"""
辩论API路由
提供智能体辩论和共识达成的REST API接口
"""

import uuid
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from backend.shared.logging_config import get_logger
from ..orchestration.debate_engine import DebateEngine
from ..orchestration.consensus_algorithm import ConsensusAlgorithm, ConsensusMethod
from ..models.agent_models import DebateRequest, DebateResponse
from ..utils.state_manager import StateManager

logger = get_logger("agent-service.debate_api")

router = APIRouter()


def get_debate_engine() -> DebateEngine:
    """获取辩论引擎依赖"""
    from ..main import debate_engine
    if debate_engine is None:
        raise HTTPException(status_code=503, detail="Debate Engine未初始化")
    return debate_engine


def get_consensus_algorithm() -> ConsensusAlgorithm:
    """获取共识算法依赖"""
    from ..main import consensus_algorithm
    if consensus_algorithm is None:
        raise HTTPException(status_code=503, detail="Consensus Algorithm未初始化")
    return consensus_algorithm


def get_state_manager() -> StateManager:
    """获取状态管理器依赖"""
    from ..main import state_manager
    if state_manager is None:
        raise HTTPException(status_code=503, detail="State Manager未初始化")
    return state_manager


@router.post("/start", response_model=DebateResponse)
async def start_debate(
    request: DebateRequest,
    background_tasks: BackgroundTasks,
    engine: DebateEngine = Depends(get_debate_engine)
):
    """启动智能体辩论"""
    try:
        # 记录接收到的请求
        logger.info(f"📥 Agent Service接收到辩论请求: {request.model_dump()}")

        # 启动辩论
        debate_id = await engine.start_debate(
            topic=request.topic,
            participants=[p.value for p in request.participants],
            context=request.context,
            rules=request.rules
        )
        
        # 创建响应
        response = DebateResponse(
            debate_id=debate_id,
            status="running",
            topic=request.topic,
            participants=[p.value for p in request.participants],
            rounds=[],
            consensus=None,
            final_decision=None
        )
        
        logger.info(f"🗣️ 启动辩论: {debate_id} - {request.topic}")
        return response
        
    except Exception as e:
        logger.error(f"❌ 启动辩论失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{debate_id}/status")
async def get_debate_status(
    debate_id: str,
    engine: DebateEngine = Depends(get_debate_engine)
):
    """获取辩论状态"""
    try:
        status = await engine.get_debate_status(debate_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"辩论不存在: {debate_id}")
        
        logger.info(f"📊 获取辩论状态: {debate_id}")
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取辩论状态失败: {debate_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{debate_id}/cancel")
async def cancel_debate(
    debate_id: str,
    engine: DebateEngine = Depends(get_debate_engine)
):
    """取消辩论"""
    try:
        success = await engine.cancel_debate(debate_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"辩论不存在: {debate_id}")
        
        logger.info(f"🚫 取消辩论: {debate_id}")
        return {"message": f"辩论已取消: {debate_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 取消辩论失败: {debate_id} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active")
async def get_active_debates(
    engine: DebateEngine = Depends(get_debate_engine)
):
    """获取活跃的辩论"""
    try:
        active_debates = []
        
        for debate_id, debate in engine.active_debates.items():
            active_debates.append({
                "debate_id": debate_id,
                "topic": debate["topic"],
                "status": debate["status"].value,
                "current_round": debate["current_round"],
                "participants": debate["participants"],
                "started_at": debate["started_at"].isoformat()
            })
        
        logger.info(f"📊 获取活跃辩论: {len(active_debates)}个")
        return {"active_debates": active_debates}
        
    except Exception as e:
        logger.error(f"❌ 获取活跃辩论失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/consensus")
async def reach_consensus(
    agent_results: Dict[str, Any],
    method: str = "hybrid",
    context: Optional[Dict[str, Any]] = None,
    algorithm: ConsensusAlgorithm = Depends(get_consensus_algorithm)
):
    """达成共识"""
    try:
        # 验证共识方法
        try:
            consensus_method = ConsensusMethod(method)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"不支持的共识方法: {method}")
        
        # 执行共识算法
        consensus = await algorithm.reach_consensus(
            agent_results=agent_results,
            method=consensus_method,
            context=context
        )
        
        logger.info(f"🤝 达成共识: {consensus.get('recommendation', 'unknown')}")
        return consensus
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 达成共识失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/consensus/methods")
async def get_consensus_methods():
    """获取可用的共识方法"""
    try:
        methods = []
        for method in ConsensusMethod:
            methods.append({
                "method": method.value,
                "name": method.name,
                "description": _get_method_description(method)
            })
        
        logger.info(f"📋 获取共识方法: {len(methods)}种")
        return {"methods": methods}
        
    except Exception as e:
        logger.error(f"❌ 获取共识方法失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_debate(
    topic: str = "AAPL投资决策",
    participants: List[str] = ["bull_researcher", "bear_researcher"],
    engine: DebateEngine = Depends(get_debate_engine)
):
    """测试辩论功能"""
    try:
        # 创建测试上下文
        context = {
            "symbol": "AAPL",
            "company_name": "Apple Inc.",
            "market": "US",
            "analysis_date": "2025-01-22",
            "test_mode": True
        }
        
        # 启动测试辩论
        debate_id = await engine.start_debate(
            topic=topic,
            participants=participants,
            context=context
        )
        
        logger.info(f"🧪 启动测试辩论: {debate_id}")
        return {
            "debate_id": debate_id,
            "topic": topic,
            "participants": participants,
            "context": context,
            "message": "测试辩论已启动"
        }
        
    except Exception as e:
        logger.error(f"❌ 测试辩论失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/consensus/test")
async def test_consensus(
    method: str = "hybrid",
    algorithm: ConsensusAlgorithm = Depends(get_consensus_algorithm)
):
    """测试共识算法"""
    try:
        # 创建模拟的智能体结果
        mock_results = {
            "fundamentals_analyst": {
                "status": "success",
                "agent_type": "fundamentals_analyst",
                "result": {
                    "recommendation": "buy",
                    "confidence_score": 0.8,
                    "reasoning": "财务数据良好"
                }
            },
            "market_analyst": {
                "status": "success",
                "agent_type": "market_analyst",
                "result": {
                    "recommendation": "buy",
                    "confidence_score": 0.7,
                    "reasoning": "技术指标积极"
                }
            },
            "risk_manager": {
                "status": "success",
                "agent_type": "risk_manager",
                "result": {
                    "recommendation": "hold",
                    "confidence_score": 0.6,
                    "reasoning": "风险需要控制"
                }
            }
        }
        
        # 验证共识方法
        try:
            consensus_method = ConsensusMethod(method)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"不支持的共识方法: {method}")
        
        # 执行共识算法
        consensus = await algorithm.reach_consensus(
            agent_results=mock_results,
            method=consensus_method,
            context={"test_mode": True}
        )
        
        logger.info(f"🧪 测试共识算法: {method}")
        return {
            "method": method,
            "mock_results": mock_results,
            "consensus": consensus,
            "message": "共识算法测试完成"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 测试共识算法失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_debate_statistics(
    engine: DebateEngine = Depends(get_debate_engine),
    state_manager: StateManager = Depends(get_state_manager)
):
    """获取辩论统计信息"""
    try:
        # 当前活跃辩论
        active_count = len(engine.active_debates)
        
        # 模拟历史统计数据
        total_debates = active_count + 15
        completed_debates = 12
        cancelled_debates = 3
        
        # 辩论主题统计
        topic_categories = {
            "投资决策": 8,
            "风险评估": 4,
            "市场分析": 3
        }
        
        # 参与者统计
        participant_stats = {
            "bull_researcher": 10,
            "bear_researcher": 10,
            "neutral_debator": 8,
            "risk_manager": 6
        }
        
        statistics = {
            "current_active": active_count,
            "total_debates": total_debates,
            "completed_debates": completed_debates,
            "cancelled_debates": cancelled_debates,
            "completion_rate": completed_debates / max(total_debates, 1),
            "average_rounds": 2.5,
            "topic_categories": topic_categories,
            "participant_stats": participant_stats
        }
        
        logger.info(f"📊 获取辩论统计信息")
        return statistics
        
    except Exception as e:
        logger.error(f"❌ 获取辩论统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _get_method_description(method: ConsensusMethod) -> str:
    """获取共识方法描述"""
    descriptions = {
        ConsensusMethod.MAJORITY_VOTE: "多数投票 - 选择得票最多的选项",
        ConsensusMethod.WEIGHTED_VOTE: "加权投票 - 根据智能体权重进行投票",
        ConsensusMethod.CONFIDENCE_WEIGHTED: "置信度加权 - 根据置信度进行加权",
        ConsensusMethod.EXPERT_PRIORITY: "专家优先 - 优先考虑专家意见",
        ConsensusMethod.HYBRID: "混合方法 - 综合多种方法达成共识"
    }
    return descriptions.get(method, "未知方法")
