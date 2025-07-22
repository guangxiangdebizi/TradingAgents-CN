"""
Analysis Engine - 集成版分析引擎服务
集成Agent Service的多智能体分析能力
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any

# 导入共享模块
from backend.shared.models.analysis import (
    AnalysisRequest, AnalysisProgress, AnalysisResult, 
    AnalysisStatus, APIResponse, HealthCheck
)
from backend.shared.utils.logger import get_service_logger
from backend.shared.utils.config import get_service_config
from backend.shared.clients.base import BaseServiceClient

# 导入增强分析器
from .analysis.enhanced_analyzer import EnhancedAnalyzer
from .integrations.agent_service_client import get_agent_service_client, cleanup_agent_service_client

# 全局变量
logger = get_service_logger("analysis-engine-integrated")
redis_client: Optional[redis.Redis] = None
data_service_client: Optional[BaseServiceClient] = None
enhanced_analyzer: Optional[EnhancedAnalyzer] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global redis_client, data_service_client, enhanced_analyzer
    
    # 启动时初始化
    logger.info("🚀 Analysis Engine Integrated 启动中...")
    
    # 初始化Redis连接
    config = get_service_config("analysis_engine")
    redis_config = config.get("redis", {})
    
    try:
        redis_client = redis.Redis(
            host=redis_config.get("host", "localhost"),
            port=redis_config.get("port", 6379),
            db=redis_config.get("db", 0),
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("✅ Redis连接成功")
    except Exception as e:
        logger.warning(f"⚠️ Redis连接失败: {e}")
        redis_client = None
    
    # 初始化数据服务客户端
    try:
        data_service_url = config.get("data_service_url", "http://localhost:8001")
        data_service_client = BaseServiceClient(data_service_url)
        if await data_service_client.health_check():
            logger.info("✅ 数据服务连接成功")
        else:
            logger.warning("⚠️ 数据服务连接失败")
            data_service_client = None
    except Exception as e:
        logger.warning(f"⚠️ 数据服务初始化失败: {e}")
        data_service_client = None
    
    # 初始化增强分析器
    try:
        enhanced_analyzer = EnhancedAnalyzer()
        await enhanced_analyzer.initialize()
        logger.info("✅ 增强分析器初始化成功")
    except Exception as e:
        logger.error(f"❌ 增强分析器初始化失败: {e}")
        enhanced_analyzer = None
    
    logger.info("✅ Analysis Engine Integrated 启动完成")
    
    yield
    
    # 关闭时清理
    logger.info("🔄 Analysis Engine Integrated 关闭中...")
    
    try:
        if enhanced_analyzer:
            await enhanced_analyzer.cleanup()
        
        await cleanup_agent_service_client()
        
        if redis_client:
            await redis_client.close()
        
        if data_service_client:
            await data_service_client.close()
            
        logger.info("✅ Analysis Engine Integrated 关闭完成")
    except Exception as e:
        logger.error(f"❌ 关闭过程中发生错误: {e}")


# 创建FastAPI应用
app = FastAPI(
    title="TradingAgents Analysis Engine Integrated",
    description="集成版股票分析引擎 - 支持多智能体协作分析",
    version="2.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "TradingAgents Analysis Engine Integrated",
        "version": "2.0.0",
        "description": "集成版股票分析引擎 - 支持多智能体协作分析",
        "features": [
            "多智能体协作分析",
            "工作流编排分析", 
            "智能体辩论分析",
            "传统独立分析",
            "智能分析策略选择"
        ]
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """健康检查"""
    dependencies = {}
    
    # 检查Redis连接
    if redis_client:
        try:
            await redis_client.ping()
            dependencies["redis"] = "healthy"
        except Exception:
            dependencies["redis"] = "unhealthy"
    else:
        dependencies["redis"] = "not_configured"
    
    # 检查数据服务连接
    if data_service_client:
        if await data_service_client.health_check():
            dependencies["data_service"] = "healthy"
        else:
            dependencies["data_service"] = "unhealthy"
    else:
        dependencies["data_service"] = "not_configured"
    
    # 检查Agent Service连接
    try:
        agent_client = await get_agent_service_client()
        if await agent_client.health_check():
            dependencies["agent_service"] = "healthy"
        else:
            dependencies["agent_service"] = "unhealthy"
    except Exception:
        dependencies["agent_service"] = "unhealthy"
    
    # 检查增强分析器
    if enhanced_analyzer:
        capabilities = await enhanced_analyzer.get_analysis_capabilities()
        dependencies["enhanced_analyzer"] = "healthy" if capabilities["agent_service_available"] else "degraded"
    else:
        dependencies["enhanced_analyzer"] = "not_configured"
    
    return HealthCheck(
        service_name="analysis-engine-integrated",
        status="healthy",
        version="2.0.0",
        dependencies=dependencies
    )


@app.get("/capabilities")
async def get_capabilities():
    """获取分析能力"""
    try:
        if enhanced_analyzer:
            capabilities = await enhanced_analyzer.get_analysis_capabilities()
            return APIResponse(
                success=True,
                message="获取分析能力成功",
                data=capabilities
            )
        else:
            return APIResponse(
                success=False,
                message="增强分析器未初始化",
                data={"independent_analysis": True}
            )
    except Exception as e:
        logger.error(f"❌ 获取分析能力失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def update_analysis_progress(
    analysis_id: str,
    status: AnalysisStatus,
    progress_percentage: int = 0,
    current_step: str = "",
    current_task: str = "",
    current_status: str = "",
    error_message: Optional[str] = None
):
    """更新分析进度"""
    if not redis_client:
        return
    
    try:
        progress = AnalysisProgress(
            analysis_id=analysis_id,
            status=status,
            progress_percentage=progress_percentage,
            current_step=current_step,
            current_task=current_task,
            current_status=current_status,
            error_message=error_message
        )
        
        # 保存到Redis
        await redis_client.setex(
            f"analysis_progress:{analysis_id}",
            3600,  # 1小时过期
            progress.model_dump_json()
        )
        
        logger.debug(f"📊 更新分析进度: {analysis_id} - {progress_percentage}%")
        
    except Exception as e:
        logger.error(f"❌ 更新分析进度失败: {e}")


async def save_analysis_result(analysis_id: str, result: AnalysisResult):
    """保存分析结果"""
    if not redis_client:
        return
    
    try:
        # 保存到Redis
        await redis_client.setex(
            f"analysis_result:{analysis_id}",
            86400,  # 24小时过期
            result.model_dump_json()
        )
        
        logger.info(f"💾 保存分析结果: {analysis_id}")
        
    except Exception as e:
        logger.error(f"❌ 保存分析结果失败: {e}")


async def perform_integrated_analysis(analysis_id: str, request: AnalysisRequest):
    """执行集成分析（后台任务）"""
    try:
        logger.info(f"🔍 开始集成分析: {analysis_id} - {request.stock_code}")
        
        # 更新进度：开始分析
        await update_analysis_progress(
            analysis_id,
            AnalysisStatus.RUNNING,
            10,
            "初始化",
            "准备集成分析",
            f"🚀 开始分析 {request.stock_code}"
        )
        
        if not enhanced_analyzer:
            raise Exception("增强分析器未初始化")
        
        # 定义进度回调函数
        async def progress_callback(percentage: int, step: str, task: str):
            await update_analysis_progress(
                analysis_id,
                AnalysisStatus.RUNNING,
                percentage,
                step,
                task,
                f"📊 {step}: {task}"
            )
        
        # 执行集成分析
        analysis_result_raw = await enhanced_analyzer.analyze_stock(
            request, progress_callback
        )
        
        # 更新进度：处理结果
        await update_analysis_progress(
            analysis_id,
            AnalysisStatus.RUNNING,
            95,
            "处理结果",
            "格式化分析结果",
            "📋 处理分析结果"
        )
        
        # 转换为标准格式
        if analysis_result_raw.get("success", False):
            analysis_result = AnalysisResult(
                analysis_id=analysis_id,
                stock_code=request.stock_code,
                stock_name=analysis_result_raw.get("stock_name", request.stock_code),
                recommendation=analysis_result_raw.get("recommendation", "持有"),
                confidence=analysis_result_raw.get("confidence", "50.0%"),
                risk_score=analysis_result_raw.get("risk_score", "50.0%"),
                target_price=analysis_result_raw.get("target_price", "0.00"),
                reasoning=analysis_result_raw.get("reasoning", "集成分析完成"),
                technical_analysis=analysis_result_raw.get("technical_analysis", "{}"),
                analysis_config={
                    "analysis_type": analysis_result_raw.get("analysis_type", "integrated"),
                    "timestamp": analysis_result_raw.get("timestamp", datetime.now().isoformat()),
                    "agent_service_used": analysis_result_raw.get("analysis_type", "").startswith("multi_agent") or 
                                         analysis_result_raw.get("analysis_type", "").startswith("agent_")
                }
            )
        else:
            # 分析失败的情况
            error_msg = analysis_result_raw.get("error", "集成分析失败")
            analysis_result = AnalysisResult(
                analysis_id=analysis_id,
                stock_code=request.stock_code,
                stock_name=request.stock_code,
                recommendation="持有",
                confidence="50.0%",
                risk_score="50.0%",
                target_price="0.00",
                reasoning=f"集成分析失败: {error_msg}",
                technical_analysis=json.dumps(analysis_result_raw, ensure_ascii=False, indent=2),
                analysis_config={
                    "analysis_type": "integrated_failed",
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        # 保存分析结果
        await save_analysis_result(analysis_id, analysis_result)
        
        # 更新进度：完成
        await update_analysis_progress(
            analysis_id,
            AnalysisStatus.COMPLETED,
            100,
            "分析完成",
            "集成分析完成",
            f"✅ {request.stock_code} 集成分析成功完成！"
        )
        
        logger.info(f"✅ 集成分析完成: {analysis_id}")
        
    except Exception as e:
        logger.error(f"❌ 集成分析失败: {analysis_id} - {e}")
        
        # 更新进度：失败
        await update_analysis_progress(
            analysis_id,
            AnalysisStatus.FAILED,
            0,
            "分析失败",
            "集成分析过程中出现错误",
            f"❌ {request.stock_code} 集成分析失败",
            str(e)
        )


@app.post("/api/analysis/start", response_model=APIResponse)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """开始股票分析 - 智能选择分析方式"""
    try:
        # 生成分析ID
        analysis_id = str(uuid.uuid4())
        
        logger.info(f"🚀 启动集成分析任务: {analysis_id} - {request.stock_code}")
        
        # 初始化进度
        await update_analysis_progress(
            analysis_id,
            AnalysisStatus.PENDING,
            0,
            "准备中",
            "集成分析任务已创建，等待执行",
            f"📋 集成分析任务 {analysis_id} 已创建"
        )
        
        # 添加后台任务
        background_tasks.add_task(perform_integrated_analysis, analysis_id, request)
        
        return APIResponse(
            success=True,
            message="集成分析任务已启动",
            data={
                "analysis_id": analysis_id,
                "analysis_type": "integrated_smart"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ 启动集成分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动集成分析失败: {str(e)}")


@app.get("/api/analysis/{analysis_id}/progress", response_model=APIResponse)
async def get_analysis_progress(analysis_id: str):
    """获取分析进度"""
    try:
        if not redis_client:
            raise HTTPException(status_code=503, detail="Redis服务不可用")
        
        # 从Redis获取进度
        progress_data = await redis_client.get(f"analysis_progress:{analysis_id}")
        
        if not progress_data:
            raise HTTPException(status_code=404, detail="分析任务不存在")
        
        progress = json.loads(progress_data)
        
        return APIResponse(
            success=True,
            message="获取分析进度成功",
            data=progress
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取分析进度失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/{analysis_id}/result", response_model=APIResponse)
async def get_analysis_result(analysis_id: str):
    """获取分析结果"""
    try:
        if not redis_client:
            raise HTTPException(status_code=503, detail="Redis服务不可用")
        
        # 从Redis获取结果
        result_data = await redis_client.get(f"analysis_result:{analysis_id}")
        
        if not result_data:
            raise HTTPException(status_code=404, detail="分析结果不存在")
        
        result = json.loads(result_data)
        
        return APIResponse(
            success=True,
            message="获取分析结果成功",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取分析结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
