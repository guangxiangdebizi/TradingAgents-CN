"""
实时通信模块 - 提供WebSocket连接和实时更新功能
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
import uuid
import streamlit as st
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger("tradingagents.web.realtime_communication")

class MessageType(Enum):
    """消息类型"""
    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_PROGRESS = "analysis_progress"
    ANALYSIS_COMPLETED = "analysis_completed"
    ANALYSIS_ERROR = "analysis_error"
    WORKFLOW_STATUS = "workflow_status"
    SYSTEM_ALERT = "system_alert"
    HEARTBEAT = "heartbeat"

@dataclass
class RealtimeMessage:
    """实时消息"""
    message_id: str
    message_type: MessageType
    timestamp: datetime
    data: Dict[str, Any]
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class RealtimeManager:
    """实时通信管理器"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.message_queue: Dict[str, List[RealtimeMessage]] = {}
        self.subscribers: Dict[MessageType, Set[str]] = {}
        self.is_running = False
        
        # 初始化订阅者字典
        for msg_type in MessageType:
            self.subscribers[msg_type] = set()
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """创建新的会话"""
        session_id = str(uuid.uuid4())
        
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "subscriptions": set(),
            "message_count": 0
        }
        
        self.message_queue[session_id] = []
        
        logger.info(f"📱 创建实时会话: {session_id}")
        return session_id
    
    def close_session(self, session_id: str):
        """关闭会话"""
        if session_id in self.active_sessions:
            # 从所有订阅中移除
            for msg_type in MessageType:
                self.subscribers[msg_type].discard(session_id)
            
            # 清理会话数据
            del self.active_sessions[session_id]
            if session_id in self.message_queue:
                del self.message_queue[session_id]
            
            logger.info(f"📱 关闭实时会话: {session_id}")
    
    def subscribe(self, session_id: str, message_types: List[MessageType]):
        """订阅消息类型"""
        if session_id not in self.active_sessions:
            logger.warning(f"⚠️ 会话不存在: {session_id}")
            return False
        
        session = self.active_sessions[session_id]
        
        for msg_type in message_types:
            self.subscribers[msg_type].add(session_id)
            session["subscriptions"].add(msg_type)
        
        logger.info(f"📱 会话 {session_id} 订阅消息类型: {[t.value for t in message_types]}")
        return True
    
    def unsubscribe(self, session_id: str, message_types: List[MessageType]):
        """取消订阅消息类型"""
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        for msg_type in message_types:
            self.subscribers[msg_type].discard(session_id)
            session["subscriptions"].discard(msg_type)
        
        logger.info(f"📱 会话 {session_id} 取消订阅消息类型: {[t.value for t in message_types]}")
        return True
    
    def broadcast_message(self, message_type: MessageType, data: Dict[str, Any], target_sessions: Optional[List[str]] = None):
        """广播消息"""
        message = RealtimeMessage(
            message_id=str(uuid.uuid4()),
            message_type=message_type,
            timestamp=datetime.now(),
            data=data
        )
        
        # 确定目标会话
        if target_sessions:
            sessions = [s for s in target_sessions if s in self.active_sessions]
        else:
            sessions = list(self.subscribers[message_type])
        
        # 发送消息到目标会话
        for session_id in sessions:
            if session_id in self.message_queue:
                self.message_queue[session_id].append(message)
                self.active_sessions[session_id]["message_count"] += 1
                self.active_sessions[session_id]["last_activity"] = datetime.now()
        
        logger.info(f"📡 广播消息 {message_type.value} 到 {len(sessions)} 个会话")
    
    def send_message(self, session_id: str, message_type: MessageType, data: Dict[str, Any]):
        """发送消息到特定会话"""
        if session_id not in self.active_sessions:
            logger.warning(f"⚠️ 会话不存在: {session_id}")
            return False
        
        message = RealtimeMessage(
            message_id=str(uuid.uuid4()),
            message_type=message_type,
            timestamp=datetime.now(),
            data=data,
            session_id=session_id
        )
        
        self.message_queue[session_id].append(message)
        self.active_sessions[session_id]["message_count"] += 1
        self.active_sessions[session_id]["last_activity"] = datetime.now()
        
        logger.info(f"📨 发送消息 {message_type.value} 到会话 {session_id}")
        return True
    
    def get_messages(self, session_id: str, limit: int = 50) -> List[RealtimeMessage]:
        """获取会话消息"""
        if session_id not in self.message_queue:
            return []
        
        messages = self.message_queue[session_id]
        
        # 更新最后活动时间
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["last_activity"] = datetime.now()
        
        # 返回最新的消息
        return messages[-limit:] if len(messages) > limit else messages
    
    def clear_messages(self, session_id: str):
        """清空会话消息"""
        if session_id in self.message_queue:
            self.message_queue[session_id] = []
            logger.info(f"🗑️ 清空会话消息: {session_id}")
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id].copy()
        session["subscriptions"] = list(session["subscriptions"])
        session["created_at"] = session["created_at"].isoformat()
        session["last_activity"] = session["last_activity"].isoformat()
        
        return session
    
    def get_active_sessions_count(self) -> int:
        """获取活跃会话数量"""
        return len(self.active_sessions)
    
    def cleanup_inactive_sessions(self, timeout_minutes: int = 30):
        """清理不活跃的会话"""
        current_time = datetime.now()
        inactive_sessions = []
        
        for session_id, session in self.active_sessions.items():
            last_activity = session["last_activity"]
            if (current_time - last_activity).total_seconds() > timeout_minutes * 60:
                inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            self.close_session(session_id)
        
        if inactive_sessions:
            logger.info(f"🧹 清理了 {len(inactive_sessions)} 个不活跃会话")

