"""
Redis客户端模块
"""

import redis.asyncio as redis
from typing import Optional, Any, Dict, List, Union
from .utils.logger import get_service_logger
from .utils.config import get_service_config

logger = get_service_logger("redis-client")


class RedisClient:
    """Redis客户端封装"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or "redis://localhost:6379/0"
        self.client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """连接到Redis"""
        try:
            self.client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # 测试连接
            await self.client.ping()
            self._connected = True
            
            logger.info("✅ Redis 连接成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ Redis 连接失败: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """断开Redis连接"""
        if self.client:
            await self.client.close()
            self._connected = False
            logger.info("🔌 Redis 连接已断开")
    
    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """设置键值"""
        if not self._connected or not self.client:
            logger.error("❌ Redis未连接")
            return False
        
        try:
            await self.client.set(key, value, ex=ex)
            return True
        except Exception as e:
            logger.error(f"❌ Redis set失败: {e}")
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """获取值"""
        if not self._connected or not self.client:
            logger.error("❌ Redis未连接")
            return None
        
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.error(f"❌ Redis get失败: {e}")
            return None
    
    async def delete(self, *keys: str) -> int:
        """删除键"""
        if not self._connected or not self.client:
            logger.error("❌ Redis未连接")
            return 0
        
        try:
            return await self.client.delete(*keys)
        except Exception as e:
            logger.error(f"❌ Redis delete失败: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self._connected or not self.client:
            logger.error("❌ Redis未连接")
            return False
        
        try:
            return bool(await self.client.exists(key))
        except Exception as e:
            logger.error(f"❌ Redis exists失败: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        if not self._connected or not self.client:
            logger.error("❌ Redis未连接")
            return False
        
        try:
            return await self.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"❌ Redis expire失败: {e}")
            return False
    
    async def hset(self, name: str, mapping: Dict[str, Any]) -> int:
        """设置哈希表"""
        if not self._connected or not self.client:
            logger.error("❌ Redis未连接")
            return 0
        
        try:
            return await self.client.hset(name, mapping=mapping)
        except Exception as e:
            logger.error(f"❌ Redis hset失败: {e}")
            return 0
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """获取哈希表值"""
        if not self._connected or not self.client:
            logger.error("❌ Redis未连接")
            return None
        
        try:
            return await self.client.hget(name, key)
        except Exception as e:
            logger.error(f"❌ Redis hget失败: {e}")
            return None
    
    async def hgetall(self, name: str) -> Dict[str, str]:
        """获取整个哈希表"""
        if not self._connected or not self.client:
            logger.error("❌ Redis未连接")
            return {}
        
        try:
            return await self.client.hgetall(name)
        except Exception as e:
            logger.error(f"❌ Redis hgetall失败: {e}")
            return {}
    
    async def lpush(self, name: str, *values: Any) -> int:
        """列表左推"""
        if not self._connected or not self.client:
            logger.error("❌ Redis未连接")
            return 0
        
        try:
            return await self.client.lpush(name, *values)
        except Exception as e:
            logger.error(f"❌ Redis lpush失败: {e}")
            return 0
    
    async def rpop(self, name: str) -> Optional[str]:
        """列表右弹"""
        if not self._connected or not self.client:
            logger.error("❌ Redis未连接")
            return None
        
        try:
            return await self.client.rpop(name)
        except Exception as e:
            logger.error(f"❌ Redis rpop失败: {e}")
            return None
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.client:
                return False
            await self.client.ping()
            return True
        except Exception as e:
            logger.error(f"❌ Redis健康检查失败: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected


# 全局Redis客户端实例
_redis_client: Optional[RedisClient] = None


def get_redis_client(redis_url: Optional[str] = None) -> RedisClient:
    """获取Redis客户端实例"""
    global _redis_client
    
    if _redis_client is None:
        if not redis_url:
            config = get_service_config("redis")
            redis_url = config.get('redis_url', 'redis://localhost:6379/0')
        _redis_client = RedisClient(redis_url)
    
    return _redis_client


async def init_redis_client(redis_url: Optional[str] = None) -> RedisClient:
    """初始化Redis客户端"""
    client = get_redis_client(redis_url)
    await client.connect()
    return client
