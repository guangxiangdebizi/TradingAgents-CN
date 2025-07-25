"""
风险管理经理智能体
移植自tradingagents，负责风险评估和最终投资决策
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..base.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class RiskManager(BaseAgent):
    """
    风险管理经理智能体
    负责综合风险评估、投资决策审核和最终投资建议
    """

    def __init__(self, llm_client=None, data_client=None):
        super().__init__(
            name="RiskManager",
            description="专业的风险管理经理，负责风险评估和最终投资决策",
            llm_client=llm_client,
            data_client=data_client
        )
        self.prompt_template = None

    async def _load_prompts(self):
        """加载风险管理提示词模板"""
        self.prompt_template = """
你是一位专业的风险管理经理，具有丰富的投资风险控制和决策审核经验。

请对股票 {symbol} 进行最终的风险评估和投资决策：

## 分析要求：
1. **综合风险评估**：整合所有风险因素进行全面评估
2. **投资决策审核**：审核研究团队和交易员的建议
3. **风险收益平衡**：确保风险与收益的合理匹配
4. **合规性检查**：确保投资决策符合风险管理要求
5. **最终决策**：基于风险控制原则做出最终投资决策
6. **监控建议**：制定后续风险监控和管理措施

## 团队分析汇总：
### 研究决策：
{research_decision}

### 交易策略：
{trading_strategy}

### 风险因素：
{risk_factors}

## 输出格式：
请提供详细的风险管理报告和最终投资决策。

