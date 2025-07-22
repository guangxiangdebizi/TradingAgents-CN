"""
任务相关的数据模型
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(str, Enum):
    """任务优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskType(str, Enum):
    """任务类型枚举"""
    SINGLE_ANALYSIS = "single_analysis"
    COMPREHENSIVE_ANALYSIS = "comprehensive_analysis"
    DEBATE_ANALYSIS = "debate_analysis"
    COLLABORATION_WORKFLOW = "collaboration_workflow"
    BATCH_ANALYSIS = "batch_analysis"


class TaskRequest(BaseModel):
    """任务请求模型"""
    task_type: TaskType = Field(..., description="任务类型")
    symbol: str = Field(..., description="股票代码")
    company_name: str = Field(..., description="公司名称")
    market: str = Field(default="US", description="市场")
    analysis_date: str = Field(..., description="分析日期")
    analysis_types: List[str] = Field(default_factory=list, description="分析类型列表")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="任务参数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="任务优先级")
    timeout: int = Field(default=600, description="超时时间（秒）")
    callback_url: Optional[str] = Field(default=None, description="回调URL")
    user_id: Optional[str] = Field(default=None, description="用户ID")


class TaskContext(BaseModel):
    """任务上下文模型"""
    task_id: str = Field(..., description="任务ID")
    symbol: str = Field(..., description="股票代码")
    company_name: str = Field(..., description="公司名称")
    market: str = Field(..., description="市场")
    analysis_date: str = Field(..., description="分析日期")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="任务参数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskResult(BaseModel):
    """任务结果模型"""
    task_id: str = Field(..., description="任务ID")
    agent_id: str = Field(..., description="执行智能体ID")
    agent_type: str = Field(..., description="智能体类型")
    status: TaskStatus = Field(..., description="任务状态")
    result: Dict[str, Any] = Field(default_factory=dict, description="执行结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    duration: float = Field(default=0.0, description="执行时间（秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="完成时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    progress: float = Field(default=0.0, description="进度百分比")
    current_step: Optional[str] = Field(default=None, description="当前步骤")
    results: List[TaskResult] = Field(default_factory=list, description="子任务结果")
    final_result: Optional[Dict[str, Any]] = Field(default=None, description="最终结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    started_at: Optional[datetime] = Field(default=None, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    total_duration: float = Field(default=0.0, description="总执行时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BatchTaskRequest(BaseModel):
    """批量任务请求模型"""
    batch_id: str = Field(..., description="批次ID")
    tasks: List[TaskRequest] = Field(..., description="任务列表")
    execution_mode: str = Field(default="parallel", description="执行模式（parallel/sequential）")
    max_concurrent: int = Field(default=5, description="最大并发数")
    timeout: int = Field(default=1800, description="总超时时间（秒）")
    callback_url: Optional[str] = Field(default=None, description="回调URL")


class BatchTaskResponse(BaseModel):
    """批量任务响应模型"""
    batch_id: str = Field(..., description="批次ID")
    total_tasks: int = Field(..., description="总任务数")
    completed_tasks: int = Field(default=0, description="已完成任务数")
    failed_tasks: int = Field(default=0, description="失败任务数")
    progress: float = Field(default=0.0, description="整体进度")
    status: str = Field(..., description="批次状态")
    task_results: List[TaskResponse] = Field(default_factory=list, description="任务结果")
    started_at: datetime = Field(default_factory=datetime.now, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    total_duration: float = Field(default=0.0, description="总执行时间")


class WorkflowStep(BaseModel):
    """工作流步骤模型"""
    step_id: str = Field(..., description="步骤ID")
    step_name: str = Field(..., description="步骤名称")
    agent_type: str = Field(..., description="执行智能体类型")
    dependencies: List[str] = Field(default_factory=list, description="依赖步骤")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="步骤参数")
    timeout: int = Field(default=300, description="步骤超时时间")
    retry_count: int = Field(default=0, description="重试次数")
    max_retries: int = Field(default=3, description="最大重试次数")


class WorkflowDefinition(BaseModel):
    """工作流定义模型"""
    workflow_id: str = Field(..., description="工作流ID")
    workflow_name: str = Field(..., description="工作流名称")
    description: str = Field(..., description="工作流描述")
    steps: List[WorkflowStep] = Field(..., description="工作流步骤")
    execution_mode: str = Field(default="sequential", description="执行模式")
    timeout: int = Field(default=1800, description="总超时时间")
    version: str = Field(default="1.0", description="版本号")


class WorkflowExecution(BaseModel):
    """工作流执行模型"""
    execution_id: str = Field(..., description="执行ID")
    workflow_id: str = Field(..., description="工作流ID")
    status: str = Field(..., description="执行状态")
    current_step: Optional[str] = Field(default=None, description="当前步骤")
    completed_steps: List[str] = Field(default_factory=list, description="已完成步骤")
    failed_steps: List[str] = Field(default_factory=list, description="失败步骤")
    step_results: Dict[str, TaskResult] = Field(default_factory=dict, description="步骤结果")
    context: Dict[str, Any] = Field(default_factory=dict, description="执行上下文")
    started_at: datetime = Field(default_factory=datetime.now, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    total_duration: float = Field(default=0.0, description="总执行时间")


class TaskQueue(BaseModel):
    """任务队列模型"""
    queue_name: str = Field(..., description="队列名称")
    pending_tasks: int = Field(default=0, description="待处理任务数")
    running_tasks: int = Field(default=0, description="运行中任务数")
    completed_tasks: int = Field(default=0, description="已完成任务数")
    failed_tasks: int = Field(default=0, description="失败任务数")
    max_size: int = Field(default=1000, description="队列最大容量")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")


class TaskStatistics(BaseModel):
    """任务统计模型"""
    total_tasks: int = Field(default=0, description="总任务数")
    successful_tasks: int = Field(default=0, description="成功任务数")
    failed_tasks: int = Field(default=0, description="失败任务数")
    cancelled_tasks: int = Field(default=0, description="取消任务数")
    timeout_tasks: int = Field(default=0, description="超时任务数")
    average_duration: float = Field(default=0.0, description="平均执行时间")
    success_rate: float = Field(default=0.0, description="成功率")
    failure_rate: float = Field(default=0.0, description="失败率")
    throughput: float = Field(default=0.0, description="吞吐量（任务/小时）")
    peak_concurrent_tasks: int = Field(default=0, description="峰值并发任务数")
    statistics_date: datetime = Field(default_factory=datetime.now, description="统计日期")


class TaskFilter(BaseModel):
    """任务过滤器模型"""
    status: Optional[List[TaskStatus]] = Field(default=None, description="状态过滤")
    agent_types: Optional[List[str]] = Field(default=None, description="智能体类型过滤")
    symbols: Optional[List[str]] = Field(default=None, description="股票代码过滤")
    markets: Optional[List[str]] = Field(default=None, description="市场过滤")
    priority: Optional[List[TaskPriority]] = Field(default=None, description="优先级过滤")
    date_from: Optional[datetime] = Field(default=None, description="开始日期")
    date_to: Optional[datetime] = Field(default=None, description="结束日期")
    user_id: Optional[str] = Field(default=None, description="用户ID过滤")
    limit: int = Field(default=100, description="返回数量限制")
    offset: int = Field(default=0, description="偏移量")


class TaskSearchRequest(BaseModel):
    """任务搜索请求模型"""
    filters: TaskFilter = Field(default_factory=TaskFilter, description="过滤条件")
    sort_by: str = Field(default="created_at", description="排序字段")
    sort_order: str = Field(default="desc", description="排序顺序")
    include_results: bool = Field(default=False, description="是否包含结果详情")


class TaskSearchResponse(BaseModel):
    """任务搜索响应模型"""
    total_count: int = Field(..., description="总数量")
    tasks: List[TaskResponse] = Field(..., description="任务列表")
    has_more: bool = Field(..., description="是否有更多数据")
    next_offset: Optional[int] = Field(default=None, description="下一页偏移量")


class TaskCancellationRequest(BaseModel):
    """任务取消请求模型"""
    task_id: str = Field(..., description="任务ID")
    reason: Optional[str] = Field(default=None, description="取消原因")
    force: bool = Field(default=False, description="是否强制取消")


class TaskRetryRequest(BaseModel):
    """任务重试请求模型"""
    task_id: str = Field(..., description="任务ID")
    retry_count: int = Field(default=1, description="重试次数")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="新的参数")


class TaskMetrics(BaseModel):
    """任务指标模型"""
    task_id: str = Field(..., description="任务ID")
    cpu_usage: float = Field(default=0.0, description="CPU使用率")
    memory_usage: float = Field(default=0.0, description="内存使用量（MB）")
    network_io: float = Field(default=0.0, description="网络IO（KB）")
    disk_io: float = Field(default=0.0, description="磁盘IO（KB）")
    llm_tokens_used: int = Field(default=0, description="LLM Token使用量")
    api_calls_made: int = Field(default=0, description="API调用次数")
    cache_hits: int = Field(default=0, description="缓存命中次数")
    cache_misses: int = Field(default=0, description="缓存未命中次数")
    timestamp: datetime = Field(default_factory=datetime.now, description="指标时间")
