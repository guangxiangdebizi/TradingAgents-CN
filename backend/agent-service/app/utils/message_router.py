"""
消息路由器
负责智能体间的消息传递和通信协调
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from backend.shared.logging_config import get_logger
from backend.shared.redis_client import RedisClient

logger = get_logger("agent-service.message_router")


class MessageType(Enum):
    """消息类型枚举"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    COLLABORATION_REQUEST = "collaboration_request"
    COLLABORATION_RESPONSE = "collaboration_response"
    DEBATE_MESSAGE = "debate_message"
    CONSENSUS_UPDATE = "consensus_update"
    STATUS_UPDATE = "status_update"
    ERROR_NOTIFICATION = "error_notification"
    HEARTBEAT = "heartbeat"


class MessagePriority(Enum):
    """消息优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Message:
    """消息数据类"""
    message_id: str
    message_type: MessageType
    sender_id: str
    receiver_id: str
    content: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = None
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """从字典创建"""
        return cls(
            message_id=data["message_id"],
            message_type=MessageType(data["message_type"]),
            sender_id=data["sender_id"],
            receiver_id=data["receiver_id"],
            content=data["content"],
            priority=MessagePriority(data["priority"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3)
        )


class MessageRouter:
    """消息路由器"""
    
    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client
        
        # 消息队列
        self.message_queues: Dict[str, List[Message]] = {}
        
        # 消息处理器
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        
        # 订阅者
        self.subscribers: Dict[str, List[str]] = {}  # topic -> [agent_ids]
        
        # 消息统计
        self.message_stats = {
            "sent": 0,
            "received": 0,
            "failed": 0,
            "retried": 0
        }
        
        # 消息处理任务
        self.processing_task: Optional[asyncio.Task] = None
        self.processing_interval = 0.1  # 秒
        
        logger.info("🏗️ 消息路由器初始化")
    
    async def initialize(self):
        """初始化消息路由器"""
        try:
            # 启动消息处理任务
            self.processing_task = asyncio.create_task(self._process_messages_loop())
            
            # 设置Redis订阅
            await self._setup_redis_subscriptions()
            
            logger.info("✅ 消息路由器初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 消息路由器初始化失败: {e}")
            raise
    
    async def send_message(
        self,
        message_type: MessageType,
        sender_id: str,
        receiver_id: str,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        expires_at: Optional[datetime] = None
    ) -> str:
        """发送消息"""
        try:
            # 创建消息
            message = Message(
                message_id=f"{sender_id}_{receiver_id}_{datetime.now().timestamp()}",
                message_type=message_type,
                sender_id=sender_id,
                receiver_id=receiver_id,
                content=content,
                priority=priority,
                expires_at=expires_at
            )
            
            # 添加到队列
            await self._add_to_queue(message)
            
            # 发布到Redis
            await self._publish_to_redis(message)
            
            self.message_stats["sent"] += 1
            
            logger.debug(f"📤 发送消息: {message.message_id} ({sender_id} -> {receiver_id})")
            
            return message.message_id
            
        except Exception as e:
            logger.error(f"❌ 发送消息失败: {e}")
            self.message_stats["failed"] += 1
            raise
    
    async def broadcast_message(
        self,
        message_type: MessageType,
        sender_id: str,
        topic: str,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> List[str]:
        """广播消息"""
        try:
            message_ids = []
            
            # 获取订阅者
            subscribers = self.subscribers.get(topic, [])
            
            # 向每个订阅者发送消息
            for subscriber_id in subscribers:
                if subscriber_id != sender_id:  # 不发送给自己
                    message_id = await self.send_message(
                        message_type=message_type,
                        sender_id=sender_id,
                        receiver_id=subscriber_id,
                        content=content,
                        priority=priority
                    )
                    message_ids.append(message_id)
            
            logger.debug(f"📡 广播消息: {topic} -> {len(message_ids)}个接收者")
            
            return message_ids
            
        except Exception as e:
            logger.error(f"❌ 广播消息失败: {e}")
            raise
    
    async def subscribe(self, agent_id: str, topic: str):
        """订阅主题"""
        try:
            if topic not in self.subscribers:
                self.subscribers[topic] = []
            
            if agent_id not in self.subscribers[topic]:
                self.subscribers[topic].append(agent_id)
                
                # 在Redis中记录订阅关系
                await self.redis_client.sadd(f"subscribers:{topic}", agent_id)
                
                logger.debug(f"📡 订阅主题: {agent_id} -> {topic}")
            
        except Exception as e:
            logger.error(f"❌ 订阅主题失败: {agent_id} -> {topic} - {e}")
    
    async def unsubscribe(self, agent_id: str, topic: str):
        """取消订阅主题"""
        try:
            if topic in self.subscribers and agent_id in self.subscribers[topic]:
                self.subscribers[topic].remove(agent_id)
                
                # 从Redis中移除订阅关系
                await self.redis_client.srem(f"subscribers:{topic}", agent_id)
                
                logger.debug(f"📡 取消订阅: {agent_id} -> {topic}")
            
        except Exception as e:
            logger.error(f"❌ 取消订阅失败: {agent_id} -> {topic} - {e}")
    
    async def get_messages(self, agent_id: str, limit: int = 10) -> List[Message]:
        """获取智能体的消息"""
        try:
            messages = []
            
            # 从本地队列获取
            if agent_id in self.message_queues:
                messages.extend(self.message_queues[agent_id][:limit])
                # 移除已获取的消息
                self.message_queues[agent_id] = self.message_queues[agent_id][limit:]
            
            # 从Redis获取
            redis_messages = await self._get_from_redis_queue(agent_id, limit - len(messages))
            messages.extend(redis_messages)
            
            self.message_stats["received"] += len(messages)
            
            logger.debug(f"📥 获取消息: {agent_id} -> {len(messages)}条")
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ 获取消息失败: {agent_id} - {e}")
            return []
    
    async def add_message_handler(self, message_type: MessageType, handler: Callable):
        """添加消息处理器"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        
        self.message_handlers[message_type].append(handler)
        logger.debug(f"📝 添加消息处理器: {message_type.value}")
    
    async def remove_message_handler(self, message_type: MessageType, handler: Callable):
        """移除消息处理器"""
        if message_type in self.message_handlers and handler in self.message_handlers[message_type]:
            self.message_handlers[message_type].remove(handler)
            logger.debug(f"📝 移除消息处理器: {message_type.value}")
    
    async def _add_to_queue(self, message: Message):
        """添加消息到队列"""
        try:
            receiver_id = message.receiver_id
            
            if receiver_id not in self.message_queues:
                self.message_queues[receiver_id] = []
            
            # 按优先级插入
            inserted = False
            for i, existing_message in enumerate(self.message_queues[receiver_id]):
                if message.priority.value > existing_message.priority.value:
                    self.message_queues[receiver_id].insert(i, message)
                    inserted = True
                    break
            
            if not inserted:
                self.message_queues[receiver_id].append(message)
            
        except Exception as e:
            logger.error(f"❌ 添加消息到队列失败: {e}")
    
    async def _publish_to_redis(self, message: Message):
        """发布消息到Redis"""
        try:
            # 发布到接收者的频道
            channel = f"agent_messages:{message.receiver_id}"
            await self.redis_client.publish(channel, json.dumps(message.to_dict(), default=str))
            
            # 同时添加到Redis队列（持久化）
            queue_key = f"message_queue:{message.receiver_id}"
            await self.redis_client.lpush(queue_key, json.dumps(message.to_dict(), default=str))
            await self.redis_client.expire(queue_key, 3600)  # 1小时过期
            
        except Exception as e:
            logger.error(f"❌ 发布消息到Redis失败: {e}")
    
    async def _get_from_redis_queue(self, agent_id: str, limit: int) -> List[Message]:
        """从Redis队列获取消息"""
        try:
            messages = []
            queue_key = f"message_queue:{agent_id}"
            
            for _ in range(limit):
                message_data = await self.redis_client.rpop(queue_key)
                if not message_data:
                    break
                
                try:
                    message_dict = json.loads(message_data)
                    message = Message.from_dict(message_dict)
                    messages.append(message)
                except Exception as e:
                    logger.error(f"❌ 解析Redis消息失败: {e}")
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ 从Redis队列获取消息失败: {e}")
            return []
    
    async def _setup_redis_subscriptions(self):
        """设置Redis订阅"""
        try:
            # 这里可以设置Redis的pub/sub订阅
            # 由于Redis客户端的具体实现可能不同，这里先留空
            pass
        except Exception as e:
            logger.error(f"❌ 设置Redis订阅失败: {e}")
    
    async def _process_messages_loop(self):
        """消息处理循环"""
        while True:
            try:
                await asyncio.sleep(self.processing_interval)
                await self._process_pending_messages()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 消息处理循环错误: {e}")
    
    async def _process_pending_messages(self):
        """处理待处理的消息"""
        try:
            # 处理本地队列中的消息
            for agent_id, messages in self.message_queues.items():
                for message in messages[:]:  # 复制列表避免修改时出错
                    # 检查消息是否过期
                    if message.expires_at and datetime.now() > message.expires_at:
                        messages.remove(message)
                        continue
                    
                    # 调用消息处理器
                    await self._handle_message(message)
            
        except Exception as e:
            logger.error(f"❌ 处理待处理消息失败: {e}")
    
    async def _handle_message(self, message: Message):
        """处理单个消息"""
        try:
            handlers = self.message_handlers.get(message.message_type, [])
            
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(message)
                    else:
                        handler(message)
                except Exception as e:
                    logger.error(f"❌ 消息处理器执行失败: {e}")
            
        except Exception as e:
            logger.error(f"❌ 处理消息失败: {e}")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取消息统计"""
        return {
            "message_stats": self.message_stats.copy(),
            "queue_sizes": {agent_id: len(messages) for agent_id, messages in self.message_queues.items()},
            "subscribers": {topic: len(agents) for topic, agents in self.subscribers.items()},
            "handlers": {msg_type.value: len(handlers) for msg_type, handlers in self.message_handlers.items()},
            "timestamp": datetime.now().isoformat()
        }
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 检查Redis连接
            await self.redis_client.ping()
            
            # 检查处理任务状态
            if self.processing_task and self.processing_task.done():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 消息路由器健康检查失败: {e}")
            return False
    
    async def cleanup(self):
        """清理资源"""
        try:
            # 取消处理任务
            if self.processing_task:
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass
            
            # 清理消息队列
            self.message_queues.clear()
            self.message_handlers.clear()
            self.subscribers.clear()
            
            logger.info("✅ 消息路由器清理完成")
            
        except Exception as e:
            logger.error(f"❌ 消息路由器清理失败: {e}")