## 最终决策：
基于风险管理原则给出明确的最终投资建议和风险控制措施。
"""

    async def analyze(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行风险管理分析

        Args:
            symbol: 股票代码
            context: 分析上下文，包含所有团队的分析结果

        Returns:
            风险管理结果和最终投资决策
        """
        self._log_analysis_start(symbol)

        try:
            # 1. 收集所有分析结果
            all_analysis = await self._collect_all_analysis(context)

            # 2. 综合风险评估
            comprehensive_risk = await self._comprehensive_risk_assessment(all_analysis)

            # 3. 审核投资建议
            decision_review = await self._review_investment_decisions(all_analysis)

            # 4. 风险收益分析
            risk_return_analysis = await self._analyze_risk_return(
                comprehensive_risk, decision_review
            )

            # 5. 制定最终决策
            final_decision = await self._make_final_decision(
                comprehensive_risk, decision_review, risk_return_analysis
            )

            # 6. 生成AI风险分析
            ai_analysis = await self._generate_ai_analysis(
                symbol, all_analysis, comprehensive_risk, final_decision
            )

            # 7. 整合最终结果
            result = {
                "analysis_type": "risk_management",
                "symbol": symbol,
                "analyst": self.name,
                "timestamp": datetime.now().isoformat(),
                "comprehensive_risk": comprehensive_risk,
                "decision_review": decision_review,
                "risk_return_analysis": risk_return_analysis,
                "final_decision": final_decision,
                "ai_analysis": ai_analysis,
                "final_recommendation": final_decision.get("recommendation", "HOLD"),
                "risk_level": comprehensive_risk.get("overall_risk", "MEDIUM"),
                "confidence_score": final_decision.get("confidence", 0.5),
                "monitoring_plan": final_decision.get("monitoring_plan", [])
            }

            self._log_analysis_complete(symbol, f"最终决策: {result['final_recommendation']}")
            return result

        except Exception as e:
            self.logger.error(f"❌ [{self.name}] 分析失败: {symbol} - {e}")
            return {
                "analysis_type": "risk_management",
                "symbol": symbol,
                "analyst": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _collect_all_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """收集所有分析结果"""
        try:
            return {
                "market_analysis": context.get("technical_report", {}),
                "fundamentals_analysis": context.get("fundamentals_report", {}),
                "news_analysis": context.get("news_report", {}),
                "social_analysis": context.get("social_report", {}),
                "bull_research": context.get("bull_opinion", {}),
                "bear_research": context.get("bear_opinion", {}),
                "research_decision": context.get("research_decision", {}),
                "trading_strategy": context.get("investment_plan", {})
            }
        except Exception as e:
            self.logger.error(f"❌ 收集分析结果失败: {e}")
            return {}

    async def _comprehensive_risk_assessment(self, all_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """综合风险评估"""
        try:
            # 收集各类风险
            market_risks = self._assess_market_risks(all_analysis.get("market_analysis", {}))
            fundamental_risks = self._assess_fundamental_risks(all_analysis.get("fundamentals_analysis", {}))
            news_risks = self._assess_news_risks(all_analysis.get("news_analysis", {}))
            sentiment_risks = self._assess_sentiment_risks(all_analysis.get("social_analysis", {}))
            research_risks = self._assess_research_risks(all_analysis.get("bear_research", {}))
            execution_risks = self._assess_execution_risks(all_analysis.get("trading_strategy", {}))

            # 计算综合风险等级
            overall_risk = self._calculate_overall_risk([
                market_risks, fundamental_risks, news_risks,
                sentiment_risks, research_risks, execution_risks
            ])

            return {
                "market_risks": market_risks,
                "fundamental_risks": fundamental_risks,
                "news_risks": news_risks,
                "sentiment_risks": sentiment_risks,
                "research_risks": research_risks,
                "execution_risks": execution_risks,
                "overall_risk": overall_risk,
                "risk_summary": self._generate_risk_summary(overall_risk),
                "key_risk_factors": self._identify_key_risk_factors([
                    market_risks, fundamental_risks, news_risks,
                    sentiment_risks, research_risks, execution_risks
                ])
            }
        except Exception as e:
            self.logger.error(f"❌ 综合风险评估失败: {e}")
            return {"overall_risk": "MEDIUM"}

    def _assess_market_risks(self, market_analysis: Dict) -> Dict[str, Any]:
        """评估市场风险"""
        recommendation = market_analysis.get("recommendation", "持有")
        confidence = market_analysis.get("confidence_score", 0.5)

        if recommendation == "卖出" or confidence < 0.4:
            risk_level = "HIGH"
        elif recommendation == "买入" and confidence > 0.7:
            risk_level = "LOW"
        else:
            risk_level = "MEDIUM"

        return {
            "risk_level": risk_level,
            "factors": [
                f"技术分析建议: {recommendation}",
                f"分析置信度: {confidence:.2f}"
            ]
        }

    def _assess_fundamental_risks(self, fundamentals_analysis: Dict) -> Dict[str, Any]:
        """评估基本面风险"""
        investment_grade = fundamentals_analysis.get("investment_grade", "B级")
        valuation = fundamentals_analysis.get("valuation", "合理估值")

        if investment_grade == "C级" or "高估" in valuation:
            risk_level = "HIGH"
        elif investment_grade == "A级" and "低估" in valuation:
            risk_level = "LOW"
        else:
            risk_level = "MEDIUM"

        return {
            "risk_level": risk_level,
            "factors": [
                f"投资评级: {investment_grade}",
                f"估值水平: {valuation}"
            ]
        }

    def _assess_news_risks(self, news_analysis: Dict) -> Dict[str, Any]:
        """评估新闻风险"""
        market_sentiment = news_analysis.get("market_sentiment", "neutral")
        impact_score = news_analysis.get("news_impact_score", 0.5)

        if market_sentiment == "negative" and impact_score > 0.7:
            risk_level = "HIGH"
        elif market_sentiment == "positive" and impact_score > 0.7:
            risk_level = "LOW"
        else:
            risk_level = "MEDIUM"

        return {
            "risk_level": risk_level,
            "factors": [
                f"新闻情绪: {market_sentiment}",
                f"影响程度: {impact_score:.2f}"
            ]
        }

    def _assess_sentiment_risks(self, social_analysis: Dict) -> Dict[str, Any]:
        """评估情绪风险"""
        retail_sentiment = social_analysis.get("retail_sentiment", "中性")
        discussion_trend = social_analysis.get("discussion_trend", "中")

        if retail_sentiment == "悲观" and discussion_trend == "高":
            risk_level = "HIGH"
        elif retail_sentiment == "乐观" and discussion_trend == "高":
            risk_level = "LOW"
        else:
            risk_level = "MEDIUM"

        return {
            "risk_level": risk_level,
            "factors": [
                f"散户情绪: {retail_sentiment}",
                f"讨论热度: {discussion_trend}"
            ]
        }

    def _assess_research_risks(self, bear_research: Dict) -> Dict[str, Any]:
        """评估研究风险"""
        risk_level = bear_research.get("risk_level", "中")
        bear_factors_count = len(bear_research.get("bear_factors", []))

        if risk_level == "高" or bear_factors_count >= 4:
            research_risk = "HIGH"
        elif risk_level == "低" and bear_factors_count <= 2:
            research_risk = "LOW"
        else:
            research_risk = "MEDIUM"

        return {
            "risk_level": research_risk,
            "factors": [
                f"看跌风险等级: {risk_level}",
                f"风险因素数量: {bear_factors_count}"
            ]
        }

    def _assess_execution_risks(self, trading_strategy: Dict) -> Dict[str, Any]:
        """评估执行风险"""
        execution_priority = trading_strategy.get("execution_priority", "NORMAL")
        position_size = trading_strategy.get("position_size", "中等仓位")

        if execution_priority == "HIGH" and position_size == "大仓位":
            risk_level = "HIGH"
        elif execution_priority == "LOW" and position_size == "小仓位":
            risk_level = "LOW"
        else:
            risk_level = "MEDIUM"

        return {
            "risk_level": risk_level,
            "factors": [
                f"执行优先级: {execution_priority}",
                f"仓位大小: {position_size}"
            ]
        }

    def _calculate_overall_risk(self, risk_assessments: List[Dict]) -> str:
        """计算综合风险等级"""
        try:
            risk_scores = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
            total_score = 0
            valid_assessments = 0

            for assessment in risk_assessments:
                if assessment and "risk_level" in assessment:
                    total_score += risk_scores.get(assessment["risk_level"], 2)
                    valid_assessments += 1

            if valid_assessments == 0:
                return "MEDIUM"

            average_score = total_score / valid_assessments

            if average_score >= 2.5:
                return "HIGH"
            elif average_score <= 1.5:
                return "LOW"
            else:
                return "MEDIUM"
        except:
            return "MEDIUM"

    def _generate_risk_summary(self, overall_risk: str) -> str:
        """生成风险摘要"""
        summaries = {
            "HIGH": "整体风险较高，需要谨慎投资并加强风险控制",
            "MEDIUM": "整体风险适中，可以考虑投资但需要密切监控",
            "LOW": "整体风险较低，投资环境相对安全"
        }
        return summaries.get(overall_risk, "风险水平需要进一步评估")

    def _identify_key_risk_factors(self, risk_assessments: List[Dict]) -> List[str]:
        """识别关键风险因素"""
        key_factors = []

        for assessment in risk_assessments:
            if assessment and assessment.get("risk_level") == "HIGH":
                factors = assessment.get("factors", [])
                key_factors.extend(factors)

        return key_factors[:5]  # 返回前5个关键风险因素

    async def _review_investment_decisions(self, all_analysis: Dict) -> Dict[str, Any]:
        """审核投资决策"""
        try:
            research_decision = all_analysis.get("research_decision", {})
            trading_strategy = all_analysis.get("trading_strategy", {})

            # 审核研究决策
            research_review = self._review_research_decision(research_decision)

            # 审核交易策略
            trading_review = self._review_trading_strategy(trading_strategy)

            # 一致性检查
            consistency_check = self._check_consistency(research_decision, trading_strategy)

            return {
                "research_review": research_review,
                "trading_review": trading_review,
                "consistency_check": consistency_check,
                "overall_assessment": self._assess_decision_quality(
                    research_review, trading_review, consistency_check
                )
            }
        except Exception as e:
            self.logger.error(f"❌ 投资决策审核失败: {e}")
            return {}

    def _review_research_decision(self, research_decision: Dict) -> Dict[str, Any]:
        """审核研究决策"""
        recommendation = research_decision.get("recommendation", "HOLD")
        confidence = research_decision.get("confidence", 0.5)
        reasoning = research_decision.get("reasoning", "")

        # 评估决策质量
        if confidence > 0.7 and reasoning:
            quality = "HIGH"
        elif confidence > 0.5:
            quality = "MEDIUM"
        else:
            quality = "LOW"

        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "quality": quality,
            "reasoning_quality": "充分" if reasoning else "不足"
        }

    def _review_trading_strategy(self, trading_strategy: Dict) -> Dict[str, Any]:
        """审核交易策略"""
        action = trading_strategy.get("trade_recommendation", "HOLD")
        execution_plan = trading_strategy.get("execution_plan", {})
        risk_controls = trading_strategy.get("risk_controls", {})

        # 评估策略完整性
        completeness = 0
        if execution_plan:
            completeness += 1
        if risk_controls:
            completeness += 1
        if action != "HOLD":
            completeness += 1

        quality = "HIGH" if completeness >= 3 else "MEDIUM" if completeness >= 2 else "LOW"

        return {
            "action": action,
            "quality": quality,
            "execution_plan_quality": "完整" if execution_plan else "缺失",
            "risk_control_quality": "完整" if risk_controls else "缺失"
        }

    def _check_consistency(self, research_decision: Dict, trading_strategy: Dict) -> Dict[str, Any]:
        """检查一致性"""
        research_rec = research_decision.get("recommendation", "HOLD")
        trading_action = trading_strategy.get("trade_recommendation", "HOLD")

        # 映射关系
        mapping = {"BUY": "买入", "SELL": "卖出", "HOLD": "观望"}
        research_mapped = mapping.get(research_rec, research_rec)
        trading_mapped = mapping.get(trading_action, trading_action)

        is_consistent = research_mapped == trading_mapped

        return {
            "is_consistent": is_consistent,
            "research_recommendation": research_rec,
            "trading_action": trading_action,
            "consistency_level": "高" if is_consistent else "低"
        }

    def _assess_decision_quality(self, research_review: Dict, trading_review: Dict,
                               consistency_check: Dict) -> str:
        """评估决策质量"""
        research_quality = research_review.get("quality", "MEDIUM")
        trading_quality = trading_review.get("quality", "MEDIUM")
        is_consistent = consistency_check.get("is_consistent", False)

        quality_scores = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

        total_score = (quality_scores.get(research_quality, 2) +
                      quality_scores.get(trading_quality, 2))

        if is_consistent:
            total_score += 1

        if total_score >= 6:
            return "优秀"
        elif total_score >= 4:
            return "良好"
        else:
            return "需要改进"

    async def _analyze_risk_return(self, comprehensive_risk: Dict,
                                 decision_review: Dict) -> Dict[str, Any]:
        """分析风险收益"""
        try:
            overall_risk = comprehensive_risk.get("overall_risk", "MEDIUM")
            decision_quality = decision_review.get("overall_assessment", "良好")

            # 风险收益评估
            risk_return_ratio = self._calculate_risk_return_ratio(overall_risk, decision_quality)

            return {
                "risk_level": overall_risk,
                "expected_return": self._estimate_expected_return(decision_quality),
                "risk_return_ratio": risk_return_ratio,
                "investment_attractiveness": self._assess_attractiveness(risk_return_ratio),
                "recommendation_adjustment": self._suggest_adjustment(overall_risk, decision_quality)
            }
        except Exception as e:
            self.logger.error(f"❌ 风险收益分析失败: {e}")
            return {}

    def _calculate_risk_return_ratio(self, risk_level: str, decision_quality: str) -> float:
        """计算风险收益比"""
        risk_scores = {"HIGH": 0.3, "MEDIUM": 0.6, "LOW": 0.9}
        quality_scores = {"优秀": 0.9, "良好": 0.7, "需要改进": 0.4}

        risk_score = risk_scores.get(risk_level, 0.6)
        quality_score = quality_scores.get(decision_quality, 0.7)

        return quality_score / (1 - risk_score + 0.1)  # 避免除零

    def _estimate_expected_return(self, decision_quality: str) -> str:
        """估算预期收益"""
        return {
            "优秀": "10-15%",
            "良好": "5-10%",
            "需要改进": "0-5%"
        }.get(decision_quality, "5-10%")

    def _assess_attractiveness(self, risk_return_ratio: float) -> str:
        """评估投资吸引力"""
        if risk_return_ratio > 1.5:
            return "高吸引力"
        elif risk_return_ratio > 1.0:
            return "中等吸引力"
        else:
            return "低吸引力"

    def _suggest_adjustment(self, risk_level: str, decision_quality: str) -> str:
        """建议调整"""
        if risk_level == "HIGH":
            return "建议降低仓位或暂缓投资"
        elif decision_quality == "需要改进":
            return "建议重新评估或获取更多信息"
        else:
            return "可按原计划执行"

    async def _make_final_decision(self, comprehensive_risk: Dict, decision_review: Dict,
                                 risk_return_analysis: Dict) -> Dict[str, Any]:
        """制定最终决策"""
        try:
            overall_risk = comprehensive_risk.get("overall_risk", "MEDIUM")
            decision_quality = decision_review.get("overall_assessment", "良好")
            attractiveness = risk_return_analysis.get("investment_attractiveness", "中等吸引力")
            adjustment = risk_return_analysis.get("recommendation_adjustment", "可按原计划执行")

            # 最终决策逻辑
            final_recommendation = self._determine_final_recommendation(
                overall_risk, decision_quality, attractiveness, adjustment
            )

            # 计算置信度
            confidence = self._calculate_final_confidence(
                overall_risk, decision_quality, attractiveness
            )

            # 制定监控计划
            monitoring_plan = self._create_monitoring_plan(overall_risk, final_recommendation)

            return {
                "recommendation": final_recommendation,
                "confidence": confidence,
                "reasoning": self._generate_decision_reasoning(
                    overall_risk, decision_quality, attractiveness, adjustment
                ),
                "risk_controls": self._define_risk_controls(final_recommendation, overall_risk),
                "monitoring_plan": monitoring_plan,
                "review_schedule": self._set_review_schedule(final_recommendation),
                "exit_conditions": self._define_exit_conditions(final_recommendation, overall_risk)
            }
        except Exception as e:
            self.logger.error(f"❌ 最终决策制定失败: {e}")
            return {
                "recommendation": "HOLD",
                "confidence": 0.5,
                "reasoning": "需要进一步分析"
            }

    def _determine_final_recommendation(self, risk_level: str, quality: str,
                                      attractiveness: str, adjustment: str) -> str:
        """确定最终建议"""
        # 如果建议暂缓投资，则采纳
        if "暂缓投资" in adjustment:
            return "HOLD"

        # 基于风险和吸引力决策
        if risk_level == "LOW" and attractiveness == "高吸引力":
            return "BUY"
        elif risk_level == "HIGH" or attractiveness == "低吸引力":
            return "SELL" if "降低仓位" in adjustment else "HOLD"
        elif quality == "优秀" and attractiveness == "中等吸引力":
            return "BUY"
        else:
            return "HOLD"

    def _calculate_final_confidence(self, risk_level: str, quality: str, attractiveness: str) -> float:
        """计算最终置信度"""
        base_confidence = 0.5

        # 风险调整
        if risk_level == "LOW":
            base_confidence += 0.2
        elif risk_level == "HIGH":
            base_confidence -= 0.2

        # 质量调整
        if quality == "优秀":
            base_confidence += 0.2
        elif quality == "需要改进":
            base_confidence -= 0.2

        # 吸引力调整
        if attractiveness == "高吸引力":
            base_confidence += 0.1
        elif attractiveness == "低吸引力":
            base_confidence -= 0.1

        return max(0.1, min(0.9, base_confidence))

    def _generate_decision_reasoning(self, risk_level: str, quality: str,
                                   attractiveness: str, adjustment: str) -> str:
        """生成决策推理"""
        return f"基于综合风险评估({risk_level})、决策质量({quality})、投资吸引力({attractiveness})，{adjustment}"

    def _define_risk_controls(self, recommendation: str, risk_level: str) -> List[str]:
        """定义风险控制措施"""
        controls = ["定期风险评估", "严格止损执行"]

        if recommendation == "BUY":
            controls.extend([
                "分批建仓",
                "设置止损位",
                "监控市场变化"
            ])
        elif recommendation == "SELL":
            controls.extend([
                "分批减仓",
                "关注市场流动性",
                "避免恐慌性抛售"
            ])

        if risk_level == "HIGH":
            controls.extend([
                "加强风险监控",
                "降低仓位上限",
                "准备应急预案"
            ])

        return controls

    def _create_monitoring_plan(self, risk_level: str, recommendation: str) -> List[str]:
        """创建监控计划"""
        plan = [
            "每日市场监控",
            "每周风险评估",
            "每月策略回顾"
        ]

        if risk_level == "HIGH":
            plan.insert(0, "实时风险监控")

        if recommendation != "HOLD":
            plan.append("执行进度跟踪")

        return plan

    def _set_review_schedule(self, recommendation: str) -> str:
        """设置复盘计划"""
        if recommendation == "BUY" or recommendation == "SELL":
            return "每周复盘，必要时调整策略"
        else:
            return "每两周复盘，关注市场变化"

    def _define_exit_conditions(self, recommendation: str, risk_level: str) -> List[str]:
        """定义退出条件"""
        conditions = []

        if recommendation == "BUY":
            conditions = [
                "达到目标收益率",
                "基本面发生重大变化",
                "技术面破位下跌"
            ]
        elif recommendation == "SELL":
            conditions = [
                "完成减仓目标",
                "市场情况好转",
                "出现更好投资机会"
            ]

        if risk_level == "HIGH":
            conditions.append("风险进一步恶化时立即退出")

        return conditions

    async def _generate_ai_analysis(self, symbol: str, all_analysis: Dict,
                                  comprehensive_risk: Dict, final_decision: Dict) -> str:
        """生成AI风险分析"""
        try:
            if self.llm_client:
                prompt = self.prompt_template.format(
                    symbol=symbol,
                    research_decision=str(all_analysis.get("research_decision", {})),
                    trading_strategy=str(all_analysis.get("trading_strategy", {})),
                    risk_factors=str(comprehensive_risk)
                )

                response = await self.llm_client.generate(
                    prompt=prompt,
                    context={"final_decision": final_decision}
                )

                return response.get("content", "AI分析生成失败")
            else:
                # 模拟AI分析
                recommendation = final_decision.get("recommendation", "HOLD")
                confidence = final_decision.get("confidence", 0.5)
                risk_level = comprehensive_risk.get("overall_risk", "MEDIUM")

                return f"""
## {symbol} 风险管理最终报告

### 综合风险评估
- 整体风险等级: {risk_level}
- 风险摘要: {comprehensive_risk.get('risk_summary', '风险适中')}
- 关键风险因素: {len(comprehensive_risk.get('key_risk_factors', []))}个

### 决策审核结果
- 研究决策质量: {all_analysis.get('research_decision', {}).get('quality', '良好')}
- 交易策略质量: {all_analysis.get('trading_strategy', {}).get('quality', '良好')}
- 决策一致性: {'高' if all_analysis.get('research_decision', {}).get('recommendation') == all_analysis.get('trading_strategy', {}).get('trade_recommendation') else '需要关注'}

### 最终投资决策
- 投资建议: {recommendation}
- 决策置信度: {confidence:.2%}
- 决策推理: {final_decision.get('reasoning', '基于综合分析')}

### 风险控制措施
{chr(10).join(f"- {control}" for control in final_decision.get('risk_controls', []))}

### 监控和复盘
- 监控计划: {', '.join(final_decision.get('monitoring_plan', []))}
- 复盘安排: {final_decision.get('review_schedule', '定期复盘')}

### 风险管理建议
作为风险管理经理，{'强烈建议执行该投资决策' if confidence > 0.7 else '建议谨慎执行该投资决策' if confidence > 0.5 else '建议重新评估投资决策'}，
同时严格执行风险控制措施，确保投资安全。
"""
        except Exception as e:
            self.logger.error(f"❌ AI分析生成失败: {e}")
            return f"AI分析生成失败: {str(e)}"
