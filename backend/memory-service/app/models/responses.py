"""
响应数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: Optional[str] = Field(None, description="响应消息")
    timestamp: str = Field(..., description="响应时间戳")

class MemoryResponse(BaseResponse):
    """记忆操作响应"""
    data: Optional[Dict[str, Any]] = Field(None, description="记忆数据")

class MemoryItem(BaseModel):
    """记忆项"""
    matched_situation: str = Field(..., description="匹配的情况")
    recommendation: str = Field(..., description="建议内容")
    similarity_score: float = Field(..., description="相似度分数")
    metadata: Dict[str, Any] = Field(..., description="元数据")
    distance: float = Field(..., description="向量距离")

class SearchResponse(BaseResponse):
    """搜索响应"""
    results: List[MemoryItem] = Field(..., description="搜索结果")
    total: int = Field(..., description="结果总数")
    query: Optional[str] = Field(None, description="查询文本")

class EmbeddingResponse(BaseResponse):
    """Embedding响应"""
    embedding: List[float] = Field(..., description="Embedding向量")
    dimension: int = Field(..., description="向量维度")
    provider: str = Field(..., description="提供商")
    model: str = Field(..., description="模型名称")

class CollectionResponse(BaseResponse):
    """集合响应"""
    collection_name: str = Field(..., description="集合名称")
    description: Optional[str] = Field(None, description="集合描述")
    metadata: Optional[Dict[str, Any]] = Field(None, description="集合元数据")

class CollectionInfo(BaseModel):
    """集合信息"""
    name: str = Field(..., description="集合名称")
    description: str = Field(..., description="集合描述")
    metadata: Dict[str, Any] = Field(..., description="集合元数据")
    created_at: str = Field(..., description="创建时间")
    count: int = Field(..., description="记忆数量")

class CollectionListResponse(BaseResponse):
    """集合列表响应"""
    collections: List[CollectionInfo] = Field(..., description="集合列表")
    total: int = Field(..., description="集合总数")

class CollectionStatsResponse(BaseResponse):
    """集合统计响应"""
    collection_name: str = Field(..., description="集合名称")
    stats: Dict[str, Any] = Field(..., description="统计信息")

class BatchResponse(BaseResponse):
    """批量操作响应"""
    processed: int = Field(..., description="处理数量")
    successful: int = Field(..., description="成功数量")
    failed: int = Field(..., description="失败数量")
    errors: List[str] = Field(default_factory=list, description="错误列表")

class ProviderInfo(BaseModel):
    """提供商信息"""
    name: str = Field(..., description="提供商名称")
    model: Optional[str] = Field(None, description="模型名称")
    status: str = Field(..., description="状态")
    dimension: Optional[int] = Field(None, description="向量维度")

class ProvidersResponse(BaseResponse):
    """提供商列表响应"""
    providers: List[ProviderInfo] = Field(..., description="提供商列表")
    default_provider: str = Field(..., description="默认提供商")

class DatabaseStatsResponse(BaseResponse):
    """数据库统计响应"""
    total_collections: int = Field(..., description="总集合数")
    total_documents: int = Field(..., description="总文档数")
    storage_type: str = Field(..., description="存储类型")
    db_path: str = Field(..., description="数据库路径")
    collections: List[CollectionInfo] = Field(..., description="集合详情")

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    service: str = Field(..., description="服务名称")
    timestamp: str = Field(..., description="检查时间")
    components: Dict[str, bool] = Field(..., description="组件状态")

class ExportResponse(BaseResponse):
    """导出响应"""
    format: str = Field(..., description="导出格式")
    file_path: Optional[str] = Field(None, description="文件路径")
    download_url: Optional[str] = Field(None, description="下载链接")
    size: int = Field(..., description="文件大小")

class ImportResponse(BaseResponse):
    """导入响应"""
    imported: int = Field(..., description="导入数量")
    skipped: int = Field(..., description="跳过数量")
    errors: List[str] = Field(default_factory=list, description="错误列表")

class AnalysisResult(BaseModel):
    """分析结果"""
    analysis_type: str = Field(..., description="分析类型")
    results: Dict[str, Any] = Field(..., description="分析结果")
    insights: List[str] = Field(default_factory=list, description="洞察")

class AnalysisResponse(BaseResponse):
    """分析响应"""
    collection_name: str = Field(..., description="集合名称")
    analysis: AnalysisResult = Field(..., description="分析结果")

class OptimizationResult(BaseModel):
    """优化结果"""
    operation: str = Field(..., description="优化操作")
    before_stats: Dict[str, Any] = Field(..., description="优化前统计")
    after_stats: Dict[str, Any] = Field(..., description="优化后统计")
    improvements: Dict[str, Any] = Field(..., description="改进指标")

class OptimizationResponse(BaseResponse):
    """优化响应"""
    collection_name: str = Field(..., description="集合名称")
    optimization: OptimizationResult = Field(..., description="优化结果")
