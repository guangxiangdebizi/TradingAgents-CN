"""
Analysis Engine - 分析引擎服务
提供股票分析和AI模型调用功能
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

# 导入独立的分析逻辑 (不直接依赖tradingagents)
from .analysis.independent_analyzer import IndependentAnalyzer
from .analysis.config import ANALYSIS_CONFIG

# 全局变量
logger = get_service_logger("analysis-engine")
redis_client: Optional[redis.Redis] = None
data_service_client: Optional[BaseServiceClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global redis_client, data_service_client
    
    # 启动时初始化
    logger.info("🚀 Analysis Engine 启动中...")
    
    # 初始化Redis连接
    config = get_service_config("analysis_engine")
    try:
        redis_client = redis.from_url(config['redis_url'])
        await redis_client.ping()
        logger.info("✅ Redis 连接成功")
    except Exception as e:
        logger.warning(f"⚠️ Redis 连接失败: {e}")
        redis_client = None
    
    # 初始化数据服务客户端
    try:
        data_service_client = BaseServiceClient("data_service")
        if await data_service_client.health_check():
            logger.info("✅ Data Service 连接成功")
        else:
            logger.warning("⚠️ Data Service 连接失败")
    except Exception as e:
        logger.warning(f"⚠️ Data Service 初始化失败: {e}")
    
    logger.info("✅ Analysis Engine 启动完成")
    
    yield
    
    # 关闭时清理
    logger.info("🛑 Analysis Engine 关闭中...")
    if redis_client:
        await redis_client.close()
    if data_service_client:
        await data_service_client.close()
    logger.info("✅ Analysis Engine 已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="TradingAgents Analysis Engine",
    description="股票分析引擎服务",
    version="1.0.0",
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


async def get_redis() -> Optional[redis.Redis]:
    """获取Redis客户端"""
    return redis_client


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
    
    return HealthCheck(
        service_name="analysis-engine",
        status="healthy",
        version="1.0.0",
        dependencies=dependencies
    )


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


async def perform_stock_analysis(analysis_id: str, request: AnalysisRequest):
    """执行股票分析（后台任务）"""
    try:
        logger.info(f"🔍 开始分析: {analysis_id} - {request.stock_code}")
        
        # 更新进度：开始分析
        await update_analysis_progress(
            analysis_id,
            AnalysisStatus.RUNNING,
            10,
            "初始化分析引擎",
            "初始化AI分析引擎，准备开始分析",
            f"📊 开始分析 {request.stock_code} 股票，这可能需要几分钟时间..."
        )
        
        # 准备分析参数
        analysis_config = {
            "company_of_interest": request.stock_code,
            "trade_date": request.analysis_date.strftime("%Y-%m-%d"),
            "llm_provider": request.llm_provider.value,
            "model_version": request.model_version,
            "enable_memory": request.enable_memory,
            "debug_mode": request.debug_mode,
            "max_output_length": request.max_output_length,
            "include_sentiment": request.include_sentiment,
            "include_risk_assessment": request.include_risk_assessment,
            "custom_prompt": request.custom_prompt,
            "selected_analysts": {
                "market_analyst": request.market_analyst,
                "social_analyst": request.social_analyst,
                "news_analyst": request.news_analyst,
                "fundamental_analyst": request.fundamental_analyst,
            }
        }
        
        # 更新进度：获取数据
        await update_analysis_progress(
            analysis_id,
            AnalysisStatus.RUNNING,
            30,
            "获取股票数据",
            "从数据源获取股票历史数据和基本信息",
            f"📈 正在获取 {request.stock_code} 的历史数据..."
        )
        
        # 更新进度：AI分析
        await update_analysis_progress(
            analysis_id,
            AnalysisStatus.RUNNING,
            60,
            "AI智能分析",
            "AI正在进行多维度分析",
            f"🤖 AI正在分析 {request.stock_code}，请耐心等待..."
        )
        
        # 使用独立分析器进行分析
        config = ANALYSIS_CONFIG.copy()
        config.update({
            "llm_provider": analysis_config.get("llm_provider", "deepseek"),
            "debug_mode": analysis_config.get("debug_mode", False),
            "enable_tradingagents_api": True  # 尝试调用TradingAgents API
        })

        # 初始化独立分析器
        analyzer = IndependentAnalyzer(config=config)

        # 执行分析
        analysis_result_raw = await analyzer.analyze_stock(
            analysis_config["company_of_interest"],
            analysis_config["trade_date"]
        )
        
        # 更新进度：生成报告
        await update_analysis_progress(
            analysis_id,
            AnalysisStatus.RUNNING,
            90,
            "生成分析报告",
            "整理分析结果，生成详细报告",
            f"📄 正在生成 {request.stock_code} 的分析报告..."
        )
        
        # 解析分析结果
        if analysis_result_raw.get("success"):
            analysis_data = analysis_result_raw.get("analysis", {})
            market_data = analysis_result_raw.get("market_data", {})

            # 格式化推荐动作
            action_map = {"BUY": "买入", "SELL": "卖出", "HOLD": "持有"}
            recommendation = action_map.get(analysis_data.get("action", "HOLD"), "持有")

            # 格式化置信度和风险评分
            confidence = f"{analysis_data.get('confidence', 0.5) * 100:.1f}%"
            risk_score = f"{analysis_data.get('risk_score', 0.5) * 100:.1f}%"

            analysis_result = AnalysisResult(
                analysis_id=analysis_id,
                stock_code=request.stock_code,
                stock_name=analysis_result_raw.get("company_name", request.stock_code),
                recommendation=recommendation,
                confidence=confidence,
                risk_score=risk_score,
                target_price=f"{market_data.get('current_price', 0):.2f}",
                reasoning=analysis_data.get("reasoning", "分析完成"),
                technical_analysis=json.dumps(analysis_result_raw, ensure_ascii=False, indent=2),
                analysis_config=analysis_config
            )
        else:
            # 分析失败的情况
            error_msg = analysis_result_raw.get("error", "分析失败")
            analysis_result = AnalysisResult(
                analysis_id=analysis_id,
                stock_code=request.stock_code,
                stock_name=request.stock_code,
                recommendation="持有",
                confidence="50.0%",
                risk_score="50.0%",
                target_price="0.00",
                reasoning=f"分析失败: {error_msg}",
                technical_analysis=json.dumps(analysis_result_raw, ensure_ascii=False, indent=2),
                analysis_config=analysis_config
            )
        
        # 保存分析结果
        await save_analysis_result(analysis_id, analysis_result)
        
        # 更新进度：完成
        await update_analysis_progress(
            analysis_id,
            AnalysisStatus.COMPLETED,
            100,
            "分析完成",
            "分析完成",
            f"✅ {request.stock_code} 分析成功完成！"
        )
        
        logger.info(f"✅ 分析完成: {analysis_id}")
        
    except Exception as e:
        logger.error(f"❌ 分析失败: {analysis_id} - {e}")
        
        # 更新进度：失败
        await update_analysis_progress(
            analysis_id,
            AnalysisStatus.FAILED,
            0,
            "分析失败",
            "分析过程中出现错误",
            f"❌ {request.stock_code} 分析失败",
            str(e)
        )


@app.post("/api/analysis/start", response_model=APIResponse)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """开始股票分析"""
    try:
        # 生成分析ID
        analysis_id = str(uuid.uuid4())
        
        logger.info(f"🚀 启动分析任务: {analysis_id} - {request.stock_code}")
        
        # 初始化进度
        await update_analysis_progress(
            analysis_id,
            AnalysisStatus.PENDING,
            0,
            "准备中",
            "分析任务已创建，等待执行",
            f"📋 分析任务 {analysis_id} 已创建"
        )
        
        # 添加后台任务
        background_tasks.add_task(perform_stock_analysis, analysis_id, request)
        
        return APIResponse(
            success=True,
            message="分析任务已启动",
            data={"analysis_id": analysis_id}
        )
        
    except Exception as e:
        logger.error(f"❌ 启动分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动分析失败: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"获取分析进度失败: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"获取分析结果失败: {str(e)}")


@app.delete("/api/analysis/{analysis_id}", response_model=APIResponse)
async def cancel_analysis(analysis_id: str):
    """取消分析任务"""
    try:
        if not redis_client:
            raise HTTPException(status_code=503, detail="Redis服务不可用")
        
        # 更新状态为取消
        await update_analysis_progress(
            analysis_id,
            AnalysisStatus.CANCELLED,
            0,
            "已取消",
            "分析任务已被用户取消",
            "❌ 分析任务已取消"
        )
        
        return APIResponse(
            success=True,
            message="分析任务已取消"
        )
        
    except Exception as e:
        logger.error(f"❌ 取消分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"取消分析失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    config = get_service_config("analysis_engine")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config['port'],
        reload=config['debug'],
        log_level=config['log_level'].lower()
    )
