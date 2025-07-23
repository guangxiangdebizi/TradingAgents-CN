"""
基础服务客户端
"""
import httpx
from typing import Optional, Dict, Any
from ..utils.logger import get_service_logger
from ..utils.config import get_config, get_service_config


class BaseServiceClient:
    """基础服务客户端"""
    
    def __init__(self, service_name: str, base_url: Optional[str] = None):
        self.service_name = service_name
        self.logger = get_service_logger(f"client.{service_name}")
        self.config = get_config()
        
        # 设置基础URL
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = self.config.get_service_url(service_name)
        
        # 创建HTTP客户端
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"TradingAgents-Client/{service_name}"
            }
        )
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET请求"""
        try:
            self.logger.debug(f"GET {endpoint} with params: {params}")
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"GET {endpoint} failed: {e}")
            raise
    
    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """POST请求"""
        try:
            self.logger.debug(f"POST {endpoint} with data: {data}")
            response = await self.client.post(endpoint, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"POST {endpoint} failed: {e}")
            raise
    
    async def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT请求"""
        try:
            self.logger.debug(f"PUT {endpoint} with data: {data}")
            response = await self.client.put(endpoint, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"PUT {endpoint} failed: {e}")
            raise
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE请求"""
        try:
            self.logger.debug(f"DELETE {endpoint}")
            response = await self.client.delete(endpoint)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"DELETE {endpoint} failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            response = await self.get("/health")
            status = response.get("status")
            # 接受 "healthy" 和 "degraded" 状态作为可用状态
            return status in ["healthy", "degraded"]
        except Exception as e:
            self.logger.warning(f"Health check failed for {self.service_name}: {e}")
            return False
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
