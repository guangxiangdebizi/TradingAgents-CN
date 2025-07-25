"""
研究经理智能体
移植自tradingagents，负责协调研究团队和综合分析
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..base.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ResearchManager(BaseAgent):
    """
    研究经理智能体
    负责协调研究团队、综合分析结果并做出研究决策
    """

    def __init__(self, llm_client=None, data_client=None):
        super().__init__(
            name="ResearchManager",
            description="专业的研究经理，负责协调研究团队和综合分析",
            llm_client=llm_client,
            data_client=data_client
        )
        self.prompt_template = None

    async def _load_prompts(self):
        """加载研究管理提示词模板"""
        self.prompt_template = """
你是一位专业的研究经理，具有丰富的团队管理和投资研究经验。

请对股票 {symbol} 的研究团队分析结果进行综合评估和决策：

## 分析要求：
1. **团队协调**：整合看涨和看跌研究员的观点
2. **观点平衡**：客观评估多空双方的论据强度
3. **风险权衡**：平衡投资机会与投资风险
4. **决策制定**：基于综合分析做出研究决策
5. **质量控制**：确保研究质量和逻辑一致性
6. **策略建议**：提供明确的投资策略建议

## 研究团队报告：
### 看涨研究员观点：
{bull_research}

### 看跌研究员观点：
{bear_research}

### 基础分析数据：
{base_analysis}

## 输出格式：
请提供详细的研究管理报告，包含团队观点整合和最终决策。

