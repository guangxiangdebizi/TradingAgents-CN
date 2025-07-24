"""
LLM服务客户端
"""

from typing import Optional, Dict, Any, List
from .base import BaseServiceClient
from ..utils.logger import get_service_logger

logger = get_service_logger("llm-client")


class LLMClient(BaseServiceClient):
    """LLM服务客户端"""
    
    def __init__(self, base_url: Optional[str] = None):
        super().__init__("llm-service", base_url)
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        聊天完成接口
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数
        
        Returns:
            LLM响应结果
        """
        try:
            data = {
                "messages": messages,
                "model": model,
                "temperature": temperature,
                **kwargs
            }

            if max_tokens:
                data["max_tokens"] = max_tokens

            self.logger.info(f"🔍 LLM客户端请求: model={model}, messages_count={len(messages)}")
            self.logger.info(f"🔍 LLM客户端消息: {[{'role': msg['role'], 'content': msg['content'][:200] + '...' if len(msg['content']) > 200 else msg['content']} for msg in messages]}")
            self.logger.info(f"🔍 LLM客户端请求数据: {data}")
            self.logger.info(f"🔍 LLM客户端请求URL: {self.base_url}/api/v1/chat/completions")
            self.logger.info(f"🔍 LLM客户端base_url: {self.base_url}")
            self.logger.info(f"🔍 LLM客户端完整请求路径: /api/v1/chat/completions")

            response = await self.post("/api/v1/chat/completions", data)

            self.logger.info(f"🔍 LLM客户端响应: {response}")
            return response
            
        except Exception as e:
            # 判断是否为连接错误或超时错误
            if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
                self.logger.critical(f"🚨 严重告警: LLM Service不可达 - 无法完成对话")
                self.logger.critical(f"🚨 请检查LLM Service是否启动: {self.base_url}")
                self.logger.critical(f"🚨 错误详情: {type(e).__name__}: {str(e)}")
            else:
                self.logger.error(f"Chat completion failed: {e}")
            raise
    
    async def analyze_text(
        self,
        text: str,
        analysis_type: str = "sentiment",
        model: str = "deepseek-chat",
        **kwargs
    ) -> Dict[str, Any]:
        """
        文本分析接口
        
        Args:
            text: 要分析的文本
            analysis_type: 分析类型 (sentiment, summary, keywords等)
            model: 模型名称
            **kwargs: 其他参数
        
        Returns:
            分析结果
        """
        try:
            data = {
                "text": text,
                "analysis_type": analysis_type,
                "model": model,
                **kwargs
            }
            
            self.logger.debug(f"Text analysis request: type={analysis_type}, text_length={len(text)}")
            response = await self.post("/api/v1/analyze", data)
            
            self.logger.debug(f"Text analysis response: {response.get('success', False)}")
            return response
            
        except Exception as e:
            self.logger.error(f"Text analysis failed: {e}")
            raise
    
    async def generate_report(
        self,
        data: Dict[str, Any],
        report_type: str = "analysis",
        model: str = "deepseek-chat",
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成报告接口
        
        Args:
            data: 报告数据
            report_type: 报告类型
            model: 模型名称
            **kwargs: 其他参数
        
        Returns:
            生成的报告
        """
        try:
            request_data = {
                "data": data,
                "report_type": report_type,
                "model": model,
                **kwargs
            }
            
            self.logger.debug(f"Report generation request: type={report_type}")
            response = await self.post("/api/v1/generate/report", request_data)
            
            self.logger.debug(f"Report generation response: {response.get('success', False)}")
            return response
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise
    
    async def get_models(self) -> Dict[str, Any]:
        """
        获取可用模型列表
        
        Returns:
            模型列表
        """
        try:
            self.logger.debug("Getting available models")
            response = await self.get("/api/v1/models")
            
            self.logger.debug(f"Models response: {len(response.get('data', {}).get('models', []))} models")
            return response
            
        except Exception as e:
            self.logger.error(f"Get models failed: {e}")
            raise
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """
        获取使用统计
        
        Returns:
            使用统计信息
        """
        try:
            self.logger.debug("Getting usage statistics")
            response = await self.get("/api/v1/usage/stats")
            
            self.logger.debug("Usage stats retrieved successfully")
            return response
            
        except Exception as e:
            self.logger.error(f"Get usage stats failed: {e}")
            raise


# 全局LLM客户端实例
_llm_client: Optional[LLMClient] = None


def get_llm_client(base_url: Optional[str] = None) -> LLMClient:
    """
    获取LLM客户端实例
    
    Args:
        base_url: LLM服务的基础URL
    
    Returns:
        LLM客户端实例
    """
    global _llm_client
    
    if _llm_client is None:
        _llm_client = LLMClient(base_url)
    
    return _llm_client


async def close_llm_client():
    """关闭LLM客户端"""
    global _llm_client
    
    if _llm_client:
        await _llm_client.close()
        _llm_client = None