# 全局实时管理器实例
_realtime_manager = None

def get_realtime_manager() -> RealtimeManager:
    """获取全局实时管理器实例"""
    global _realtime_manager
    if _realtime_manager is None:
        _realtime_manager = RealtimeManager()
    return _realtime_manager

class StreamlitRealtimeComponent:
    """Streamlit实时组件"""
    
    def __init__(self, session_id: Optional[str] = None):
        self.manager = get_realtime_manager()
        
        # 获取或创建会话ID
        if session_id:
            self.session_id = session_id
        else:
            # 从Streamlit会话状态获取或创建
            if "realtime_session_id" not in st.session_state:
                st.session_state.realtime_session_id = self.manager.create_session()
            self.session_id = st.session_state.realtime_session_id
        
        # 默认订阅所有消息类型
        self.manager.subscribe(self.session_id, list(MessageType))
    
    def display_realtime_updates(self, container=None):
        """显示实时更新"""
        if container is None:
            container = st.container()
        
        # 获取最新消息
        messages = self.manager.get_messages(self.session_id, limit=10)
        
        if messages:
            with container:
                st.subheader("🔔 实时更新")
                
                for message in reversed(messages[-5:]):  # 显示最新5条消息
                    self._display_message(message)
    
    def _display_message(self, message: RealtimeMessage):
        """显示单条消息"""
        timestamp = message.timestamp.strftime("%H:%M:%S")
        
        if message.message_type == MessageType.ANALYSIS_STARTED:
            st.info(f"🚀 [{timestamp}] 开始分析: {message.data.get('symbol', 'Unknown')}")
        
        elif message.message_type == MessageType.ANALYSIS_PROGRESS:
            progress = message.data.get('progress', 0)
            step = message.data.get('step', 'Unknown')
            st.info(f"⏳ [{timestamp}] 分析进度: {step} ({progress}%)")
        
        elif message.message_type == MessageType.ANALYSIS_COMPLETED:
            symbol = message.data.get('symbol', 'Unknown')
            duration = message.data.get('duration', 0)
            st.success(f"✅ [{timestamp}] 分析完成: {symbol} (耗时: {duration:.1f}s)")
        
        elif message.message_type == MessageType.ANALYSIS_ERROR:
            error = message.data.get('error', 'Unknown error')
            st.error(f"❌ [{timestamp}] 分析失败: {error}")
        
        elif message.message_type == MessageType.WORKFLOW_STATUS:
            status = message.data.get('status', 'Unknown')
            st.info(f"📊 [{timestamp}] 工作流状态: {status}")
        
        elif message.message_type == MessageType.SYSTEM_ALERT:
            level = message.data.get('level', 'info')
            alert_message = message.data.get('message', 'System alert')
            
            if level == 'error':
                st.error(f"🚨 [{timestamp}] {alert_message}")
            elif level == 'warning':
                st.warning(f"⚠️ [{timestamp}] {alert_message}")
            else:
                st.info(f"ℹ️ [{timestamp}] {alert_message}")
    
    def send_analysis_started(self, symbol: str, analysis_type: str = "complete"):
        """发送分析开始消息"""
        self.manager.send_message(
            self.session_id,
            MessageType.ANALYSIS_STARTED,
            {
                "symbol": symbol,
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def send_analysis_progress(self, symbol: str, step: str, progress: float):
        """发送分析进度消息"""
        self.manager.send_message(
            self.session_id,
            MessageType.ANALYSIS_PROGRESS,
            {
                "symbol": symbol,
                "step": step,
                "progress": progress,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def send_analysis_completed(self, symbol: str, duration: float, result_summary: str = ""):
        """发送分析完成消息"""
        self.manager.send_message(
            self.session_id,
            MessageType.ANALYSIS_COMPLETED,
            {
                "symbol": symbol,
                "duration": duration,
                "result_summary": result_summary,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def send_analysis_error(self, symbol: str, error: str):
        """发送分析错误消息"""
        self.manager.send_message(
            self.session_id,
            MessageType.ANALYSIS_ERROR,
            {
                "symbol": symbol,
                "error": error,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'session_id'):
            self.manager.close_session(self.session_id)

def create_realtime_component() -> StreamlitRealtimeComponent:
    """创建Streamlit实时组件"""
    return StreamlitRealtimeComponent()

# 实时更新装饰器
def realtime_update(message_type: MessageType):
    """实时更新装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            manager = get_realtime_manager()
            
            # 执行函数
            try:
                result = func(*args, **kwargs)
                
                # 发送成功消息
                if message_type == MessageType.ANALYSIS_COMPLETED:
                    manager.broadcast_message(
                        message_type,
                        {
                            "function": func.__name__,
                            "status": "success",
                            "result": str(result)[:200],  # 限制长度
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                
                return result
                
            except Exception as e:
                # 发送错误消息
                manager.broadcast_message(
                    MessageType.ANALYSIS_ERROR,
                    {
                        "function": func.__name__,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                )
                raise
        
        return wrapper
    return decorator