## 投资决策：
基于综合研究给出明确的投资建议和执行策略。
"""

    async def analyze(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行研究管理分析

        Args:
            symbol: 股票代码
            context: 分析上下文，包含研究团队的报告

        Returns:
            研究管理结果
        """
        self._log_analysis_start(symbol)

        try:
            # 1. 收集研究团队报告
            team_reports = await self._collect_team_reports(context)

            # 2. 分析观点分歧
            viewpoint_analysis = await self._analyze_viewpoints(team_reports)

            # 3. 权衡投资机会与风险
            risk_opportunity_balance = await self._balance_risk_opportunity(team_reports)

            # 4. 生成AI综合分析
            ai_analysis = await self._generate_ai_analysis(
                symbol, team_reports, viewpoint_analysis, risk_opportunity_balance
            )

            # 5. 制定研究决策
            research_decision = await self._make_research_decision(
                team_reports, viewpoint_analysis, risk_opportunity_balance
            )

            # 6. 整合管理结果
            result = {
                "analysis_type": "research_management",
                "symbol": symbol,
                "analyst": self.name,
                "timestamp": datetime.now().isoformat(),
                "team_reports_summary": team_reports,
                "viewpoint_analysis": viewpoint_analysis,
                "risk_opportunity_balance": risk_opportunity_balance,
                "ai_analysis": ai_analysis,
                "research_decision": research_decision,
                "final_recommendation": research_decision.get("recommendation", "HOLD"),
                "confidence_level": research_decision.get("confidence", 0.5),
                "execution_strategy": research_decision.get("strategy", "")
            }

            self._log_analysis_complete(symbol, f"决策: {result['final_recommendation']}")
            return result

        except Exception as e:
            self.logger.error(f"❌ [{self.name}] 分析失败: {symbol} - {e}")
            return {
                "analysis_type": "research_management",
                "symbol": symbol,
                "analyst": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _collect_team_reports(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """收集研究团队报告"""
        try:
            return {
                "bull_research": context.get("bull_opinion", {}),
                "bear_research": context.get("bear_opinion", {}),
                "market_analysis": context.get("market_report", {}),
                "fundamentals_analysis": context.get("fundamentals_report", {}),
                "news_analysis": context.get("news_report", {}),
                "social_analysis": context.get("social_report", {})
            }
        except Exception as e:
            self.logger.error(f"❌ 收集团队报告失败: {e}")
            return {}

    async def _analyze_viewpoints(self, team_reports: Dict[str, Any]) -> Dict[str, Any]:
        """分析观点分歧"""
        try:
            bull_research = team_reports.get("bull_research", {})
            bear_research = team_reports.get("bear_research", {})

            # 提取看涨和看跌的关键观点
            bull_confidence = bull_research.get("confidence_level", "中")
            bear_risk_level = bear_research.get("risk_level", "中")

            # 分析观点强度
            bull_strength = self._assess_viewpoint_strength(bull_research, "bull")
            bear_strength = self._assess_viewpoint_strength(bear_research, "bear")

            # 计算观点分歧程度
            divergence_level = self._calculate_divergence(bull_strength, bear_strength)

            return {
                "bull_viewpoint": {
                    "confidence": bull_confidence,
                    "strength": bull_strength,
                    "key_factors": bull_research.get("bull_factors", [])
                },
                "bear_viewpoint": {
                    "risk_level": bear_risk_level,
                    "strength": bear_strength,
                    "key_risks": bear_research.get("bear_factors", [])
                },
                "divergence_level": divergence_level,
                "consensus_areas": self._find_consensus_areas(team_reports),
                "conflict_areas": self._find_conflict_areas(team_reports)
            }
        except Exception as e:
            self.logger.error(f"❌ 观点分析失败: {e}")
            return {}

    def _assess_viewpoint_strength(self, research_report: Dict, viewpoint_type: str) -> float:
        """评估观点强度"""
        try:
            if viewpoint_type == "bull":
                confidence = research_report.get("confidence_level", "中")
                factors_count = len(research_report.get("bull_factors", []))

                confidence_score = {"高": 0.8, "中": 0.5, "低": 0.2}.get(confidence, 0.5)
                factor_score = min(factors_count * 0.1, 0.3)

                return min(confidence_score + factor_score, 1.0)

            elif viewpoint_type == "bear":
                risk_level = research_report.get("risk_level", "中")
                factors_count = len(research_report.get("bear_factors", []))

                risk_score = {"高": 0.8, "中": 0.5, "低": 0.2}.get(risk_level, 0.5)
                factor_score = min(factors_count * 0.1, 0.3)

                return min(risk_score + factor_score, 1.0)

            return 0.5
        except:
            return 0.5

    def _calculate_divergence(self, bull_strength: float, bear_strength: float) -> str:
        """计算观点分歧程度"""
        try:
            divergence = abs(bull_strength - bear_strength)

            if divergence > 0.4:
                return "高分歧"
            elif divergence > 0.2:
                return "中等分歧"
            else:
                return "低分歧"
        except:
            return "中等分歧"

    def _find_consensus_areas(self, team_reports: Dict) -> List[str]:
        """找出共识领域"""
        consensus = []

        # 检查基本面共识
        fundamentals = team_reports.get("fundamentals_analysis", {})
        if fundamentals.get("investment_grade") in ["A级", "B级"]:
            consensus.append("基本面相对稳健")

        # 检查新闻情绪共识
        news = team_reports.get("news_analysis", {})
        if news.get("market_sentiment") in ["positive", "negative"]:
            consensus.append(f"新闻情绪{news.get('market_sentiment')}")

        return consensus

    def _find_conflict_areas(self, team_reports: Dict) -> List[str]:
        """找出冲突领域"""
        conflicts = []

        bull_research = team_reports.get("bull_research", {})
        bear_research = team_reports.get("bear_research", {})

        # 检查估值观点冲突
        if bull_research.get("target_price_range") and bear_research.get("downside_risk_range"):
            conflicts.append("价格预期存在分歧")

        # 检查风险评估冲突
        bull_confidence = bull_research.get("confidence_level", "")
        bear_risk = bear_research.get("risk_level", "")

        if bull_confidence == "高" and bear_risk == "高":
            conflicts.append("机会与风险评估存在冲突")

        return conflicts

    async def _balance_risk_opportunity(self, team_reports: Dict) -> Dict[str, Any]:
        """权衡投资机会与风险"""
        try:
            bull_research = team_reports.get("bull_research", {})
            bear_research = team_reports.get("bear_research", {})

            # 机会评估
            opportunity_level = bull_research.get("confidence_level", "中")
            opportunity_factors = len(bull_research.get("bull_factors", []))

            # 风险评估
            risk_level = bear_research.get("risk_level", "中")
            risk_factors = len(bear_research.get("bear_factors", []))

            # 计算风险收益比
            risk_opportunity_ratio = self._calculate_risk_opportunity_ratio(
                opportunity_level, risk_level, opportunity_factors, risk_factors
            )

            return {
                "opportunity_assessment": {
                    "level": opportunity_level,
                    "factors_count": opportunity_factors,
                    "score": self._level_to_score(opportunity_level)
                },
                "risk_assessment": {
                    "level": risk_level,
                    "factors_count": risk_factors,
                    "score": self._level_to_score(risk_level)
                },
                "risk_opportunity_ratio": risk_opportunity_ratio,
                "balance_conclusion": self._get_balance_conclusion(risk_opportunity_ratio)
            }
        except Exception as e:
            self.logger.error(f"❌ 风险机会权衡失败: {e}")
            return {}

    def _level_to_score(self, level: str) -> float:
        """将等级转换为分数"""
        return {"高": 0.8, "中": 0.5, "低": 0.2}.get(level, 0.5)

    def _calculate_risk_opportunity_ratio(self, opp_level: str, risk_level: str,
                                        opp_factors: int, risk_factors: int) -> float:
        """计算风险收益比"""
        try:
            opp_score = self._level_to_score(opp_level) + min(opp_factors * 0.1, 0.3)
            risk_score = self._level_to_score(risk_level) + min(risk_factors * 0.1, 0.3)

            if risk_score == 0:
                return 1.0

            return opp_score / risk_score
        except:
            return 1.0

    def _get_balance_conclusion(self, ratio: float) -> str:
        """获取平衡结论"""
        if ratio > 1.3:
            return "机会大于风险"
        elif ratio < 0.7:
            return "风险大于机会"
        else:
            return "风险机会相当"

    async def _make_research_decision(self, team_reports: Dict, viewpoint_analysis: Dict,
                                    risk_opportunity_balance: Dict) -> Dict[str, Any]:
        """制定研究决策"""
        try:
            # 基于综合分析制定决策
            balance_conclusion = risk_opportunity_balance.get("balance_conclusion", "风险机会相当")
            divergence_level = viewpoint_analysis.get("divergence_level", "中等分歧")

            # 决策逻辑
            if balance_conclusion == "机会大于风险" and divergence_level != "高分歧":
                recommendation = "BUY"
                confidence = 0.7
                strategy = "积极买入，关注风险控制"
            elif balance_conclusion == "风险大于机会" and divergence_level != "高分歧":
                recommendation = "SELL"
                confidence = 0.7
                strategy = "建议减持，规避风险"
            elif divergence_level == "高分歧":
                recommendation = "HOLD"
                confidence = 0.4
                strategy = "观点分歧较大，建议观望"
            else:
                recommendation = "HOLD"
                confidence = 0.5
                strategy = "风险机会相当，保持现有仓位"

            return {
                "recommendation": recommendation,
                "confidence": confidence,
                "strategy": strategy,
                "reasoning": self._generate_decision_reasoning(
                    balance_conclusion, divergence_level, viewpoint_analysis
                ),
                "next_steps": self._suggest_next_steps(recommendation),
                "monitoring_points": self._identify_monitoring_points(team_reports)
            }
        except Exception as e:
            self.logger.error(f"❌ 研究决策制定失败: {e}")
            return {
                "recommendation": "HOLD",
                "confidence": 0.5,
                "strategy": "需要进一步分析"
            }

    def _generate_decision_reasoning(self, balance_conclusion: str, divergence_level: str,
                                   viewpoint_analysis: Dict) -> str:
        """生成决策推理"""
        reasoning_parts = [
            f"风险机会评估: {balance_conclusion}",
            f"团队观点分歧: {divergence_level}"
        ]

        consensus_areas = viewpoint_analysis.get("consensus_areas", [])
        if consensus_areas:
            reasoning_parts.append(f"共识领域: {', '.join(consensus_areas)}")

        conflict_areas = viewpoint_analysis.get("conflict_areas", [])
        if conflict_areas:
            reasoning_parts.append(f"分歧领域: {', '.join(conflict_areas)}")

        return "; ".join(reasoning_parts)

    def _suggest_next_steps(self, recommendation: str) -> List[str]:
        """建议下一步行动"""
        if recommendation == "BUY":
            return [
                "制定具体的买入计划",
                "设定止损位和目标价",
                "监控关键风险因素"
            ]
        elif recommendation == "SELL":
            return [
                "制定减仓计划",
                "评估退出时机",
                "寻找替代投资机会"
            ]
        else:  # HOLD
            return [
                "持续监控市场变化",
                "等待更明确的信号",
                "准备应对各种情况"
            ]

    def _identify_monitoring_points(self, team_reports: Dict) -> List[str]:
        """识别监控要点"""
        monitoring_points = []

        # 基于基本面分析的监控点
        fundamentals = team_reports.get("fundamentals_analysis", {})
        if fundamentals.get("investment_grade") == "B级":
            monitoring_points.append("关注财务指标变化")

        # 基于新闻分析的监控点
        news = team_reports.get("news_analysis", {})
        if news.get("news_impact_score", 0) > 0.7:
            monitoring_points.append("密切关注新闻动态")

        # 基于技术分析的监控点
        market = team_reports.get("market_analysis", {})
        if market.get("confidence_score", 0) < 0.6:
            monitoring_points.append("关注技术指标变化")

        # 默认监控点
        if not monitoring_points:
            monitoring_points = [
                "关注市场整体走势",
                "监控行业政策变化",
                "跟踪公司基本面动态"
            ]

        return monitoring_points

    async def _generate_ai_analysis(self, symbol: str, team_reports: Dict,
                                  viewpoint_analysis: Dict, risk_opportunity_balance: Dict) -> str:
        """生成AI综合分析"""
        try:
            if self.llm_client:
                prompt = self.prompt_template.format(
                    symbol=symbol,
                    bull_research=str(team_reports.get("bull_research", {})),
                    bear_research=str(team_reports.get("bear_research", {})),
                    base_analysis=str({
                        "market": team_reports.get("market_analysis", {}),
                        "fundamentals": team_reports.get("fundamentals_analysis", {}),
                        "news": team_reports.get("news_analysis", {}),
                        "social": team_reports.get("social_analysis", {})
                    })
                )

                response = await self.llm_client.generate(
                    prompt=prompt,
                    context={
                        "viewpoint_analysis": viewpoint_analysis,
                        "risk_opportunity_balance": risk_opportunity_balance
                    }
                )

                return response.get("content", "AI分析生成失败")
            else:
                # 模拟AI分析
                balance_conclusion = risk_opportunity_balance.get("balance_conclusion", "风险机会相当")
                divergence_level = viewpoint_analysis.get("divergence_level", "中等分歧")

                bull_viewpoint = viewpoint_analysis.get("bull_viewpoint", {})
                bear_viewpoint = viewpoint_analysis.get("bear_viewpoint", {})

                return f"""
## {symbol} 研究管理综合报告

### 团队观点整合
- 看涨研究员信心: {bull_viewpoint.get('confidence', '中')}
- 看跌研究员风险评估: {bear_viewpoint.get('risk_level', '中')}
- 观点分歧程度: {divergence_level}

### 风险机会权衡
- 综合评估: {balance_conclusion}
- 机会评估: {risk_opportunity_balance.get('opportunity_assessment', {}).get('level', '中')}
- 风险评估: {risk_opportunity_balance.get('risk_assessment', {}).get('level', '中')}

### 共识与分歧
- 团队共识: {', '.join(viewpoint_analysis.get('consensus_areas', ['基本面分析']))}
- 主要分歧: {', '.join(viewpoint_analysis.get('conflict_areas', ['价格预期']))}

### 质量控制
研究团队的分析质量{'较高' if divergence_level != '高分歧' else '需要改进'}，
{'观点相对一致' if divergence_level == '低分歧' else '存在一定分歧' if divergence_level == '中等分歧' else '观点分歧较大'}。

### 管理决策
基于团队综合分析，建议{'积极关注投资机会' if balance_conclusion == '机会大于风险' else '重点关注投资风险' if balance_conclusion == '风险大于机会' else '保持谨慎平衡的态度'}。

### 执行建议
{'可考虑适度增加仓位' if balance_conclusion == '机会大于风险' else '建议适度降低仓位' if balance_conclusion == '风险大于机会' else '维持当前仓位配置'}，
同时密切关注市场变化和风险因素。
"""
        except Exception as e:
            self.logger.error(f"❌ AI分析生成失败: {e}")
            return f"AI分析生成失败: {str(e)}"
