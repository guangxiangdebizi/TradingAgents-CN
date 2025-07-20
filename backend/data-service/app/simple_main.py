#!/usr/bin/env python3
"""
简化版 Data Service - 快速启动，避免启动时的复杂初始化
"""

import os
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 基础配置
app = FastAPI(
    title="TradingAgents Data Service",
    description="数据服务 - 快速启动版本",
    version="1.0.0"
)

# CORS 配置
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
        "service": "TradingAgents Data Service (Simple)",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "data-service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "dependencies": {
            "mongodb": "connected",
            "redis": "connected"
        }
    }

@app.get("/api/stock/info/{symbol}")
async def get_stock_info(symbol: str):
    """获取股票基本信息"""
    try:
        # 模拟股票信息
        stock_info = {
            "symbol": symbol.upper(),
            "name": f"测试股票 {symbol}",
            "market": "A股" if symbol.isdigit() else "美股",
            "current_price": 100.50,
            "change": 2.30,
            "change_percent": 2.34,
            "volume": 1000000,
            "market_cap": 50000000000,
            "pe_ratio": 15.6,
            "pb_ratio": 2.1,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": "获取股票信息成功",
            "data": stock_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票信息失败: {str(e)}")

@app.get("/api/stock/data/{symbol}")
async def get_stock_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取股票历史数据"""
    try:
        # 模拟历史数据
        stock_data = {
            "symbol": symbol.upper(),
            "start_date": start_date or "2024-01-01",
            "end_date": end_date or datetime.now().strftime('%Y-%m-%d'),
            "data": [
                {
                    "date": "2024-07-20",
                    "open": 98.50,
                    "high": 102.30,
                    "low": 97.80,
                    "close": 100.50,
                    "volume": 1000000
                },
                {
                    "date": "2024-07-19",
                    "open": 96.20,
                    "high": 99.10,
                    "low": 95.50,
                    "close": 98.20,
                    "volume": 850000
                }
            ],
            "total_records": 2
        }
        
        return {
            "success": True,
            "message": "获取股票数据成功",
            "data": stock_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票数据失败: {str(e)}")

@app.get("/api/stock/fundamentals/{symbol}")
async def get_stock_fundamentals(symbol: str):
    """获取股票基本面数据"""
    try:
        # 模拟基本面数据
        fundamentals = {
            "symbol": symbol.upper(),
            "company_name": f"测试公司 {symbol}",
            "industry": "科技",
            "sector": "信息技术",
            "market_cap": 50000000000,
            "pe_ratio": 15.6,
            "pb_ratio": 2.1,
            "roe": 18.5,
            "debt_to_equity": 0.3,
            "revenue_growth": 12.5,
            "profit_margin": 22.3,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": "获取基本面数据成功",
            "data": fundamentals,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取基本面数据失败: {str(e)}")

@app.get("/api/stock/news/{symbol}")
async def get_stock_news(symbol: str):
    """获取股票新闻"""
    try:
        # 模拟新闻数据
        news = {
            "symbol": symbol.upper(),
            "news": [
                {
                    "title": f"{symbol} 公司发布季度财报",
                    "summary": "公司业绩超预期，营收增长显著",
                    "source": "财经新闻",
                    "published_at": datetime.now().isoformat(),
                    "sentiment": "positive"
                },
                {
                    "title": f"{symbol} 获得新订单",
                    "summary": "公司获得重要客户大额订单",
                    "source": "行业资讯",
                    "published_at": datetime.now().isoformat(),
                    "sentiment": "positive"
                }
            ],
            "total_count": 2
        }
        
        return {
            "success": True,
            "message": "获取股票新闻成功",
            "data": news,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票新闻失败: {str(e)}")

@app.get("/api/config/status")
async def get_config_status():
    """获取配置状态"""
    return {
        "success": True,
        "message": "配置状态正常",
        "data": {
            "data_sources": {
                "tushare": "configured",
                "akshare": "available",
                "finnhub": "configured"
            },
            "llm_models": {
                "dashscope": "configured",
                "deepseek": "configured"
            },
            "databases": {
                "mongodb": "connected",
                "redis": "connected"
            }
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/test/connection")
async def test_connection():
    """测试连接"""
    return {
        "success": True,
        "message": "连接测试成功",
        "data": {
            "service": "data-service",
            "status": "running",
            "endpoints": [
                "/health",
                "/api/stock/info/{symbol}",
                "/api/stock/data/{symbol}",
                "/api/stock/fundamentals/{symbol}",
                "/api/stock/news/{symbol}",
                "/api/config/status"
            ]
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 启动简化版 Data Service...")
    print("📍 服务地址: http://localhost:8002")
    print("📚 API 文档: http://localhost:8002/docs")
    print("🔍 健康检查: http://localhost:8002/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
