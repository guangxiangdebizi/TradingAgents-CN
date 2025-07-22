"""
请求数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class AddMemoryRequest(BaseModel):
    """添加记忆请求"""
    collection_name: str = Field(..., description="集合名称")
    situation: str = Field(..., description="情况描述")
    recommendation: str = Field(..., description="建议内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")

class SearchMemoryRequest(BaseModel):
    """搜索记忆请求"""
    collection_name: str = Field(..., description="集合名称")
    query: str = Field(..., description="查询文本")
    n_results: int = Field(3, description="返回结果数量", ge=1, le=20)
    similarity_threshold: float = Field(0.0, description="相似度阈值", ge=0.0, le=1.0)

class EmbeddingRequest(BaseModel):
    """生成Embedding请求"""
    text: str = Field(..., description="要生成Embedding的文本")
    provider: Optional[str] = Field(None, description="Embedding提供商")
    model: Optional[str] = Field(None, description="模型名称")

class CreateCollectionRequest(BaseModel):
    """创建集合请求"""
    name: str = Field(..., description="集合名称")
    description: Optional[str] = Field("", description="集合描述")
    metadata: Optional[Dict[str, Any]] = Field(None, description="集合元数据")

class BatchAddMemoryRequest(BaseModel):
    """批量添加记忆请求"""
    collection_name: str = Field(..., description="集合名称")
    situations_and_advice: List[tuple] = Field(..., description="情况和建议列表")
    metadata: Optional[Dict[str, Any]] = Field(None, description="通用元数据")

class UpdateMemoryRequest(BaseModel):
    """更新记忆请求"""
    collection_name: str = Field(..., description="集合名称")
    memory_id: str = Field(..., description="记忆ID")
    situation: Optional[str] = Field(None, description="新的情况描述")
    recommendation: Optional[str] = Field(None, description="新的建议内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="新的元数据")

class DeleteMemoryRequest(BaseModel):
    """删除记忆请求"""
    collection_name: str = Field(..., description="集合名称")
    memory_id: str = Field(..., description="记忆ID")

class ExportMemoryRequest(BaseModel):
    """导出记忆请求"""
    collection_name: str = Field(..., description="集合名称")
    format: str = Field("json", description="导出格式", pattern="^(json|csv|xlsx)$")
    include_embeddings: bool = Field(False, description="是否包含Embedding向量")

class ImportMemoryRequest(BaseModel):
    """导入记忆请求"""
    collection_name: str = Field(..., description="集合名称")
    data: List[Dict[str, Any]] = Field(..., description="要导入的数据")
    overwrite: bool = Field(False, description="是否覆盖现有数据")

class AnalyzeMemoryRequest(BaseModel):
    """分析记忆请求"""
    collection_name: str = Field(..., description="集合名称")
    analysis_type: str = Field("similarity", description="分析类型", pattern="^(similarity|clustering|trends)$")
    parameters: Optional[Dict[str, Any]] = Field(None, description="分析参数")

class OptimizeCollectionRequest(BaseModel):
    """优化集合请求"""
    collection_name: str = Field(..., description="集合名称")
    operation: str = Field("compact", description="优化操作", pattern="^(compact|reindex|cleanup)$")
    parameters: Optional[Dict[str, Any]] = Field(None, description="优化参数")
