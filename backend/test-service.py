#!/usr/bin/env python3
"""
简单的测试服务，验证基础环境是否正常
"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(title="Test Service", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Test service is running!"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "test-service",
        "version": "1.0.0",
        "environment": {
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
            "MONGODB_URL": os.environ.get("MONGODB_URL", ""),
            "REDIS_URL": os.environ.get("REDIS_URL", "")
        }
    }

@app.get("/env")
async def env():
    """显示环境变量"""
    return dict(os.environ)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
