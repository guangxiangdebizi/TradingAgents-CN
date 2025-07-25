"""
看跌研究员智能体
移植自tradingagents，专注于风险识别和看跌因素分析
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..base.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class BearResearcher(BaseAgent):
    """
    看跌研究员智能体
    专注于风险识别、看跌因素分析和投资风险评估
    """

    def __init__(self, llm_client=None, data_client=None):
        super().__init__(
            name="BearResearcher",
            description="专业的看跌研究员，擅长风险识别和看跌因素分析",
            llm_client=llm_client,
            data_client=data_client
        )
        self.prompt_template = None

    async def _load_prompts(self):
        """加载看跌研究提示词模板"""
        self.prompt_template = """
你是一位专业的看跌研究员，具有丰富的风险识别和投资风险评估经验。

请对股票 {symbol} 进行看跌因素分析，重点关注：

## 分析要求：
1. **基本面风险**：财务数据中的负面因素和风险点
2. **技术面风险**：技术指标显示的卖出信号和风险
3. **风险事件**：可能导致股价下跌的风险事件
4. **行业风险**：行业发展瓶颈和政策风险
5. **估值风险**：高估值风险和泡沫风险
6. **流动性风险**：市场流动性和资金面风险

## 分析数据：
{analysis_data}

## 风险环境：
{risk_context}

## 输出格式：
请提供详细的看跌研究报告，重点突出风险点和下跌逻辑。

