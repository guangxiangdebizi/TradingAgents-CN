"""
看涨研究员智能体
移植自tradingagents，专注于挖掘看涨因素和投资机会
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..base.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class BullResearcher(BaseAgent):
    """
    看涨研究员智能体
    专注于挖掘看涨因素、投资机会和正面催化剂
    """
    
    def __init__(self, llm_client=None, data_client=None):
        super().__init__(
            name="BullResearcher",
            description="专业的看涨研究员，擅长挖掘投资机会和看涨因素",
            llm_client=llm_client,
            data_client=data_client
        )
        self.prompt_template = None
    
    async def _load_prompts(self):
        """加载看涨研究提示词模板"""
        self.prompt_template = """
你是一位专业的看涨研究员，具有丰富的投资机会挖掘和价值发现经验。

请对股票 {symbol} 进行看涨因素分析，重点关注：

## 分析要求：
1. **基本面优势**：财务数据中的积极因素
2. **技术面机会**：技术指标显示的买入信号
3. **催化剂事件**：可能推动股价上涨的事件
4. **行业前景**：行业发展趋势和政策利好
5. **估值优势**：相对估值的吸引力
6. **成长潜力**：未来增长空间和驱动因素

## 分析数据：
{analysis_data}

## 市场环境：
{market_context}

## 输出格式：
请提供详细的看涨研究报告，重点突出投资亮点和上涨逻辑。

