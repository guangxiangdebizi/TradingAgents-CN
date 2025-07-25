#!/usr/bin/env python3
"""
独立分析器 - 不依赖TradingAgents主系统
通过API调用获取数据和分析结果
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class IndependentAnalyzer:
    """
    独立分析器
    通过微服务API调用实现分析功能，不直接依赖TradingAgents
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.data_service_url = self.config.get("data_service_url", "http://localhost:8002")
        self.tradingagents_api_url = self.config.get("tradingagents_api_url", "http://localhost:8000")
        
    async def analyze_stock(self, symbol: str, trade_date: str = None) -> Dict[str, Any]:
        """
        分析股票 - 通过API调用实现
        
        Args:
            symbol: 股票代码
            trade_date: 交易日期
            
        Returns:
            分析结果字典
        """
        try:
            # 1. 获取股票数据
            stock_data = await self._get_stock_data(symbol, trade_date)
            if not stock_data:
                raise Exception(f"无法获取股票数据: {symbol}")
            
            # 2. 调用TradingAgents分析API (如果可用)
            analysis_result = await self._call_tradingagents_analysis(symbol, trade_date)
            
            # 3. 如果TradingAgents不可用，使用本地分析
            if not analysis_result:
                analysis_result = await self._local_analysis(stock_data, symbol)
            
            # 4. 格式化结果
            return self._format_analysis_result(analysis_result, stock_data)
            
        except Exception as e:
            logger.error(f"分析失败: {symbol} - {e}")
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_stock_data(self, symbol: str, trade_date: str = None) -> Optional[Dict]:
        """通过Data Service获取股票数据"""
        try:
            # 创建连接器以避免警告
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                # 计算日期范围
                if trade_date:
                    end_date = trade_date
                    # 获取前30天的数据用于分析
                    from datetime import datetime, timedelta
                    trade_dt = datetime.strptime(trade_date, "%Y-%m-%d")
                    start_dt = trade_dt - timedelta(days=30)
                    start_date = start_dt.strftime("%Y-%m-%d")
                else:
                    end_date = datetime.now().strftime("%Y-%m-%d")
                    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                
                # 调用Data Service API
                url = f"{self.data_service_url}/api/enhanced/stock/{symbol}"
                params = {
                    "start_date": start_date,
                    "end_date": end_date,
                    "force_refresh": "true"  # 转换为字符串
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            return data.get("data")
                    
                    logger.warning(f"Data Service返回错误: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"获取股票数据失败: {e}")
            return None
    
    async def _call_tradingagents_analysis(self, symbol: str, trade_date: str = None) -> Optional[Dict]:
        """
        调用TradingAgents分析API
        如果TradingAgents提供了HTTP API接口
        """
        try:
            # 检查TradingAgents是否提供API接口
            async with aiohttp.ClientSession() as session:
                # 尝试调用TradingAgents的分析API
                url = f"{self.tradingagents_api_url}/api/analyze"
                payload = {
                    "symbol": symbol,
                    "trade_date": trade_date or datetime.now().strftime("%Y-%m-%d"),
                    "config": self.config
                }
                
                async with session.post(url, json=payload, timeout=120) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            return data.get("result")
                    
                    logger.info(f"TradingAgents API不可用: {response.status}")
                    return None
                    
        except Exception as e:
            logger.info(f"TradingAgents API调用失败，将使用本地分析: {e}")
            return None
    
    async def _local_analysis(self, stock_data: Dict, symbol: str) -> Dict[str, Any]:
        """
        本地分析逻辑 - 当TradingAgents不可用时的备用方案
        """
        try:
            # 基础技术分析
            historical_data = stock_data.get("historical_data", [])
            stock_info = stock_data.get("stock_info", {})
            
            if not historical_data:
                return {
                    "action": "HOLD",
                    "confidence": 0.5,
                    "risk_score": 0.5,
                    "reasoning": "数据不足，建议观望",
                    "analysis_type": "local_basic"
                }
            
            # 简单的技术分析
            recent_prices = [float(item.get("close", 0)) for item in historical_data[-10:]]
            if len(recent_prices) < 2:
                return {
                    "action": "HOLD",
                    "confidence": 0.5,
                    "risk_score": 0.5,
                    "reasoning": "历史数据不足",
                    "analysis_type": "local_basic"
                }
            
            # 计算简单移动平均
            sma_5 = sum(recent_prices[-5:]) / min(5, len(recent_prices))
            sma_10 = sum(recent_prices[-10:]) / min(10, len(recent_prices))
            current_price = recent_prices[-1]
            
            # 简单的买卖信号
            if current_price > sma_5 > sma_10:
                action = "BUY"
                confidence = 0.7
                risk_score = 0.4
                reasoning = f"价格({current_price:.2f})高于短期均线({sma_5:.2f})和长期均线({sma_10:.2f})，呈上升趋势"
            elif current_price < sma_5 < sma_10:
                action = "SELL"
                confidence = 0.7
                risk_score = 0.6
                reasoning = f"价格({current_price:.2f})低于短期均线({sma_5:.2f})和长期均线({sma_10:.2f})，呈下降趋势"
            else:
                action = "HOLD"
                confidence = 0.6
                risk_score = 0.5
                reasoning = f"价格({current_price:.2f})在均线附近震荡，建议观望"
            
            return {
                "action": action,
                "confidence": confidence,
                "risk_score": risk_score,
                "reasoning": reasoning,
                "analysis_type": "local_technical",
                "indicators": {
                    "current_price": current_price,
                    "sma_5": sma_5,
                    "sma_10": sma_10
                }
            }
            
        except Exception as e:
            logger.error(f"本地分析失败: {e}")
            return {
                "action": "HOLD",
                "confidence": 0.5,
                "risk_score": 0.5,
                "reasoning": f"分析过程出错: {str(e)}",
                "analysis_type": "error"
            }
    
    def _format_analysis_result(self, analysis_result: Dict, stock_data: Dict) -> Dict[str, Any]:
        """格式化分析结果"""
        stock_info = stock_data.get("stock_info", {})
        
        return {
            "success": True,
            "symbol": stock_data.get("symbol", ""),
            "company_name": stock_info.get("name", ""),
            "analysis": {
                "action": analysis_result.get("action", "HOLD"),
                "confidence": analysis_result.get("confidence", 0.5),
                "risk_score": analysis_result.get("risk_score", 0.5),
                "reasoning": analysis_result.get("reasoning", ""),
                "analysis_type": analysis_result.get("analysis_type", "unknown")
            },
            "market_data": {
                "current_price": stock_info.get("current_price", 0),
                "change": stock_info.get("change", 0),
                "change_percent": stock_info.get("change_percent", 0),
                "data_source": stock_data.get("data_source", "unknown")
            },
            "timestamp": datetime.now().isoformat(),
            "data_freshness": stock_data.get("timestamp", "")
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = {
            "service": "analysis-engine",
            "status": "healthy",
            "dependencies": {}
        }
        
        # 检查Data Service
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.data_service_url}/health", timeout=5) as response:
                    if response.status == 200:
                        status["dependencies"]["data_service"] = "healthy"
                    else:
                        status["dependencies"]["data_service"] = f"unhealthy ({response.status})"
        except Exception as e:
            status["dependencies"]["data_service"] = f"unreachable ({str(e)})"
        
        # 检查TradingAgents API (可选)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.tradingagents_api_url}/health", timeout=5) as response:
                    if response.status == 200:
                        status["dependencies"]["tradingagents_api"] = "healthy"
                    else:
                        status["dependencies"]["tradingagents_api"] = f"unhealthy ({response.status})"
        except Exception as e:
            status["dependencies"]["tradingagents_api"] = f"unreachable ({str(e)}) - using local analysis"
        
        # 如果关键依赖不可用，标记为降级服务
        if status["dependencies"].get("data_service", "").startswith("unhealthy"):
            status["status"] = "degraded"
        
        return status