## 风险提示：
基于看跌因素给出具体的风险警示和防范建议。
"""

    async def analyze(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行看跌研究分析

        Args:
            symbol: 股票代码
            context: 分析上下文，包含其他分析师的报告

        Returns:
            看跌研究结果
        """
        self._log_analysis_start(symbol)

        try:
            # 1. 整合其他分析师的数据
            analysis_data = await self._integrate_analysis_data(context)

            # 2. 识别看跌因素
            bear_factors = await self._identify_bear_factors(analysis_data)

            # 3. 评估投资风险
            risk_assessment = await self._evaluate_risks(bear_factors)

            # 4. 生成AI研究报告
            ai_analysis = await self._generate_ai_analysis(
                symbol, analysis_data, bear_factors, risk_assessment
            )

            # 5. 整合研究结果
            result = {
                "analysis_type": "bear_research",
                "symbol": symbol,
                "analyst": self.name,
                "timestamp": datetime.now().isoformat(),
                "bear_factors": bear_factors,
                "risk_assessment": risk_assessment,
                "ai_analysis": ai_analysis,
                "bear_thesis": self._extract_bear_thesis(ai_analysis),
                "risk_level": self._calculate_risk_level(bear_factors),
                "downside_risk_range": self._estimate_downside_risk(risk_assessment)
            }

            self._log_analysis_complete(symbol, f"风险等级: {result['risk_level']}")
            return result

        except Exception as e:
            self.logger.error(f"❌ [{self.name}] 分析失败: {symbol} - {e}")
            return {
                "analysis_type": "bear_research",
                "symbol": symbol,
                "analyst": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _integrate_analysis_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """整合其他分析师的数据"""
        try:
            integrated_data = {
                "market_analysis": context.get("market_report", {}),
                "fundamentals_analysis": context.get("fundamentals_report", {}),
                "news_analysis": context.get("news_report", {}),
                "social_analysis": context.get("social_report", {})
            }

            return integrated_data
        except Exception as e:
            self.logger.error(f"❌ 数据整合失败: {e}")
            return {}

    async def _identify_bear_factors(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别看跌因素"""
        try:
            bear_factors = []

            # 从市场分析中提取看跌因素
            market_data = analysis_data.get("market_analysis", {})
            if market_data.get("recommendation") == "卖出":
                bear_factors.append({
                    "category": "技术面",
                    "factor": "技术指标显示卖出信号",
                    "severity": "高",
                    "description": "技术分析显示股票处于下降趋势"
                })

            # 从基本面分析中提取看跌因素
            fundamentals_data = analysis_data.get("fundamentals_analysis", {})
            if fundamentals_data.get("investment_grade") == "C级":
                bear_factors.append({
                    "category": "基本面",
                    "factor": "财务状况恶化",
                    "severity": "高",
                    "description": "公司财务指标表现不佳，存在财务风险"
                })

            # 检查估值风险
            valuation = fundamentals_data.get("valuation", "")
            if "高估" in valuation:
                bear_factors.append({
                    "category": "估值",
                    "factor": "估值过高",
                    "severity": "中",
                    "description": "当前估值水平偏高，存在回调风险"
                })

            # 从新闻分析中提取看跌因素
            news_data = analysis_data.get("news_analysis", {})
            if news_data.get("market_sentiment") == "negative":
                bear_factors.append({
                    "category": "消息面",
                    "factor": "负面新闻较多",
                    "severity": "中",
                    "description": "近期负面新闻增多，市场情绪转向悲观"
                })

            # 从社交媒体分析中提取看跌因素
            social_data = analysis_data.get("social_analysis", {})
            if social_data.get("retail_sentiment") == "悲观":
                bear_factors.append({
                    "category": "情绪面",
                    "factor": "散户情绪悲观",
                    "severity": "中",
                    "description": "社交媒体讨论偏向悲观，散户情绪低迷"
                })

            # 添加通用风险因素
            bear_factors.extend([
                {
                    "category": "市场风险",
                    "factor": "系统性风险",
                    "severity": "中",
                    "description": "整体市场波动可能影响个股表现"
                },
                {
                    "category": "流动性风险",
                    "factor": "资金面收紧",
                    "severity": "低",
                    "description": "市场流动性变化可能影响股价"
                }
            ])

            return bear_factors
        except Exception as e:
            self.logger.error(f"❌ 看跌因素识别失败: {e}")
            return []

    async def _evaluate_risks(self, bear_factors: List[Dict]) -> Dict[str, Any]:
        """评估投资风险"""
        try:
            if not bear_factors:
                return {"risk_level": "低", "key_risks": []}

            # 按严重程度统计看跌因素
            high_severity = sum(1 for factor in bear_factors if factor.get("severity") == "高")
            medium_severity = sum(1 for factor in bear_factors if factor.get("severity") == "中")
            low_severity = sum(1 for factor in bear_factors if factor.get("severity") == "低")

            # 计算风险等级
            risk_score = high_severity * 3 + medium_severity * 2 + low_severity * 1

            if risk_score >= 6:
                risk_level = "高"
            elif risk_score >= 3:
                risk_level = "中"
            else:
                risk_level = "低"

            # 提取关键风险
            key_risks = [
                factor["factor"] for factor in bear_factors
                if factor.get("severity") == "高"
            ]

            return {
                "risk_level": risk_level,
                "risk_score": risk_score,
                "key_risks": key_risks,
                "factor_distribution": {
                    "high": high_severity,
                    "medium": medium_severity,
                    "low": low_severity,
                    "total": len(bear_factors)
                },
                "risk_categories": self._categorize_risks(bear_factors)
            }
        except Exception as e:
            self.logger.error(f"❌ 投资风险评估失败: {e}")
            return {"risk_level": "中"}

    def _categorize_risks(self, bear_factors: List[Dict]) -> Dict[str, int]:
        """按类别统计风险因素"""
        categories = {}
        for factor in bear_factors:
            category = factor.get("category", "其他")
            categories[category] = categories.get(category, 0) + 1
        return categories

    async def _generate_ai_analysis(self, symbol: str, analysis_data: Dict,
                                  bear_factors: List, risk_assessment: Dict) -> str:
        """生成AI研究报告"""
        try:
            if self.llm_client:
                prompt = self.prompt_template.format(
                    symbol=symbol,
                    analysis_data=str(analysis_data),
                    risk_context=str(risk_assessment)
                )

                response = await self.llm_client.generate(
                    prompt=prompt,
                    context={"bear_factors": bear_factors}
                )

                return response.get("content", "AI分析生成失败")
            else:
                # 模拟AI分析
                risk_level = risk_assessment.get("risk_level", "中")
                key_risks = risk_assessment.get("key_risks", [])

                return f"""
## {symbol} 看跌研究报告

### 风险警示
- 风险等级: {risk_level}
- 关键看跌因素: {len(bear_factors)}个
- 核心风险点: {', '.join(key_risks) if key_risks else '基本面风险'}

### 看跌因素分析
{self._format_bear_factors(bear_factors)}

### 投资风险评估
基于当前分析，{symbol}{'存在较高的投资风险' if risk_level == '高' else '存在一定的投资风险' if risk_level == '中' else '投资风险相对可控'}。
主要风险逻辑包括：{', '.join(key_risks[:3]) if key_risks else '市场系统性风险'}。

### 风险提示
投资者应密切关注以下风险因素的变化，及时调整投资策略。

### 投资建议
建议{'谨慎回避' if risk_level == '高' else '适度减仓' if risk_level == '中' else '密切关注'}，
{'建议及时止损' if risk_level == '高' else '可考虑减持' if risk_level == '中' else '保持观望'}。
"""
        except Exception as e:
            self.logger.error(f"❌ AI分析生成失败: {e}")
            return f"AI分析生成失败: {str(e)}"

    def _format_bear_factors(self, bear_factors: List[Dict]) -> str:
        """格式化看跌因素"""
        if not bear_factors:
            return "- 暂未发现明显看跌因素"

        lines = []
        for factor in bear_factors:
            category = factor.get("category", "其他")
            factor_name = factor.get("factor", "")
            severity = factor.get("severity", "中")
            description = factor.get("description", "")
            lines.append(f"- {category}: {factor_name} (严重程度: {severity}) - {description}")

        return "\n".join(lines)

    def _extract_bear_thesis(self, ai_analysis: str) -> str:
        """提取看跌论点"""
        try:
            # 简单提取投资风险评估部分
            if "投资风险评估" in ai_analysis:
                lines = ai_analysis.split("\n")
                for i, line in enumerate(lines):
                    if "投资风险评估" in line and i + 1 < len(lines):
                        return lines[i + 1].strip()
            return "基于多重看跌因素，存在投资风险"
        except:
            return "基于多重看跌因素，存在投资风险"

    def _calculate_risk_level(self, bear_factors: List[Dict]) -> str:
        """计算风险等级"""
        try:
            if not bear_factors:
                return "低"

            high_count = sum(1 for factor in bear_factors if factor.get("severity") == "高")
            total_count = len(bear_factors)

            if high_count >= 2 or total_count >= 5:
                return "高"
            elif high_count >= 1 or total_count >= 3:
                return "中"
            else:
                return "低"
        except:
            return "中"

    def _estimate_downside_risk(self, risk_assessment: Dict) -> str:
        """估算下跌风险区间"""
        try:
            risk_level = risk_assessment.get("risk_level", "中")

            if risk_level == "高":
                return "下跌风险15-30%"
            elif risk_level == "中":
                return "下跌风险5-15%"
            else:
                return "下跌风险有限"
        except:
            return "待进一步分析"
