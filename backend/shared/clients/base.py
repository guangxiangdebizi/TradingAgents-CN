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
            timeout=300.0,  # 设置为300秒，适应LLM模型调用时间
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"TradingAgents-Client/{service_name}"
            }
        )
    
    async def get(self, endpoint: str, params: Optional[Dict] = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        """GET请求"""
        try:
            self.logger.debug(f"GET {endpoint} with params: {params}")

            # 如果指定了timeout，创建临时客户端
            if timeout is not None:
                async with httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=timeout,
                    headers=self.client.headers
                ) as temp_client:
                    response = await temp_client.get(endpoint, params=params)
            else:
                response = await self.client.get(endpoint, params=params)

            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            # 判断是否为连接错误或超时错误
            if isinstance(e, (httpx.ConnectError, httpx.TimeoutException)):
                self.logger.critical(f"🚨 严重告警: 目标服务不可达或超时 - {self.base_url}{endpoint}")
                self.logger.critical(f"🚨 错误类型: {type(e).__name__}, 详情: {str(e)}")
                self.logger.critical(f"🚨 请检查目标服务是否启动: {self.base_url}")
            else:
                self.logger.error(f"GET {endpoint} failed: {e}")
            raise
    
    async def post(self, endpoint: str, data: Optional[Dict] = None, headers: Optional[Dict] = None, timeout: Optional[float] = None, raw_data: Optional[bytes] = None) -> Dict[str, Any]:
        """POST请求"""
        try:
            self.logger.info(f"🔍 BaseClient POST请求: {self.base_url}{endpoint}")
            self.logger.info(f"🔍 BaseClient base_url: {self.base_url}")
            self.logger.info(f"🔍 BaseClient endpoint: {endpoint}")
            self.logger.info(f"🔍 BaseClient 请求数据: {data if data else 'raw_data'}")
            self.logger.debug(f"POST {endpoint} with data: {data if data else 'raw_data'}")

            # 如果指定了自定义headers或timeout，创建临时客户端
            if headers is not None or timeout is not None:
                # 合并headers
                merged_headers = dict(self.client.headers)
                if headers:
                    merged_headers.update(headers)

                # 使用指定的timeout或默认timeout
                client_timeout = timeout if timeout is not None else 300.0  # 设置为300秒，适应LLM模型调用时间

                async with httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=client_timeout,
                    headers=merged_headers
                ) as temp_client:
                    if raw_data is not None:
                        response = await temp_client.post(endpoint, content=raw_data)
                    else:
                        response = await temp_client.post(endpoint, json=data)
            else:
                if raw_data is not None:
                    response = await self.client.post(endpoint, content=raw_data)
                else:
                    response = await self.client.post(endpoint, json=data)

            response.raise_for_status()
            result = response.json()
            self.logger.info(f"🔍 BaseClient POST响应: status={response.status_code}, content_length={len(response.content)}")
            self.logger.info(f"🔍 BaseClient POST响应内容: {str(result)[:300]}...")
            return result
        except httpx.HTTPError as e:
            # 判断是否为连接错误或超时错误
            if isinstance(e, (httpx.ConnectError, httpx.TimeoutException)):
                self.logger.critical(f"🚨 严重告警: 目标服务不可达或超时 - {self.base_url}{endpoint}")
                self.logger.critical(f"🚨 错误类型: {type(e).__name__}, 详情: {str(e)}")
                self.logger.critical(f"🚨 请检查目标服务是否启动: {self.base_url}")
            else:
                self.logger.error(f"🔍 BaseClient POST {self.base_url}{endpoint} failed: {e}")
                self.logger.error(f"🔍 BaseClient 错误详情: {type(e).__name__}: {str(e)}")
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
