"""
分析工具
提供技术分析和基本面分析功能
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import math

logger = logging.getLogger(__name__)

class AnalysisTools:
    """分析工具类"""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """初始化分析工具"""
        try:
            logger.info("📊 初始化分析工具...")
            
            self.initialized = True
            logger.info("✅ 分析工具初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 分析工具初始化失败: {e}")
            raise
    
    async def calculate_technical_indicators(self, data: Dict[str, Any], indicators: List[str]) -> Dict[str, Any]:
        """计算技术指标"""
        try:
            logger.info(f"📈 计算技术指标: {indicators}")
            
            # 模拟价格数据
            prices = data.get("prices", [150, 151, 149, 152, 148, 153, 150, 155, 152, 157])
            volumes = data.get("volumes", [1000000] * len(prices))
            
            results = {}
            
            for indicator in indicators:
                if indicator.upper() == "RSI":
                    results["rsi"] = self._calculate_rsi(prices)
                elif indicator.upper() == "MACD":
                    results["macd"] = self._calculate_macd(prices)
                elif indicator.upper() == "MA":
                    results["moving_averages"] = self._calculate_moving_averages(prices)
                elif indicator.upper() == "BOLLINGER":
                    results["bollinger_bands"] = self._calculate_bollinger_bands(prices)
                elif indicator.upper() == "VOLUME":
                    results["volume_analysis"] = self._analyze_volume(prices, volumes)
            
            return {
                "success": True,
                "indicators": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 计算技术指标失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> Dict[str, Any]:
        """计算RSI指标"""
        if len(prices) < period + 1:
            return {"value": 50.0, "signal": "neutral"}
        
        # 计算价格变化
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # 分离上涨和下跌
        gains = [max(delta, 0) for delta in deltas]
        losses = [abs(min(delta, 0)) for delta in deltas]
        
        # 计算平均收益和损失
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        # 判断信号
        if rsi > 70:
            signal = "overbought"
        elif rsi < 30:
            signal = "oversold"
        else:
            signal = "neutral"
        
        return {
            "value": round(rsi, 2),
            "signal": signal,
            "period": period
        }
    
    def _calculate_macd(self, prices: List[float]) -> Dict[str, Any]:
        """计算MACD指标"""
        if len(prices) < 26:
            return {"macd": 0, "signal": 0, "histogram": 0, "trend": "neutral"}
        
        # 简化的MACD计算
        ema12 = self._calculate_ema(prices, 12)
        ema26 = self._calculate_ema(prices, 26)
        
        macd_line = ema12 - ema26
        signal_line = macd_line * 0.9  # 简化的信号线
        histogram = macd_line - signal_line
        
        # 判断趋势
        if macd_line > signal_line and histogram > 0:
            trend = "bullish"
        elif macd_line < signal_line and histogram < 0:
            trend = "bearish"
        else:
            trend = "neutral"
        
        return {
            "macd": round(macd_line, 4),
            "signal": round(signal_line, 4),
            "histogram": round(histogram, 4),
            "trend": trend
        }
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """计算指数移动平均"""
        if len(prices) < period:
            return sum(prices) / len(prices)
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_moving_averages(self, prices: List[float]) -> Dict[str, Any]:
        """计算移动平均线"""
        result = {}
        
        for period in [5, 10, 20, 50]:
            if len(prices) >= period:
                ma = sum(prices[-period:]) / period
                result[f"ma_{period}"] = round(ma, 2)
        
        return result
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20) -> Dict[str, Any]:
        """计算布林带"""
        if len(prices) < period:
            current_price = prices[-1] if prices else 150
            return {
                "upper": current_price * 1.02,
                "middle": current_price,
                "lower": current_price * 0.98,
                "position": "middle"
            }
        
        # 计算移动平均和标准差
        recent_prices = prices[-period:]
        ma = sum(recent_prices) / period
        variance = sum((p - ma) ** 2 for p in recent_prices) / period
        std = math.sqrt(variance)
        
        upper = ma + (2 * std)
        lower = ma - (2 * std)
        current_price = prices[-1]
        
        # 判断位置
        if current_price > upper:
            position = "above_upper"
        elif current_price < lower:
            position = "below_lower"
        else:
            position = "middle"
        
        return {
            "upper": round(upper, 2),
            "middle": round(ma, 2),
            "lower": round(lower, 2),
            "position": position
        }
    
    def _analyze_volume(self, prices: List[float], volumes: List[int]) -> Dict[str, Any]:
        """分析成交量"""
        if len(volumes) < 2:
            return {"trend": "neutral", "strength": "normal"}
        
        recent_volume = sum(volumes[-5:]) / 5 if len(volumes) >= 5 else volumes[-1]
        avg_volume = sum(volumes) / len(volumes)
        
        volume_ratio = recent_volume / avg_volume
        
        if volume_ratio > 1.5:
            strength = "high"
        elif volume_ratio < 0.5:
            strength = "low"
        else:
            strength = "normal"
        
        # 价量关系分析
        price_change = (prices[-1] - prices[-2]) / prices[-2] if len(prices) >= 2 else 0
        volume_change = (volumes[-1] - volumes[-2]) / volumes[-2] if len(volumes) >= 2 else 0
        
        if price_change > 0 and volume_change > 0:
            trend = "bullish_confirmation"
        elif price_change < 0 and volume_change > 0:
            trend = "bearish_confirmation"
        else:
            trend = "neutral"
        
        return {
            "trend": trend,
            "strength": strength,
            "volume_ratio": round(volume_ratio, 2),
            "recent_volume": int(recent_volume),
            "average_volume": int(avg_volume)
        }
    
    async def perform_fundamental_analysis(self, financial_data: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行基本面分析"""
        try:
            logger.info("💰 执行基本面分析")
            
            # 提取财务数据
            revenue = financial_data.get("revenue", 50000000000)
            net_income = financial_data.get("net_income", 5000000000)
            total_assets = financial_data.get("total_assets", 100000000000)
            total_debt = financial_data.get("total_debt", 30000000000)
            shareholders_equity = financial_data.get("shareholders_equity", 70000000000)
            
            # 提取市场数据
            market_cap = market_data.get("market_cap", 2500000000)
            current_price = market_data.get("price", 150.0)
            
            # 计算财务比率
            ratios = self._calculate_financial_ratios(
                revenue, net_income, total_assets, total_debt, 
                shareholders_equity, market_cap
            )
            
            # 评估财务健康度
            health_score = self._assess_financial_health(ratios)
            
            # 生成分析结论
            analysis = self._generate_fundamental_analysis(ratios, health_score)
            
            return {
                "success": True,
                "ratios": ratios,
                "health_score": health_score,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 基本面分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_financial_ratios(self, revenue: float, net_income: float, 
                                  total_assets: float, total_debt: float,
                                  shareholders_equity: float, market_cap: float) -> Dict[str, float]:
        """计算财务比率"""
        ratios = {}
        
        # 盈利能力比率
        if revenue > 0:
            ratios["net_margin"] = (net_income / revenue) * 100
        
        if total_assets > 0:
            ratios["roa"] = (net_income / total_assets) * 100
        
        if shareholders_equity > 0:
            ratios["roe"] = (net_income / shareholders_equity) * 100
        
        # 偿债能力比率
        if total_assets > 0:
            ratios["debt_to_assets"] = (total_debt / total_assets) * 100
        
        if shareholders_equity > 0:
            ratios["debt_to_equity"] = (total_debt / shareholders_equity) * 100
        
        # 估值比率
        if net_income > 0:
            ratios["pe_ratio"] = market_cap / net_income
        
        if shareholders_equity > 0:
            ratios["pb_ratio"] = market_cap / shareholders_equity
        
        return {k: round(v, 2) for k, v in ratios.items()}
    
    def _assess_financial_health(self, ratios: Dict[str, float]) -> Dict[str, Any]:
        """评估财务健康度"""
        score = 0
        max_score = 0
        details = {}
        
        # ROE评分
        roe = ratios.get("roe", 0)
        if roe > 15:
            score += 20
            details["roe"] = "excellent"
        elif roe > 10:
            score += 15
            details["roe"] = "good"
        elif roe > 5:
            score += 10
            details["roe"] = "fair"
        else:
            details["roe"] = "poor"
        max_score += 20
        
        # 净利率评分
        net_margin = ratios.get("net_margin", 0)
        if net_margin > 20:
            score += 20
            details["profitability"] = "excellent"
        elif net_margin > 10:
            score += 15
            details["profitability"] = "good"
        elif net_margin > 5:
            score += 10
            details["profitability"] = "fair"
        else:
            details["profitability"] = "poor"
        max_score += 20
        
        # 债务比率评分
        debt_to_assets = ratios.get("debt_to_assets", 50)
        if debt_to_assets < 30:
            score += 20
            details["leverage"] = "conservative"
        elif debt_to_assets < 50:
            score += 15
            details["leverage"] = "moderate"
        elif debt_to_assets < 70:
            score += 10
            details["leverage"] = "high"
        else:
            details["leverage"] = "excessive"
        max_score += 20
        
        # 估值评分
        pe_ratio = ratios.get("pe_ratio", 25)
        if 10 <= pe_ratio <= 20:
            score += 20
            details["valuation"] = "reasonable"
        elif 5 <= pe_ratio <= 30:
            score += 15
            details["valuation"] = "acceptable"
        else:
            score += 5
            details["valuation"] = "extreme"
        max_score += 20
        
        final_score = (score / max_score) * 100 if max_score > 0 else 50
        
        return {
            "score": round(final_score, 1),
            "grade": self._get_health_grade(final_score),
            "details": details
        }
    
    def _get_health_grade(self, score: float) -> str:
        """获取健康度等级"""
        if score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _generate_fundamental_analysis(self, ratios: Dict[str, float], health_score: Dict[str, Any]) -> str:
        """生成基本面分析结论"""
        grade = health_score["grade"]
        score = health_score["score"]
        
        if grade in ["A", "B"]:
            conclusion = f"公司基本面表现优秀（评分：{score}），财务状况健康，具有良好的投资价值。"
        elif grade == "C":
            conclusion = f"公司基本面表现一般（评分：{score}），财务状况尚可，需要关注风险因素。"
        else:
            conclusion = f"公司基本面表现较差（评分：{score}），财务状况存在问题，投资风险较高。"
        
        return conclusion
    
    async def calculate_valuation(self, financial_data: Dict[str, Any], method: str = "dcf") -> Dict[str, Any]:
        """计算估值"""
        try:
            logger.info(f"💰 计算估值: {method}")
            
            if method.lower() == "dcf":
                return await self._calculate_dcf_valuation(financial_data)
            elif method.lower() == "pe":
                return await self._calculate_pe_valuation(financial_data)
            elif method.lower() == "pb":
                return await self._calculate_pb_valuation(financial_data)
            else:
                raise ValueError(f"不支持的估值方法: {method}")
                
        except Exception as e:
            logger.error(f"❌ 估值计算失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _calculate_dcf_valuation(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """DCF估值计算"""
        # 简化的DCF计算
        free_cash_flow = financial_data.get("free_cash_flow", 6000000000)
        growth_rate = 0.05  # 假设5%增长率
        discount_rate = 0.10  # 假设10%折现率
        terminal_growth = 0.02  # 假设2%永续增长率
        
        # 计算未来5年现金流现值
        pv_cash_flows = 0
        for year in range(1, 6):
            future_cf = free_cash_flow * ((1 + growth_rate) ** year)
            pv_cf = future_cf / ((1 + discount_rate) ** year)
            pv_cash_flows += pv_cf
        
        # 计算终值
        terminal_cf = free_cash_flow * ((1 + growth_rate) ** 5) * (1 + terminal_growth)
        terminal_value = terminal_cf / (discount_rate - terminal_growth)
        pv_terminal_value = terminal_value / ((1 + discount_rate) ** 5)
        
        enterprise_value = pv_cash_flows + pv_terminal_value
        
        return {
            "success": True,
            "method": "DCF",
            "enterprise_value": round(enterprise_value, 0),
            "pv_cash_flows": round(pv_cash_flows, 0),
            "terminal_value": round(pv_terminal_value, 0),
            "assumptions": {
                "growth_rate": growth_rate,
                "discount_rate": discount_rate,
                "terminal_growth": terminal_growth
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def _calculate_pe_valuation(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """PE估值计算"""
        net_income = financial_data.get("net_income", 5000000000)
        industry_pe = 20  # 假设行业平均PE为20
        
        estimated_value = net_income * industry_pe
        
        return {
            "success": True,
            "method": "PE",
            "estimated_value": round(estimated_value, 0),
            "net_income": net_income,
            "industry_pe": industry_pe,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _calculate_pb_valuation(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """PB估值计算"""
        book_value = financial_data.get("shareholders_equity", 70000000000)
        industry_pb = 2.5  # 假设行业平均PB为2.5
        
        estimated_value = book_value * industry_pb
        
        return {
            "success": True,
            "method": "PB",
            "estimated_value": round(estimated_value, 0),
            "book_value": book_value,
            "industry_pb": industry_pb,
            "timestamp": datetime.now().isoformat()
        }
    
    async def reload(self):
        """重新加载分析工具"""
        logger.info("🔄 重新加载分析工具...")
        # 分析工具通常不需要特殊的重新加载逻辑
        logger.info("✅ 分析工具重新加载完成")
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理分析工具资源...")
        self.initialized = False
        logger.info("✅ 分析工具资源清理完成")
