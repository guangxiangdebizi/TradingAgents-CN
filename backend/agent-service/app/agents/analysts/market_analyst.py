"""
市场分析师智能体
负责技术分析和市场趋势分析
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.shared.logging_config import get_logger
from backend.shared.clients.llm_client import LLMClient
from backend.shared.clients.data_client import DataClient

from ..base_agent import BaseAgent, AgentType, AgentCapability, TaskContext, TaskResult

logger = get_logger("agent-service.market_analyst")


class MarketAnalyst(BaseAgent):
    """市场分析师智能体"""
    
    def __init__(self, agent_type: AgentType, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_type, agent_id, config)
        self.llm_client = LLMClient()
        self.data_client = DataClient()
        
        # 分析模板
        self.analysis_template = self._get_analysis_template()
        
        logger.info(f"🏗️ 市场分析师初始化完成: {self.agent_id}")
    
    def _define_capabilities(self) -> List[AgentCapability]:
        """定义智能体能力"""
        return [
            AgentCapability(
                name="technical_analysis",
                description="技术分析 - 价格趋势和技术指标分析",
                required_tools=["get_market_data", "get_technical_indicators", "get_price_history"],
                supported_markets=["US", "CN", "HK"],
                max_concurrent_tasks=3,
                estimated_duration=90
            ),
            AgentCapability(
                name="trend_analysis",
                description="趋势分析 - 识别价格趋势和支撑阻力位",
                required_tools=["get_price_history", "calculate_moving_averages"],
                supported_markets=["US", "CN", "HK"],
                max_concurrent_tasks=2,
                estimated_duration=60
            ),
            AgentCapability(
                name="volume_analysis",
                description="成交量分析 - 分析成交量变化和价量关系",
                required_tools=["get_volume_data", "get_market_data"],
                supported_markets=["US", "CN", "HK"],
                max_concurrent_tasks=2,
                estimated_duration=45
            )
        ]
    
    async def process_task(self, context: TaskContext) -> TaskResult:
        """处理市场分析任务"""
        try:
            logger.info(f"📈 开始市场分析: {context.symbol}")
            
            # 1. 获取市场数据
            market_data = await self._get_market_data(context.symbol, context.market)
            
            # 2. 获取价格历史数据
            price_history = await self._get_price_history(context.symbol, context.market)
            
            # 3. 计算技术指标
            technical_indicators = await self._calculate_technical_indicators(price_history)
            
            # 4. 进行趋势分析
            trend_analysis = await self._perform_trend_analysis(price_history, technical_indicators)
            
            # 5. 进行成交量分析
            volume_analysis = await self._perform_volume_analysis(price_history)
            
            # 6. 生成分析报告
            analysis_report = await self._generate_analysis_report(
                context, market_data, price_history, technical_indicators, 
                trend_analysis, volume_analysis
            )
            
            # 7. 生成交易信号
            trading_signals = await self._generate_trading_signals(
                technical_indicators, trend_analysis, volume_analysis
            )
            
            result = {
                "analysis_type": "market_analysis",
                "symbol": context.symbol,
                "company_name": context.company_name,
                "market": context.market,
                "analysis_date": context.analysis_date,
                "market_data": market_data,
                "price_history": price_history,
                "technical_indicators": technical_indicators,
                "trend_analysis": trend_analysis,
                "volume_analysis": volume_analysis,
                "analysis_report": analysis_report,
                "trading_signals": trading_signals,
                "confidence_score": self._calculate_confidence_score(technical_indicators, trend_analysis),
                "risk_level": self._assess_risk_level(technical_indicators, volume_analysis),
                "key_levels": self._identify_key_levels(price_history, technical_indicators),
                "analyst_id": self.agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ 市场分析完成: {context.symbol}")
            
            return TaskResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status="success",
                result=result
            )
            
        except Exception as e:
            logger.error(f"❌ 市场分析失败: {context.symbol} - {e}")
            raise
    
    async def _get_market_data(self, symbol: str, market: str) -> Dict[str, Any]:
        """获取市场数据"""
        try:
            response = await self.data_client.get_market_data(symbol, market)
            return response.get("data", {})
        except Exception as e:
            # 判断是否为连接错误或超时错误
            if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
                logger.critical(f"🚨 严重告警: 无法连接Data Service获取市场数据 - {symbol}")
                logger.critical(f"🚨 请检查Data Service是否启动并可访问")
                logger.critical(f"🚨 错误详情: {type(e).__name__}: {str(e)}")
            else:
                logger.error(f"❌ 获取市场数据失败: {symbol} - {e}")
            return {}
    
    async def _get_price_history(self, symbol: str, market: str, days: int = 252) -> Dict[str, Any]:
        """获取价格历史数据"""
        try:
            logger.info(f"🔍 Market Analyst 请求价格历史: {symbol}, market: {market}, days: {days}")
            response = await self.data_client.get_price_history(symbol, market, days)

            logger.info(f"🔍 Market Analyst 收到响应类型: {type(response)}")
            logger.info(f"🔍 Market Analyst 收到响应内容: {str(response)[:300] if response else 'None'}")

            if isinstance(response, dict):
                # Data Client已经提取了data字段，直接返回响应
                logger.info(f"🔍 Market Analyst 直接使用响应数据: {type(response)}")
                logger.info(f"🔍 Market Analyst 响应数据内容: {str(response)[:300] if response else 'None'}")
                return response
            else:
                logger.error(f"🔍 Market Analyst 响应不是字典: {type(response)}")
                return {}
        except Exception as e:
            # 判断是否为连接错误或超时错误
            if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
                logger.critical(f"🚨 严重告警: 无法连接Data Service获取价格历史 - {symbol}")
                logger.critical(f"🚨 请检查Data Service是否启动并可访问")
                logger.critical(f"🚨 错误详情: {type(e).__name__}: {str(e)}")
            else:
                logger.error(f"❌ 获取价格历史失败: {symbol} - {e}")
                import traceback
                logger.error(f"❌ 详细错误: {traceback.format_exc()}")
            return {}
    
    async def _calculate_technical_indicators(self, price_history: Dict[str, Any]) -> Dict[str, Any]:
        """计算技术指标"""
        try:
            logger.info(f"🔍 计算技术指标 - 输入数据类型: {type(price_history)}")
            logger.info(f"🔍 计算技术指标 - 输入数据内容: {str(price_history)[:300] if price_history else 'None'}")

            if isinstance(price_history, dict):
                logger.info(f"🔍 计算技术指标 - 数据键: {list(price_history.keys())}")
                prices = price_history.get("close_prices", [])
                volumes = price_history.get("volumes", [])
                logger.info(f"🔍 计算技术指标 - prices类型: {type(prices)}, 长度: {len(prices) if prices else 0}")
                logger.info(f"🔍 计算技术指标 - volumes类型: {type(volumes)}, 长度: {len(volumes) if volumes else 0}")
            else:
                logger.error(f"🔍 计算技术指标 - 输入不是字典: {type(price_history)}")
                prices = []
                volumes = []

            if not prices:
                logger.warning(f"🔍 计算技术指标 - 没有价格数据")
                return {}
            
            # 移动平均线
            ma5 = self._calculate_moving_average(prices, 5)
            ma10 = self._calculate_moving_average(prices, 10)
            ma20 = self._calculate_moving_average(prices, 20)
            ma50 = self._calculate_moving_average(prices, 50)
            
            # RSI
            rsi = self._calculate_rsi(prices, 14)
            
            # MACD
            macd_line, signal_line, histogram = self._calculate_macd(prices)
            
            # 布林带
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(prices, 20)
            
            # KDJ
            k_values, d_values, j_values = self._calculate_kdj(price_history)
            
            indicators = {
                "moving_averages": {
                    "ma5": ma5[-1] if ma5 else 0,
                    "ma10": ma10[-1] if ma10 else 0,
                    "ma20": ma20[-1] if ma20 else 0,
                    "ma50": ma50[-1] if ma50 else 0
                },
                "momentum_indicators": {
                    "rsi": rsi[-1] if rsi else 50,
                    "macd": {
                        "macd_line": macd_line[-1] if macd_line else 0,
                        "signal_line": signal_line[-1] if signal_line else 0,
                        "histogram": histogram[-1] if histogram else 0
                    }
                },
                "volatility_indicators": {
                    "bollinger_bands": {
                        "upper": bb_upper[-1] if bb_upper else 0,
                        "middle": bb_middle[-1] if bb_middle else 0,
                        "lower": bb_lower[-1] if bb_lower else 0
                    }
                },
                "oscillators": {
                    "kdj": {
                        "k": k_values[-1] if k_values else 50,
                        "d": d_values[-1] if d_values else 50,
                        "j": j_values[-1] if j_values else 50
                    }
                }
            }
            
            return indicators
            
        except Exception as e:
            logger.error(f"❌ 计算技术指标失败: {e}")
            return {}
    
    async def _perform_trend_analysis(self, price_history: Dict[str, Any], technical_indicators: Dict[str, Any]) -> Dict[str, Any]:
        """进行趋势分析"""
        try:
            prices = price_history.get("close_prices", [])
            if not prices:
                return {}
            
            # 趋势方向判断
            ma_indicators = technical_indicators.get("moving_averages", {})
            current_price = prices[-1]
            
            trend_direction = "sideways"
            if current_price > ma_indicators.get("ma20", 0) > ma_indicators.get("ma50", 0):
                trend_direction = "uptrend"
            elif current_price < ma_indicators.get("ma20", 0) < ma_indicators.get("ma50", 0):
                trend_direction = "downtrend"
            
            # 趋势强度
            trend_strength = self._calculate_trend_strength(prices, ma_indicators)
            
            # 支撑阻力位
            support_levels, resistance_levels = self._identify_support_resistance(prices)
            
            trend_analysis = {
                "trend_direction": trend_direction,
                "trend_strength": trend_strength,
                "support_levels": support_levels,
                "resistance_levels": resistance_levels,
                "price_position": self._analyze_price_position(current_price, ma_indicators),
                "breakout_potential": self._assess_breakout_potential(prices, support_levels, resistance_levels)
            }
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"❌ 趋势分析失败: {e}")
            return {}
    
    async def _perform_volume_analysis(self, price_history: Dict[str, Any]) -> Dict[str, Any]:
        """进行成交量分析"""
        try:
            volumes = price_history.get("volumes", [])
            prices = price_history.get("close_prices", [])
            
            if not volumes or not prices:
                return {}
            
            # 成交量趋势
            volume_trend = self._analyze_volume_trend(volumes)
            
            # 价量关系
            price_volume_relationship = self._analyze_price_volume_relationship(prices, volumes)
            
            # 成交量指标
            volume_ma = self._calculate_moving_average(volumes, 20)
            volume_ratio = volumes[-1] / volume_ma[-1] if volume_ma and volume_ma[-1] > 0 else 1
            
            volume_analysis = {
                "volume_trend": volume_trend,
                "price_volume_relationship": price_volume_relationship,
                "volume_ratio": volume_ratio,
                "volume_signal": "high" if volume_ratio > 1.5 else "normal" if volume_ratio > 0.5 else "low"
            }
            
            return volume_analysis
            
        except Exception as e:
            logger.error(f"❌ 成交量分析失败: {e}")
            return {}
    
    def _calculate_moving_average(self, prices: List[float], period: int) -> List[float]:
        """计算移动平均线"""
        if len(prices) < period:
            return []
        
        ma_values = []
        for i in range(period - 1, len(prices)):
            ma = sum(prices[i - period + 1:i + 1]) / period
            ma_values.append(ma)
        
        return ma_values
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """计算RSI指标"""
        if len(prices) < period + 1:
            return []
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-change)
        
        rsi_values = []
        for i in range(period - 1, len(gains)):
            avg_gain = sum(gains[i - period + 1:i + 1]) / period
            avg_loss = sum(losses[i - period + 1:i + 1]) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
        
        return rsi_values
    
    def _calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """计算MACD指标"""
        if len(prices) < slow:
            return [], [], []
        
        # 计算EMA
        ema_fast = self._calculate_ema(prices, fast)
        ema_slow = self._calculate_ema(prices, slow)
        
        # MACD线
        macd_line = []
        for i in range(len(ema_slow)):
            macd_line.append(ema_fast[i + (slow - fast)] - ema_slow[i])
        
        # 信号线
        signal_line = self._calculate_ema(macd_line, signal)
        
        # 柱状图
        histogram = []
        for i in range(len(signal_line)):
            histogram.append(macd_line[i + (signal - 1)] - signal_line[i])
        
        return macd_line, signal_line, histogram
    
    def _calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """计算指数移动平均线"""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema_values = [sum(prices[:period]) / period]  # 第一个值用SMA
        
        for i in range(period, len(prices)):
            ema = (prices[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2) -> tuple:
        """计算布林带"""
        if len(prices) < period:
            return [], [], []
        
        ma_values = self._calculate_moving_average(prices, period)
        upper_band = []
        lower_band = []
        
        for i in range(len(ma_values)):
            price_slice = prices[i:i + period]
            std = (sum([(p - ma_values[i]) ** 2 for p in price_slice]) / period) ** 0.5
            
            upper_band.append(ma_values[i] + (std_dev * std))
            lower_band.append(ma_values[i] - (std_dev * std))
        
        return upper_band, ma_values, lower_band
    
    def _calculate_kdj(self, price_history: Dict[str, Any], period: int = 9) -> tuple:
        """计算KDJ指标"""
        highs = price_history.get("high_prices", [])
        lows = price_history.get("low_prices", [])
        closes = price_history.get("close_prices", [])
        
        if len(closes) < period:
            return [], [], []
        
        k_values = []
        d_values = []
        j_values = []
        
        for i in range(period - 1, len(closes)):
            highest_high = max(highs[i - period + 1:i + 1])
            lowest_low = min(lows[i - period + 1:i + 1])
            
            if highest_high == lowest_low:
                rsv = 50
            else:
                rsv = (closes[i] - lowest_low) / (highest_high - lowest_low) * 100
            
            if not k_values:
                k = rsv
                d = rsv
            else:
                k = (2 * k_values[-1] + rsv) / 3
                d = (2 * d_values[-1] + k) / 3
            
            j = 3 * k - 2 * d
            
            k_values.append(k)
            d_values.append(d)
            j_values.append(j)
        
        return k_values, d_values, j_values
    
    def _calculate_trend_strength(self, prices: List[float], ma_indicators: Dict[str, float]) -> str:
        """计算趋势强度"""
        if not prices:
            return "weak"
        
        current_price = prices[-1]
        ma20 = ma_indicators.get("ma20", 0)
        ma50 = ma_indicators.get("ma50", 0)
        
        # 基于价格与均线的距离判断趋势强度
        if ma20 > 0:
            distance_ratio = abs(current_price - ma20) / ma20
            if distance_ratio > 0.05:
                return "strong"
            elif distance_ratio > 0.02:
                return "moderate"
        
        return "weak"
    
    def _identify_support_resistance(self, prices: List[float]) -> tuple:
        """识别支撑阻力位"""
        if len(prices) < 20:
            return [], []
        
        # 简化的支撑阻力位识别
        recent_prices = prices[-20:]
        support_levels = [min(recent_prices)]
        resistance_levels = [max(recent_prices)]
        
        return support_levels, resistance_levels
    
    def _analyze_price_position(self, current_price: float, ma_indicators: Dict[str, float]) -> str:
        """分析价格位置"""
        ma20 = ma_indicators.get("ma20", 0)
        ma50 = ma_indicators.get("ma50", 0)
        
        if current_price > ma20 > ma50:
            return "above_all_mas"
        elif current_price > ma50 > ma20:
            return "mixed_position"
        elif ma50 > ma20 > current_price:
            return "below_all_mas"
        else:
            return "neutral"
    
    def _assess_breakout_potential(self, prices: List[float], support_levels: List[float], resistance_levels: List[float]) -> str:
        """评估突破潜力"""
        if not prices or not resistance_levels:
            return "low"
        
        current_price = prices[-1]
        nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price))
        
        distance_to_resistance = abs(current_price - nearest_resistance) / current_price
        
        if distance_to_resistance < 0.02:
            return "high"
        elif distance_to_resistance < 0.05:
            return "moderate"
        else:
            return "low"
    
    def _analyze_volume_trend(self, volumes: List[float]) -> str:
        """分析成交量趋势"""
        if len(volumes) < 10:
            return "insufficient_data"
        
        recent_avg = sum(volumes[-5:]) / 5
        previous_avg = sum(volumes[-10:-5]) / 5
        
        if recent_avg > previous_avg * 1.2:
            return "increasing"
        elif recent_avg < previous_avg * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_price_volume_relationship(self, prices: List[float], volumes: List[float]) -> str:
        """分析价量关系"""
        if len(prices) < 2 or len(volumes) < 2:
            return "insufficient_data"
        
        price_change = prices[-1] - prices[-2]
        volume_change = volumes[-1] - volumes[-2]
        
        if price_change > 0 and volume_change > 0:
            return "bullish_confirmation"
        elif price_change < 0 and volume_change > 0:
            return "bearish_confirmation"
        elif price_change > 0 and volume_change < 0:
            return "bullish_divergence"
        elif price_change < 0 and volume_change < 0:
            return "bearish_divergence"
        else:
            return "neutral"
    
    async def _generate_analysis_report(
        self,
        context: TaskContext,
        market_data: Dict[str, Any],
        price_history: Dict[str, Any],
        technical_indicators: Dict[str, Any],
        trend_analysis: Dict[str, Any],
        volume_analysis: Dict[str, Any]
    ) -> str:
        """生成分析报告"""
        try:
            prompt = self.analysis_template.format(
                symbol=context.symbol,
                company_name=context.company_name,
                analysis_date=context.analysis_date,
                market_data=market_data,
                technical_indicators=technical_indicators,
                trend_analysis=trend_analysis,
                volume_analysis=volume_analysis
            )
            
            response = await self.llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="deepseek-chat",
                temperature=0.1
            )
            
            return response.get("content", "分析报告生成失败")
            
        except Exception as e:
            # 判断是否为连接错误或超时错误
            if "connection" in str(e).lower() or "timeout" in str(e).lower() or "failed" in str(e).lower():
                logger.critical(f"🚨 严重告警: 无法连接LLM Service生成分析报告")
                logger.critical(f"🚨 请检查LLM Service是否启动并可访问")
                logger.critical(f"🚨 错误详情: {type(e).__name__}: {str(e)}")
            else:
                logger.error(f"❌ 生成分析报告失败: {e}")
            return f"分析报告生成失败: {str(e)}"
    
    async def _generate_trading_signals(
        self,
        technical_indicators: Dict[str, Any],
        trend_analysis: Dict[str, Any],
        volume_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成交易信号"""
        try:
            signals = {
                "overall_signal": "hold",
                "signal_strength": 0,
                "entry_points": [],
                "exit_points": [],
                "stop_loss": None,
                "take_profit": None
            }
            
            # 基于技术指标生成信号
            ma_indicators = technical_indicators.get("moving_averages", {})
            rsi = technical_indicators.get("momentum_indicators", {}).get("rsi", 50)
            
            signal_score = 0
            
            # RSI信号
            if rsi < 30:
                signal_score += 2  # 超卖，买入信号
            elif rsi > 70:
                signal_score -= 2  # 超买，卖出信号
            
            # 趋势信号
            trend_direction = trend_analysis.get("trend_direction", "sideways")
            if trend_direction == "uptrend":
                signal_score += 1
            elif trend_direction == "downtrend":
                signal_score -= 1
            
            # 成交量确认
            volume_signal = volume_analysis.get("volume_signal", "normal")
            if volume_signal == "high":
                signal_score = signal_score * 1.5  # 放大信号强度
            
            # 确定最终信号
            if signal_score >= 2:
                signals["overall_signal"] = "buy"
                signals["signal_strength"] = min(signal_score / 4, 1.0)
            elif signal_score <= -2:
                signals["overall_signal"] = "sell"
                signals["signal_strength"] = min(abs(signal_score) / 4, 1.0)
            else:
                signals["overall_signal"] = "hold"
                signals["signal_strength"] = 0.5
            
            return signals
            
        except Exception as e:
            logger.error(f"❌ 生成交易信号失败: {e}")
            return {"overall_signal": "hold", "signal_strength": 0}
    
    def _calculate_confidence_score(self, technical_indicators: Dict[str, Any], trend_analysis: Dict[str, Any]) -> float:
        """计算置信度评分"""
        confidence = 0.5  # 基础置信度
        
        # 检查数据完整性
        if technical_indicators and trend_analysis:
            confidence += 0.2
        
        # 检查趋势一致性
        trend_direction = trend_analysis.get("trend_direction", "sideways")
        if trend_direction != "sideways":
            confidence += 0.2
        
        # 检查技术指标的有效性
        rsi = technical_indicators.get("momentum_indicators", {}).get("rsi", 50)
        if 20 < rsi < 80:  # RSI在合理范围内
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _assess_risk_level(self, technical_indicators: Dict[str, Any], volume_analysis: Dict[str, Any]) -> str:
        """评估风险水平"""
        risk_factors = 0
        
        # RSI风险
        rsi = technical_indicators.get("momentum_indicators", {}).get("rsi", 50)
        if rsi > 80 or rsi < 20:
            risk_factors += 1
        
        # 成交量风险
        volume_signal = volume_analysis.get("volume_signal", "normal")
        if volume_signal == "low":
            risk_factors += 1
        
        if risk_factors >= 2:
            return "high"
        elif risk_factors == 1:
            return "medium"
        else:
            return "low"
    
    def _identify_key_levels(self, price_history: Dict[str, Any], technical_indicators: Dict[str, Any]) -> Dict[str, List[float]]:
        """识别关键价位"""
        prices = price_history.get("close_prices", [])
        if not prices:
            return {"support": [], "resistance": []}
        
        current_price = prices[-1]
        ma_indicators = technical_indicators.get("moving_averages", {})
        
        key_levels = {
            "support": [],
            "resistance": []
        }
        
        # 添加移动平均线作为支撑阻力
        for ma_name, ma_value in ma_indicators.items():
            if ma_value > 0:
                if ma_value < current_price:
                    key_levels["support"].append(ma_value)
                else:
                    key_levels["resistance"].append(ma_value)
        
        return key_levels
    
    def _get_analysis_template(self) -> str:
        """获取分析模板"""
        return """
作为专业的市场分析师，请对股票 {symbol} ({company_name}) 进行全面的技术分析。

分析日期：{analysis_date}

市场数据：
{market_data}

技术指标：
{technical_indicators}

趋势分析：
{trend_analysis}

成交量分析：
{volume_analysis}

请提供详细的技术分析报告，包括：
1. 当前价格趋势判断
2. 主要技术指标解读
3. 支撑阻力位分析
4. 成交量特征分析
5. 短期和中期走势预测
6. 交易建议和风险提示

请用专业、客观的语言进行分析，并提供具体的技术指标数据支撑。
"""