## 投资建议：
基于看涨因素给出具体的投资建议和目标价位。
"""
    
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行看涨研究分析
        
        Args:
            symbol: 股票代码
            context: 分析上下文，包含其他分析师的报告
            
        Returns:
            看涨研究结果
        """
        self._log_analysis_start(symbol)
        
        try:
            # 1. 整合其他分析师的数据
            analysis_data = await self._integrate_analysis_data(context)
            
            # 2. 识别看涨因素
            bull_factors = await self._identify_bull_factors(analysis_data)
            
            # 3. 评估投资机会
            investment_opportunities = await self._evaluate_opportunities(bull_factors)
            
            # 4. 生成AI研究报告
            ai_analysis = await self._generate_ai_analysis(
                symbol, analysis_data, bull_factors, investment_opportunities
            )
            
            # 5. 整合研究结果
            result = {
                "analysis_type": "bull_research",
                "symbol": symbol,
                "analyst": self.name,
                "timestamp": datetime.now().isoformat(),
                "bull_factors": bull_factors,
                "investment_opportunities": investment_opportunities,
                "ai_analysis": ai_analysis,
                "bull_thesis": self._extract_bull_thesis(ai_analysis),
                "confidence_level": self._calculate_confidence(bull_factors),
                "target_price_range": self._estimate_target_price(investment_opportunities)
            }
            
            self._log_analysis_complete(symbol, f"看涨信心: {result['confidence_level']}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ [{self.name}] 分析失败: {symbol} - {e}")
            return {
                "analysis_type": "bull_research",
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
    
    async def _identify_bull_factors(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别看涨因素"""
        try:
            bull_factors = []
            
            # 从市场分析中提取看涨因素
            market_data = analysis_data.get("market_analysis", {})
            if market_data.get("recommendation") == "买入":
                bull_factors.append({
                    "category": "技术面",
                    "factor": "技术指标显示买入信号",
                    "strength": "高",
                    "description": "技术分析显示股票处于上升趋势"
                })
            
            # 从基本面分析中提取看涨因素
            fundamentals_data = analysis_data.get("fundamentals_analysis", {})
            if fundamentals_data.get("investment_grade") in ["A级", "B级"]:
                bull_factors.append({
                    "category": "基本面",
                    "factor": "财务状况良好",
                    "strength": "高" if fundamentals_data.get("investment_grade") == "A级" else "中",
                    "description": "公司财务指标表现优秀，具备投资价值"
                })
            
            # 从新闻分析中提取看涨因素
            news_data = analysis_data.get("news_analysis", {})
            if news_data.get("market_sentiment") == "positive":
                bull_factors.append({
                    "category": "消息面",
                    "factor": "正面新闻较多",
                    "strength": "中",
                    "description": "近期新闻偏向正面，市场情绪积极"
                })
            
            # 从社交媒体分析中提取看涨因素
            social_data = analysis_data.get("social_analysis", {})
            if social_data.get("retail_sentiment") == "乐观":
                bull_factors.append({
                    "category": "情绪面",
                    "factor": "散户情绪乐观",
                    "strength": "中",
                    "description": "社交媒体讨论偏向乐观，散户情绪积极"
                })
            
            return bull_factors
        except Exception as e:
            self.logger.error(f"❌ 看涨因素识别失败: {e}")
            return []
    
    async def _evaluate_opportunities(self, bull_factors: List[Dict]) -> Dict[str, Any]:
        """评估投资机会"""
        try:
            if not bull_factors:
                return {"opportunity_level": "低", "key_opportunities": []}
            
            # 按强度统计看涨因素
            high_strength = sum(1 for factor in bull_factors if factor.get("strength") == "高")
            medium_strength = sum(1 for factor in bull_factors if factor.get("strength") == "中")
            
            # 计算机会等级
            total_score = high_strength * 3 + medium_strength * 2
            
            if total_score >= 6:
                opportunity_level = "高"
            elif total_score >= 3:
                opportunity_level = "中"
            else:
                opportunity_level = "低"
            
            # 提取关键机会
            key_opportunities = [
                factor["factor"] for factor in bull_factors 
                if factor.get("strength") == "高"
            ]
            
            return {
                "opportunity_level": opportunity_level,
                "total_score": total_score,
                "key_opportunities": key_opportunities,
                "factor_distribution": {
                    "high": high_strength,
                    "medium": medium_strength,
                    "total": len(bull_factors)
                }
            }
        except Exception as e:
            self.logger.error(f"❌ 投资机会评估失败: {e}")
            return {"opportunity_level": "中"}
    
    async def _generate_ai_analysis(self, symbol: str, analysis_data: Dict, 
                                  bull_factors: List, opportunities: Dict) -> str:
        """生成AI研究报告"""
        try:
            if self.llm_client:
                prompt = self.prompt_template.format(
                    symbol=symbol,
                    analysis_data=str(analysis_data),
                    market_context=str(opportunities)
                )
                
                response = await self.llm_client.generate(
                    prompt=prompt,
                    context={"bull_factors": bull_factors}
                )
                
                return response.get("content", "AI分析生成失败")
            else:
                # 模拟AI分析
                opportunity_level = opportunities.get("opportunity_level", "中")
                key_opportunities = opportunities.get("key_opportunities", [])
                
                return f"""
## {symbol} 看涨研究报告

### 投资亮点
- 投资机会等级: {opportunity_level}
- 关键看涨因素: {len(bull_factors)}个
- 核心投资机会: {', '.join(key_opportunities) if key_opportunities else '基本面稳健'}

### 看涨因素分析
{self._format_bull_factors(bull_factors)}

### 投资逻辑
基于当前分析，{symbol}{'具有较强的投资吸引力' if opportunity_level == '高' else '具有一定的投资价值' if opportunity_level == '中' else '投资价值有限'}。
主要看涨逻辑包括：{', '.join(key_opportunities[:3]) if key_opportunities else '基本面支撑'}。

### 风险提示
虽然看涨因素较多，但仍需关注市场整体风险和个股特定风险。

### 投资建议
建议{'积极关注' if opportunity_level == '高' else '适度关注' if opportunity_level == '中' else '谨慎观察'}，
{'可考虑逢低买入' if opportunity_level == '高' else '可适量配置' if opportunity_level == '中' else '建议观望'}。
"""
        except Exception as e:
            self.logger.error(f"❌ AI分析生成失败: {e}")
            return f"AI分析生成失败: {str(e)}"
    
    def _format_bull_factors(self, bull_factors: List[Dict]) -> str:
        """格式化看涨因素"""
        if not bull_factors:
            return "- 暂未发现明显看涨因素"
        
        lines = []
        for factor in bull_factors:
            category = factor.get("category", "其他")
            factor_name = factor.get("factor", "")
            strength = factor.get("strength", "中")
            description = factor.get("description", "")
            lines.append(f"- {category}: {factor_name} (强度: {strength}) - {description}")
        
        return "\n".join(lines)
    
    def _extract_bull_thesis(self, ai_analysis: str) -> str:
        """提取看涨论点"""
        try:
            # 简单提取投资逻辑部分
            if "投资逻辑" in ai_analysis:
                lines = ai_analysis.split("\n")
                for i, line in enumerate(lines):
                    if "投资逻辑" in line and i + 1 < len(lines):
                        return lines[i + 1].strip()
            return "基于多重看涨因素，具备投资价值"
        except:
            return "基于多重看涨因素，具备投资价值"
    
    def _calculate_confidence(self, bull_factors: List[Dict]) -> str:
        """计算看涨信心等级"""
        try:
            if not bull_factors:
                return "低"
            
            high_count = sum(1 for factor in bull_factors if factor.get("strength") == "高")
            total_count = len(bull_factors)
            
            if high_count >= 2 or total_count >= 4:
                return "高"
            elif high_count >= 1 or total_count >= 2:
                return "中"
            else:
                return "低"
        except:
            return "中"
    
    def _estimate_target_price(self, opportunities: Dict) -> str:
        """估算目标价位区间"""
        try:
            opportunity_level = opportunities.get("opportunity_level", "中")
            
            if opportunity_level == "高":
                return "上涨空间15-25%"
            elif opportunity_level == "中":
                return "上涨空间5-15%"
            else:
                return "上涨空间有限"
        except:
            return "待进一步分析"
