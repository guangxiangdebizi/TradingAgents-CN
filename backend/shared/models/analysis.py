"""
分析相关的数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MarketType(str, Enum):
    """市场类型"""
    A_STOCK = "A股"
    US_STOCK = "美股"
    HK_STOCK = "港股"


class AnalysisStatus(str, Enum):
    """分析状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LLMProvider(str, Enum):
    """LLM提供商"""
    DASHSCOPE = "dashscope"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    GEMINI = "gemini"


class AnalysisRequest(BaseModel):
    """分析请求模型"""
    stock_code: str = Field(..., description="股票代码")
    market_type: MarketType = Field(default=MarketType.A_STOCK, description="市场类型")
    analysis_date: datetime = Field(default_factory=datetime.now, description="分析日期")
    research_depth: int = Field(default=3, ge=1, le=5, description="研究深度")
    
    # 分析师选择
    market_analyst: bool = Field(default=True, description="市场分析师")
    social_analyst: bool = Field(default=False, description="社交媒体分析师")
    news_analyst: bool = Field(default=False, description="新闻分析师")
    fundamental_analyst: bool = Field(default=True, description="基本面分析师")
    
    # AI模型配置
    llm_provider: LLMProvider = Field(default=LLMProvider.DASHSCOPE, description="LLM提供商")
    model_version: str = Field(default="plus-balanced", description="模型版本")
    enable_memory: bool = Field(default=True, description="启用记忆功能")
    debug_mode: bool = Field(default=False, description="调试模式")
    max_output_length: int = Field(default=4000, description="最大输出长度")
    
    # 高级选项
    include_sentiment: bool = Field(default=True, description="包含情绪分析")
    include_risk_assessment: bool = Field(default=True, description="包含风险评估")
    custom_prompt: Optional[str] = Field(default=None, description="自定义分析要求")


class AnalysisProgress(BaseModel):
    """分析进度模型"""
    analysis_id: str = Field(..., description="分析ID")
    status: AnalysisStatus = Field(..., description="分析状态")
    progress_percentage: int = Field(default=0, ge=0, le=100, description="进度百分比")
    current_step: str = Field(default="", description="当前步骤")
    current_task: str = Field(default="", description="当前任务")
    current_status: str = Field(default="", description="当前状态")
    elapsed_time: str = Field(default="0秒", description="已用时间")
    estimated_remaining: str = Field(default="计算中...", description="预计剩余时间")
    start_time: datetime = Field(default_factory=datetime.now, description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    error_message: Optional[str] = Field(default=None, description="错误信息")


class AnalysisResult(BaseModel):
    """分析结果模型"""
    analysis_id: str = Field(..., description="分析ID")
    stock_code: str = Field(..., description="股票代码")
    stock_name: Optional[str] = Field(default=None, description="股票名称")
    current_price: Optional[str] = Field(default=None, description="当前价格")
    change: Optional[str] = Field(default=None, description="价格变化")
    change_percent: Optional[str] = Field(default=None, description="变化百分比")
    
    # 投资决策
    recommendation: str = Field(default="持有", description="投资建议")
    confidence: str = Field(default="70.0%", description="置信度")
    risk_score: str = Field(default="50.0%", description="风险评分")
    target_price: Optional[str] = Field(default=None, description="目标价位")
    reasoning: Optional[str] = Field(default=None, description="AI分析推理")
    
    # 详细分析
    technical_analysis: Optional[str] = Field(default=None, description="技术分析")
    technical_indicators: Optional[str] = Field(default=None, description="技术指标")
    fundamental_analysis: Optional[str] = Field(default=None, description="基本面分析")
    sentiment_analysis: Optional[str] = Field(default=None, description="市场情绪分析")
    news_analysis: Optional[str] = Field(default=None, description="新闻事件分析")
    risk_analysis: Optional[str] = Field(default=None, description="风险评估")
    investment_advice: Optional[str] = Field(default=None, description="投资建议")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    analysis_config: Optional[Dict[str, Any]] = Field(default=None, description="分析配置")


class ExportRequest(BaseModel):
    """导出请求模型"""
    analysis_id: str = Field(..., description="分析ID")
    format: str = Field(..., description="导出格式", pattern="^(markdown|word|pdf)$")
    include_charts: bool = Field(default=True, description="包含图表")


class APIResponse(BaseModel):
    """统一API响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    error_code: Optional[str] = Field(default=None, description="错误代码")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class HealthCheck(BaseModel):
    """健康检查模型"""
    service_name: str = Field(..., description="服务名称")
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="服务版本")
    timestamp: datetime = Field(default_factory=datetime.now, description="检查时间")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="依赖服务状态")
