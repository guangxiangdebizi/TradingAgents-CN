"""
交易员智能体
移植自tradingagents，负责制定具体的交易策略和执行计划
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ..base.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class Trader(BaseAgent):
    """
    交易员智能体
    负责制定具体的交易策略、执行计划和风险控制措施
    """

    def __init__(self, llm_client=None, data_client=None):
        super().__init__(
            name="Trader",
            description="专业的交易员，负责制定具体的交易策略和执行计划",
            llm_client=llm_client,
            data_client=data_client
        )
        self.prompt_template = None

    async def _load_prompts(self):
        """加载交易策略提示词模板"""
        self.prompt_template = """
你是一位专业的交易员，具有丰富的交易执行和风险控制经验。

请为股票 {symbol} 制定具体的交易策略和执行计划：

## 分析要求：
1. **交易策略**：基于研究决策制定具体的交易方案
2. **执行计划**：确定买入/卖出的时机、价位和数量
3. **风险控制**：设定止损位、止盈位和仓位管理
4. **时机选择**：分析最佳的交易时机和市场条件
5. **成本控制**：考虑交易成本和市场冲击
6. **应急预案**：制定各种市场情况下的应对策略

## 研究决策：
{research_decision}

## 市场环境：
{market_environment}

## 技术分析：
{technical_analysis}

## 输出格式：
请提供详细的交易执行计划，包含具体的操作指导和风险控制措施。

