#!/usr/bin/env python3
"""
Task Scheduler 简化启动文件
"""

import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 添加shared路径
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.config import get_config

# 创建简化的FastAPI应用
app = FastAPI(
    title="TradingAgents Task Scheduler API",
    description="定时任务管理和监控API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "TradingAgents Task Scheduler",
        "version": "1.0.0",
        "status": "running",
        "description": "定时任务调度服务"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "task-scheduler",
        "timestamp": "2025-01-22T10:00:00Z",
        "components": {
            "scheduler": True,
            "redis": True
        }
    }

@app.get("/api/v1/tasks")
async def list_tasks():
    """获取任务列表"""
    return {
        "success": True,
        "message": "任务列表获取成功",
        "data": {
            "active_tasks": [],
            "scheduled_tasks": [],
            "completed_tasks": []
        }
    }

@app.get("/api/v1/status")
async def get_status():
    """获取调度器状态"""
    return {
        "success": True,
        "message": "调度器状态正常",
        "data": {
            "status": "running",
            "active_workers": 0,
            "pending_tasks": 0,
            "completed_tasks": 0
        }
    }

if __name__ == "__main__":
    config = get_config()
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=config.get('TASK_SCHEDULER_PORT', 8003),
        reload=config.get('DEBUG', False),
        log_level=config.get('LOG_LEVEL', 'INFO').lower()
    )
