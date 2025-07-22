"""
状态管理器
负责管理智能体和任务的状态持久化和同步
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import asdict

from backend.shared.logging_config import get_logger
from backend.shared.database import DatabaseManager
from backend.shared.redis_client import RedisClient

logger = get_logger("agent-service.state_manager")


class StateManager:
    """状态管理器"""
    
    def __init__(self, db_manager: DatabaseManager, redis_client: RedisClient):
        self.db_manager = db_manager
        self.redis_client = redis_client
        
        # 状态缓存
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self.task_states: Dict[str, Dict[str, Any]] = {}
        self.workflow_states: Dict[str, Dict[str, Any]] = {}
        
        # 状态同步任务
        self.sync_task: Optional[asyncio.Task] = None
        self.sync_interval = 30  # 秒
        
        # 状态变更监听器
        self.state_listeners: Dict[str, List[callable]] = {
            "agent": [],
            "task": [],
            "workflow": []
        }
        
        logger.info("🏗️ 状态管理器初始化")
    
    async def initialize(self):
        """初始化状态管理器"""
        try:
            # 从数据库加载状态
            await self._load_states_from_db()
            
            # 启动状态同步任务
            self.sync_task = asyncio.create_task(self._sync_states_loop())
            
            logger.info("✅ 状态管理器初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 状态管理器初始化失败: {e}")
            raise
    
    async def _load_states_from_db(self):
        """从数据库加载状态"""
        try:
            if not self.db_manager.is_mongodb_available():
                logger.warning("⚠️ MongoDB不可用，跳过状态加载")
                return
            
            # 加载智能体状态
            agents_collection = self.db_manager.get_collection("agent_states")
            async for agent_state in agents_collection.find({}):
                agent_id = agent_state.get("agent_id")
                if agent_id:
                    self.agent_states[agent_id] = agent_state
            
            # 加载任务状态
            tasks_collection = self.db_manager.get_collection("task_states")
            async for task_state in tasks_collection.find({}):
                task_id = task_state.get("task_id")
                if task_id:
                    self.task_states[task_id] = task_state
            
            # 加载工作流状态
            workflows_collection = self.db_manager.get_collection("workflow_states")
            async for workflow_state in workflows_collection.find({}):
                workflow_id = workflow_state.get("workflow_id")
                if workflow_id:
                    self.workflow_states[workflow_id] = workflow_state
            
            logger.info(f"📥 从数据库加载状态: {len(self.agent_states)}个智能体, {len(self.task_states)}个任务, {len(self.workflow_states)}个工作流")
            
        except Exception as e:
            logger.error(f"❌ 从数据库加载状态失败: {e}")
    
    async def save_agent_state(self, agent_id: str, state: Dict[str, Any]):
        """保存智能体状态"""
        try:
            # 添加时间戳
            state["last_updated"] = datetime.now().isoformat()
            
            # 更新内存缓存
            self.agent_states[agent_id] = state
            
            # 保存到Redis
            await self._save_to_redis(f"agent_state:{agent_id}", state)
            
            # 通知监听器
            await self._notify_listeners("agent", agent_id, state)
            
            logger.debug(f"💾 保存智能体状态: {agent_id}")
            
        except Exception as e:
            logger.error(f"❌ 保存智能体状态失败: {agent_id} - {e}")
    
    async def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取智能体状态"""
        try:
            # 先从内存缓存获取
            if agent_id in self.agent_states:
                return self.agent_states[agent_id]
            
            # 从Redis获取
            state = await self._get_from_redis(f"agent_state:{agent_id}")
            if state:
                self.agent_states[agent_id] = state
                return state
            
            # 从数据库获取
            if self.db_manager.is_mongodb_available():
                collection = self.db_manager.get_collection("agent_states")
                state = await collection.find_one({"agent_id": agent_id})
                if state:
                    # 移除MongoDB的_id字段
                    state.pop("_id", None)
                    self.agent_states[agent_id] = state
                    return state
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取智能体状态失败: {agent_id} - {e}")
            return None
    
    async def save_task_state(self, task_id: str, state: Dict[str, Any]):
        """保存任务状态"""
        try:
            # 添加时间戳
            state["last_updated"] = datetime.now().isoformat()
            
            # 更新内存缓存
            self.task_states[task_id] = state
            
            # 保存到Redis
            await self._save_to_redis(f"task_state:{task_id}", state)
            
            # 通知监听器
            await self._notify_listeners("task", task_id, state)
            
            logger.debug(f"💾 保存任务状态: {task_id}")
            
        except Exception as e:
            logger.error(f"❌ 保存任务状态失败: {task_id} - {e}")
    
    async def get_task_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        try:
            # 先从内存缓存获取
            if task_id in self.task_states:
                return self.task_states[task_id]
            
            # 从Redis获取
            state = await self._get_from_redis(f"task_state:{task_id}")
            if state:
                self.task_states[task_id] = state
                return state
            
            # 从数据库获取
            if self.db_manager.is_mongodb_available():
                collection = self.db_manager.get_collection("task_states")
                state = await collection.find_one({"task_id": task_id})
                if state:
                    # 移除MongoDB的_id字段
                    state.pop("_id", None)
                    self.task_states[task_id] = state
                    return state
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取任务状态失败: {task_id} - {e}")
            return None
    
    async def save_workflow_state(self, workflow_id: str, state: Dict[str, Any]):
        """保存工作流状态"""
        try:
            # 添加时间戳
            state["last_updated"] = datetime.now().isoformat()
            
            # 更新内存缓存
            self.workflow_states[workflow_id] = state
            
            # 保存到Redis
            await self._save_to_redis(f"workflow_state:{workflow_id}", state)
            
            # 通知监听器
            await self._notify_listeners("workflow", workflow_id, state)
            
            logger.debug(f"💾 保存工作流状态: {workflow_id}")
            
        except Exception as e:
            logger.error(f"❌ 保存工作流状态失败: {workflow_id} - {e}")
    
    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """获取工作流状态"""
        try:
            # 先从内存缓存获取
            if workflow_id in self.workflow_states:
                return self.workflow_states[workflow_id]
            
            # 从Redis获取
            state = await self._get_from_redis(f"workflow_state:{workflow_id}")
            if state:
                self.workflow_states[workflow_id] = state
                return state
            
            # 从数据库获取
            if self.db_manager.is_mongodb_available():
                collection = self.db_manager.get_collection("workflow_states")
                state = await collection.find_one({"workflow_id": workflow_id})
                if state:
                    # 移除MongoDB的_id字段
                    state.pop("_id", None)
                    self.workflow_states[workflow_id] = state
                    return state
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 获取工作流状态失败: {workflow_id} - {e}")
            return None
    
    async def delete_state(self, state_type: str, state_id: str):
        """删除状态"""
        try:
            # 从内存缓存删除
            if state_type == "agent" and state_id in self.agent_states:
                del self.agent_states[state_id]
            elif state_type == "task" and state_id in self.task_states:
                del self.task_states[state_id]
            elif state_type == "workflow" and state_id in self.workflow_states:
                del self.workflow_states[state_id]
            
            # 从Redis删除
            await self.redis_client.delete(f"{state_type}_state:{state_id}")
            
            # 从数据库删除
            if self.db_manager.is_mongodb_available():
                collection = self.db_manager.get_collection(f"{state_type}_states")
                await collection.delete_one({f"{state_type}_id": state_id})
            
            logger.debug(f"🗑️ 删除状态: {state_type}:{state_id}")
            
        except Exception as e:
            logger.error(f"❌ 删除状态失败: {state_type}:{state_id} - {e}")
    
    async def get_states_by_filter(self, state_type: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据过滤条件获取状态"""
        try:
            states = []
            
            # 选择对应的状态缓存
            if state_type == "agent":
                state_cache = self.agent_states
            elif state_type == "task":
                state_cache = self.task_states
            elif state_type == "workflow":
                state_cache = self.workflow_states
            else:
                return states
            
            # 从内存缓存过滤
            for state_id, state in state_cache.items():
                if self._match_filters(state, filters):
                    states.append(state)
            
            # 如果内存缓存结果不足，从数据库查询
            if len(states) < filters.get("limit", 100) and self.db_manager.is_mongodb_available():
                collection = self.db_manager.get_collection(f"{state_type}_states")
                async for state in collection.find(filters):
                    state.pop("_id", None)
                    states.append(state)
            
            return states
            
        except Exception as e:
            logger.error(f"❌ 根据过滤条件获取状态失败: {state_type} - {e}")
            return []
    
    def add_state_listener(self, state_type: str, listener: callable):
        """添加状态变更监听器"""
        if state_type in self.state_listeners:
            self.state_listeners[state_type].append(listener)
            logger.debug(f"📡 添加状态监听器: {state_type}")
    
    def remove_state_listener(self, state_type: str, listener: callable):
        """移除状态变更监听器"""
        if state_type in self.state_listeners and listener in self.state_listeners[state_type]:
            self.state_listeners[state_type].remove(listener)
            logger.debug(f"📡 移除状态监听器: {state_type}")
    
    async def _notify_listeners(self, state_type: str, state_id: str, state: Dict[str, Any]):
        """通知状态变更监听器"""
        try:
            for listener in self.state_listeners.get(state_type, []):
                try:
                    if asyncio.iscoroutinefunction(listener):
                        await listener(state_id, state)
                    else:
                        listener(state_id, state)
                except Exception as e:
                    logger.error(f"❌ 状态监听器执行失败: {e}")
        except Exception as e:
            logger.error(f"❌ 通知状态监听器失败: {e}")
    
    async def _save_to_redis(self, key: str, data: Dict[str, Any]):
        """保存到Redis"""
        try:
            await self.redis_client.set(key, json.dumps(data, default=str), ex=3600)  # 1小时过期
        except Exception as e:
            logger.error(f"❌ 保存到Redis失败: {key} - {e}")
    
    async def _get_from_redis(self, key: str) -> Optional[Dict[str, Any]]:
        """从Redis获取"""
        try:
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"❌ 从Redis获取失败: {key} - {e}")
            return None
    
    def _match_filters(self, state: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """检查状态是否匹配过滤条件"""
        try:
            for key, value in filters.items():
                if key in ["limit", "offset"]:
                    continue
                
                if key not in state:
                    return False
                
                if isinstance(value, list):
                    if state[key] not in value:
                        return False
                elif state[key] != value:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 过滤条件匹配失败: {e}")
            return False
    
    async def _sync_states_loop(self):
        """状态同步循环"""
        while True:
            try:
                await asyncio.sleep(self.sync_interval)
                await self._sync_states_to_db()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ 状态同步循环错误: {e}")
    
    async def _sync_states_to_db(self):
        """同步状态到数据库"""
        try:
            if not self.db_manager.is_mongodb_available():
                return
            
            # 同步智能体状态
            if self.agent_states:
                collection = self.db_manager.get_collection("agent_states")
                for agent_id, state in self.agent_states.items():
                    await collection.replace_one(
                        {"agent_id": agent_id},
                        state,
                        upsert=True
                    )
            
            # 同步任务状态
            if self.task_states:
                collection = self.db_manager.get_collection("task_states")
                for task_id, state in self.task_states.items():
                    await collection.replace_one(
                        {"task_id": task_id},
                        state,
                        upsert=True
                    )
            
            # 同步工作流状态
            if self.workflow_states:
                collection = self.db_manager.get_collection("workflow_states")
                for workflow_id, state in self.workflow_states.items():
                    await collection.replace_one(
                        {"workflow_id": workflow_id},
                        state,
                        upsert=True
                    )
            
            logger.debug("💾 状态同步到数据库完成")
            
        except Exception as e:
            logger.error(f"❌ 状态同步到数据库失败: {e}")
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 检查Redis连接
            await self.redis_client.ping()
            
            # 检查数据库连接
            if self.db_manager.is_mongodb_available():
                await self.db_manager.get_collection("health_check").find_one({})
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 状态管理器健康检查失败: {e}")
            return False
    
    async def cleanup(self):
        """清理资源"""
        try:
            # 取消同步任务
            if self.sync_task:
                self.sync_task.cancel()
                try:
                    await self.sync_task
                except asyncio.CancelledError:
                    pass
            
            # 最后一次同步到数据库
            await self._sync_states_to_db()
            
            # 清理内存缓存
            self.agent_states.clear()
            self.task_states.clear()
            self.workflow_states.clear()
            
            logger.info("✅ 状态管理器清理完成")
            
        except Exception as e:
            logger.error(f"❌ 状态管理器清理失败: {e}")