## 执行建议：
给出明确的交易指令和执行时间表。
"""

    async def analyze(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行交易策略分析

        Args:
            symbol: 股票代码
            context: 分析上下文，包含研究决策和市场数据

        Returns:
            交易策略结果
        """
        self._log_analysis_start(symbol)

        try:
            # 1. 获取研究决策
            research_decision = await self._get_research_decision(context)

            # 2. 分析市场环境
            market_environment = await self._analyze_market_environment(symbol, context)

            # 3. 制定交易策略
            trading_strategy = await self._develop_trading_strategy(
                research_decision, market_environment
            )

            # 4. 设计执行计划
            execution_plan = await self._design_execution_plan(
                symbol, trading_strategy, market_environment
            )

            # 5. 制定风险控制措施
            risk_controls = await self._design_risk_controls(
                symbol, trading_strategy, execution_plan
            )

            # 6. 生成AI交易分析
            ai_analysis = await self._generate_ai_analysis(
                symbol, research_decision, market_environment, trading_strategy
            )

            # 7. 整合交易结果
            result = {
                "analysis_type": "trading_strategy",
                "symbol": symbol,
                "analyst": self.name,
                "timestamp": datetime.now().isoformat(),
                "research_decision_summary": research_decision,
                "market_environment": market_environment,
                "trading_strategy": trading_strategy,
                "execution_plan": execution_plan,
                "risk_controls": risk_controls,
                "ai_analysis": ai_analysis,
                "trade_recommendation": trading_strategy.get("action", "HOLD"),
                "execution_priority": execution_plan.get("priority", "NORMAL"),
                "estimated_timeline": execution_plan.get("timeline", "1-3天")
            }

            self._log_analysis_complete(symbol, f"策略: {result['trade_recommendation']}")
            return result

        except Exception as e:
            self.logger.error(f"❌ [{self.name}] 分析失败: {symbol} - {e}")
            return {
                "analysis_type": "trading_strategy",
                "symbol": symbol,
                "analyst": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _get_research_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取研究决策"""
        try:
            research_decision = context.get("research_decision", {})

            return {
                "recommendation": research_decision.get("recommendation", "HOLD"),
                "confidence": research_decision.get("confidence", 0.5),
                "strategy": research_decision.get("strategy", ""),
                "reasoning": research_decision.get("reasoning", ""),
                "next_steps": research_decision.get("next_steps", [])
            }
        except Exception as e:
            self.logger.error(f"❌ 获取研究决策失败: {e}")
            return {"recommendation": "HOLD", "confidence": 0.5}

    async def _analyze_market_environment(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析市场环境"""
        try:
            market_data = context.get("market_report", {})

            # 获取当前市场数据
            current_price = 100.0  # 模拟价格
            volume = 1000000  # 模拟成交量
            volatility = 0.02  # 模拟波动率

            # 分析市场流动性
            liquidity_level = self._assess_liquidity(volume)

            # 分析市场波动性
            volatility_level = self._assess_volatility(volatility)

            # 分析交易时机
            timing_assessment = self._assess_timing(market_data)

            return {
                "current_price": current_price,
                "volume": volume,
                "volatility": volatility,
                "liquidity_level": liquidity_level,
                "volatility_level": volatility_level,
                "timing_assessment": timing_assessment,
                "market_trend": market_data.get("trend", "横盘"),
                "support_resistance": market_data.get("support_resistance", {})
            }
        except Exception as e:
            self.logger.error(f"❌ 市场环境分析失败: {e}")
            return {}

    def _assess_liquidity(self, volume: float) -> str:
        """评估流动性水平"""
        if volume > 5000000:
            return "高流动性"
        elif volume > 1000000:
            return "中等流动性"
        else:
            return "低流动性"

    def _assess_volatility(self, volatility: float) -> str:
        """评估波动性水平"""
        if volatility > 0.03:
            return "高波动"
        elif volatility > 0.015:
            return "中等波动"
        else:
            return "低波动"

    def _assess_timing(self, market_data: Dict) -> str:
        """评估交易时机"""
        recommendation = market_data.get("recommendation", "HOLD")
        confidence = market_data.get("confidence_score", 0.5)

        if recommendation == "买入" and confidence > 0.7:
            return "买入时机良好"
        elif recommendation == "卖出" and confidence > 0.7:
            return "卖出时机良好"
        else:
            return "时机不明确"

    async def _develop_trading_strategy(self, research_decision: Dict,
                                      market_environment: Dict) -> Dict[str, Any]:
        """制定交易策略"""
        try:
            recommendation = research_decision.get("recommendation", "HOLD")
            confidence = research_decision.get("confidence", 0.5)
            liquidity = market_environment.get("liquidity_level", "中等流动性")
            volatility = market_environment.get("volatility_level", "中等波动")

            # 基于研究决策确定交易行动
            if recommendation == "BUY":
                action = "买入"
                strategy_type = "积极买入策略"
            elif recommendation == "SELL":
                action = "卖出"
                strategy_type = "积极卖出策略"
            else:
                action = "观望"
                strategy_type = "观望策略"

            # 确定仓位大小
            position_size = self._calculate_position_size(confidence, volatility)

            # 确定执行方式
            execution_style = self._determine_execution_style(liquidity, volatility)

            return {
                "action": action,
                "strategy_type": strategy_type,
                "position_size": position_size,
                "execution_style": execution_style,
                "confidence_level": confidence,
                "risk_tolerance": self._assess_risk_tolerance(confidence, volatility)
            }
        except Exception as e:
            self.logger.error(f"❌ 交易策略制定失败: {e}")
            return {"action": "观望", "strategy_type": "保守策略"}

    def _calculate_position_size(self, confidence: float, volatility: str) -> str:
        """计算仓位大小"""
        base_size = confidence

        # 根据波动性调整
        if volatility == "高波动":
            base_size *= 0.7
        elif volatility == "低波动":
            base_size *= 1.2

        if base_size > 0.8:
            return "大仓位"
        elif base_size > 0.5:
            return "中等仓位"
        else:
            return "小仓位"

    def _determine_execution_style(self, liquidity: str, volatility: str) -> str:
        """确定执行方式"""
        if liquidity == "高流动性" and volatility == "低波动":
            return "市价执行"
        elif liquidity == "低流动性" or volatility == "高波动":
            return "分批执行"
        else:
            return "限价执行"

    def _assess_risk_tolerance(self, confidence: float, volatility: str) -> str:
        """评估风险承受能力"""
        if confidence > 0.7 and volatility != "高波动":
            return "高风险承受"
        elif confidence < 0.4 or volatility == "高波动":
            return "低风险承受"
        else:
            return "中等风险承受"

    async def _design_execution_plan(self, symbol: str, trading_strategy: Dict,
                                   market_environment: Dict) -> Dict[str, Any]:
        """设计执行计划"""
        try:
            action = trading_strategy.get("action", "观望")
            execution_style = trading_strategy.get("execution_style", "限价执行")
            position_size = trading_strategy.get("position_size", "中等仓位")
            current_price = market_environment.get("current_price", 100.0)

            if action == "观望":
                return {
                    "action": "观望",
                    "priority": "LOW",
                    "timeline": "持续观察",
                    "execution_steps": ["监控市场变化", "等待更明确信号"]
                }

            # 制定具体执行计划
            execution_plan = {
                "action": action,
                "target_price": self._calculate_target_price(action, current_price),
                "execution_style": execution_style,
                "position_size": position_size,
                "priority": self._determine_priority(trading_strategy),
                "timeline": self._estimate_timeline(execution_style, position_size),
                "execution_steps": self._generate_execution_steps(action, execution_style),
                "market_conditions": self._define_market_conditions(action)
            }

            return execution_plan
        except Exception as e:
            self.logger.error(f"❌ 执行计划设计失败: {e}")
            return {"action": "观望", "priority": "LOW"}

    def _calculate_target_price(self, action: str, current_price: float) -> Dict[str, float]:
        """计算目标价格"""
        if action == "买入":
            return {
                "limit_price": current_price * 0.98,  # 限价买入价
                "stop_price": current_price * 1.02    # 止损价
            }
        elif action == "卖出":
            return {
                "limit_price": current_price * 1.02,  # 限价卖出价
                "stop_price": current_price * 0.98    # 止损价
            }
        else:
            return {"current_price": current_price}

    def _determine_priority(self, trading_strategy: Dict) -> str:
        """确定执行优先级"""
        confidence = trading_strategy.get("confidence_level", 0.5)
        risk_tolerance = trading_strategy.get("risk_tolerance", "中等风险承受")

        if confidence > 0.8 and risk_tolerance == "高风险承受":
            return "HIGH"
        elif confidence > 0.6:
            return "MEDIUM"
        else:
            return "LOW"

    def _estimate_timeline(self, execution_style: str, position_size: str) -> str:
        """估算执行时间"""
        if execution_style == "市价执行":
            return "立即执行"
        elif execution_style == "分批执行":
            if position_size == "大仓位":
                return "3-5天"
            else:
                return "1-3天"
        else:  # 限价执行
            return "1-2天"

    def _generate_execution_steps(self, action: str, execution_style: str) -> List[str]:
        """生成执行步骤"""
        if action == "买入":
            if execution_style == "分批执行":
                return [
                    "第一批：买入30%仓位",
                    "观察市场反应",
                    "第二批：买入40%仓位",
                    "第三批：买入剩余30%仓位"
                ]
            else:
                return [
                    "设置买入价格",
                    "提交买入订单",
                    "监控执行状态",
                    "确认成交情况"
                ]
        elif action == "卖出":
            if execution_style == "分批执行":
                return [
                    "第一批：卖出40%仓位",
                    "观察市场反应",
                    "第二批：卖出35%仓位",
                    "第三批：卖出剩余25%仓位"
                ]
            else:
                return [
                    "设置卖出价格",
                    "提交卖出订单",
                    "监控执行状态",
                    "确认成交情况"
                ]
        else:
            return ["持续观察市场", "等待交易信号"]

    def _define_market_conditions(self, action: str) -> List[str]:
        """定义市场条件"""
        if action == "买入":
            return [
                "市场情绪稳定",
                "成交量充足",
                "技术指标支持",
                "无重大负面消息"
            ]
        elif action == "卖出":
            return [
                "获利了结时机",
                "风险信号出现",
                "技术指标转弱",
                "基本面恶化"
            ]
        else:
            return ["市场方向不明", "等待更多信息"]

    async def _design_risk_controls(self, symbol: str, trading_strategy: Dict,
                                  execution_plan: Dict) -> Dict[str, Any]:
        """设计风险控制措施"""
        try:
            action = trading_strategy.get("action", "观望")
            position_size = trading_strategy.get("position_size", "中等仓位")
            target_price = execution_plan.get("target_price", {})

            if action == "观望":
                return {
                    "risk_level": "低",
                    "controls": ["持续监控", "保持观望"]
                }

            # 设计风险控制
            risk_controls = {
                "stop_loss": self._calculate_stop_loss(action, target_price),
                "take_profit": self._calculate_take_profit(action, target_price),
                "position_limits": self._set_position_limits(position_size),
                "time_limits": self._set_time_limits(execution_plan.get("timeline", "1-3天")),
                "monitoring_alerts": self._set_monitoring_alerts(action),
                "emergency_exit": self._define_emergency_exit(action)
            }

            return risk_controls
        except Exception as e:
            self.logger.error(f"❌ 风险控制设计失败: {e}")
            return {"risk_level": "中", "controls": ["基础风险控制"]}

    def _calculate_stop_loss(self, action: str, target_price: Dict) -> Dict[str, Any]:
        """计算止损"""
        if action == "买入":
            return {
                "type": "止损卖出",
                "trigger_price": target_price.get("stop_price", 0),
                "loss_limit": "5%"
            }
        elif action == "卖出":
            return {
                "type": "止损买入",
                "trigger_price": target_price.get("stop_price", 0),
                "loss_limit": "3%"
            }
        else:
            return {"type": "无需止损"}

    def _calculate_take_profit(self, action: str, target_price: Dict) -> Dict[str, Any]:
        """计算止盈"""
        if action == "买入":
            return {
                "type": "止盈卖出",
                "target_return": "10-15%",
                "partial_profit": "达到8%时减仓50%"
            }
        elif action == "卖出":
            return {
                "type": "完成卖出",
                "target_return": "避免进一步损失",
                "completion_target": "全部卖出"
            }
        else:
            return {"type": "无需止盈"}

    def _set_position_limits(self, position_size: str) -> Dict[str, Any]:
        """设置仓位限制"""
        limits = {
            "大仓位": {"max_position": "20%", "single_trade": "8%"},
            "中等仓位": {"max_position": "15%", "single_trade": "5%"},
            "小仓位": {"max_position": "10%", "single_trade": "3%"}
        }

        return limits.get(position_size, limits["中等仓位"])

    def _set_time_limits(self, timeline: str) -> Dict[str, str]:
        """设置时间限制"""
        return {
            "execution_deadline": timeline,
            "review_frequency": "每日复盘",
            "strategy_review": "每周评估"
        }

    def _set_monitoring_alerts(self, action: str) -> List[str]:
        """设置监控警报"""
        common_alerts = [
            "价格异常波动警报",
            "成交量异常警报",
            "重大新闻警报"
        ]

        if action == "买入":
            common_alerts.extend([
                "买入价格触发警报",
                "止损价格警报"
            ])
        elif action == "卖出":
            common_alerts.extend([
                "卖出价格触发警报",
                "止盈价格警报"
            ])

        return common_alerts

    def _define_emergency_exit(self, action: str) -> Dict[str, str]:
        """定义紧急退出"""
        if action == "买入":
            return {
                "trigger": "重大负面消息或技术破位",
                "action": "立即止损卖出",
                "execution": "市价单执行"
            }
        elif action == "卖出":
            return {
                "trigger": "卖出计划受阻或市场急跌",
                "action": "加速卖出或暂停卖出",
                "execution": "根据市场情况调整"
            }
        else:
            return {
                "trigger": "市场极端情况",
                "action": "保持观望",
                "execution": "等待市场稳定"
            }

    async def _generate_ai_analysis(self, symbol: str, research_decision: Dict,
                                  market_environment: Dict, trading_strategy: Dict) -> str:
        """生成AI交易分析"""
        try:
            if self.llm_client:
                prompt = self.prompt_template.format(
                    symbol=symbol,
                    research_decision=str(research_decision),
                    market_environment=str(market_environment),
                    technical_analysis=str(market_environment)
                )

                response = await self.llm_client.generate(
                    prompt=prompt,
                    context={"trading_strategy": trading_strategy}
                )

                return response.get("content", "AI分析生成失败")
            else:
                # 模拟AI分析
                action = trading_strategy.get("action", "观望")
                strategy_type = trading_strategy.get("strategy_type", "保守策略")
                execution_style = trading_strategy.get("execution_style", "限价执行")
                position_size = trading_strategy.get("position_size", "中等仓位")

                return f"""
## {symbol} 交易执行分析报告

### 交易策略概述
- 交易行动: {action}
- 策略类型: {strategy_type}
- 仓位大小: {position_size}
- 执行方式: {execution_style}

### 市场环境分析
- 当前价格: {market_environment.get('current_price', 100.0)}
- 流动性水平: {market_environment.get('liquidity_level', '中等流动性')}
- 波动性水平: {market_environment.get('volatility_level', '中等波动')}
- 交易时机: {market_environment.get('timing_assessment', '时机不明确')}

### 执行建议
基于研究决策"{research_decision.get('recommendation', 'HOLD')}"和当前市场环境，
建议采用{strategy_type}，{'立即执行' if action != '观望' else '继续观望'}。

### 风险控制要点
- 严格执行止损策略
- 控制单笔交易仓位
- 密切监控市场变化
- 及时调整执行计划

### 执行时机建议
{'当前市场条件适合执行' if market_environment.get('timing_assessment') == '买入时机良好' or market_environment.get('timing_assessment') == '卖出时机良好' else '建议等待更好的执行时机'}，
{'可以按计划执行交易策略' if action != '观望' else '保持观望直到出现明确信号'}。

### 注意事项
- 关注市场流动性变化
- 监控交易成本控制
- 准备应急执行预案
- 定期评估策略效果
"""
        except Exception as e:
            self.logger.error(f"❌ AI分析生成失败: {e}")
            return f"AI分析生成失败: {str(e)}"
