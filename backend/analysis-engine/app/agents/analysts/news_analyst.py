"""
新闻分析师智能体
移植自tradingagents，负责新闻分析和市场情绪评估
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..base.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class NewsAnalyst(BaseAgent):
    """
    新闻分析师智能体
    专注于新闻分析、市场情绪评估和事件影响分析
    """
    
    def __init__(self, llm_client=None, data_client=None):
        super().__init__(
            name="NewsAnalyst",
            description="专业的新闻分析师，擅长新闻解读和市场情绪分析",
            llm_client=llm_client,
            data_client=data_client
        )
        self.prompt_template = None
    
    async def _load_prompts(self):
        """加载新闻分析提示词模板"""
        self.prompt_template = """
你是一位专业的新闻分析师，具有丰富的市场新闻解读和情绪分析经验。

请对股票 {symbol} 的相关新闻进行全面分析，包括：

## 分析要求：
1. **新闻事件分析**：重要新闻事件的影响评估
2. **情绪倾向分析**：正面、负面、中性新闻的分布
3. **市场影响评估**：新闻对股价可能的影响
4. **时效性分析**：新闻的时效性和持续影响
5. **可信度评估**：新闻来源的可信度分析

## 新闻数据：
{news_data}

## 情绪分析：
{sentiment_analysis}

## 输出格式：
请提供详细的新闻分析报告，包含具体的事件分析和影响评估。

## 投资建议：
基于新闻分析给出短期市场情绪预测和投资建议。
"""
    
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行新闻分析
        
        Args:
            symbol: 股票代码
            context: 分析上下文
            
        Returns:
            新闻分析结果
        """
        self._log_analysis_start(symbol)
        
        try:
            # 1. 获取新闻数据
            news_data = await self._get_news_data(symbol, context)
            
            # 2. 执行情绪分析
            sentiment_analysis = await self._perform_sentiment_analysis(news_data)
            
            # 3. 分析新闻影响
            impact_analysis = await self._analyze_news_impact(news_data, sentiment_analysis)
            
            # 4. 生成AI分析报告
            ai_analysis = await self._generate_ai_analysis(
                symbol, news_data, sentiment_analysis, impact_analysis
            )
            
            # 5. 整合分析结果
            result = {
                "analysis_type": "news_analysis",
                "symbol": symbol,
                "analyst": self.name,
                "timestamp": datetime.now().isoformat(),
                "news_summary": news_data.get("summary", ""),
                "sentiment_analysis": sentiment_analysis,
                "impact_analysis": impact_analysis,
                "ai_analysis": ai_analysis,
                "market_sentiment": self._extract_market_sentiment(sentiment_analysis),
                "news_impact_score": self._calculate_impact_score(impact_analysis)
            }
            
            self._log_analysis_complete(symbol, f"情绪: {result['market_sentiment']}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ [{self.name}] 分析失败: {symbol} - {e}")
            return {
                "analysis_type": "news_analysis",
                "symbol": symbol,
                "analyst": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_news_data(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取新闻数据"""
        try:
            if self.data_client:
                data = await self.data_client.get_news_data(
                    symbol=symbol,
                    days=context.get("news_days", 7)
                )
                return data
            else:
                # 模拟新闻数据
                return {
                    "symbol": symbol,
                    "news_count": 15,
                    "news_items": [
                        {
                            "title": f"{symbol}公司发布季度财报，业绩超预期",
                            "content": "公司本季度营收增长15%，净利润增长20%",
                            "source": "财经新闻",
                            "timestamp": "2025-07-24T10:00:00",
                            "sentiment": "positive"
                        },
                        {
                            "title": f"{symbol}获得重要合作伙伴关系",
                            "content": "公司与行业龙头企业签署战略合作协议",
                            "source": "商业新闻",
                            "timestamp": "2025-07-23T14:30:00",
                            "sentiment": "positive"
                        },
                        {
                            "title": f"分析师上调{symbol}目标价",
                            "content": "多家投行上调目标价，看好公司发展前景",
                            "source": "投资分析",
                            "timestamp": "2025-07-22T09:15:00",
                            "sentiment": "positive"
                        }
                    ],
                    "summary": f"获取到{symbol}的15条相关新闻"
                }
        except Exception as e:
            self.logger.error(f"❌ 获取新闻数据失败: {e}")
            return {"error": str(e)}
    
    async def _perform_sentiment_analysis(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行情绪分析"""
        try:
            if "error" in news_data:
                return {"overall_sentiment": "neutral", "confidence": 0.5}
            
            news_items = news_data.get("news_items", [])
            if not news_items:
                return {"overall_sentiment": "neutral", "confidence": 0.5}
            
            # 统计情绪分布
            positive_count = sum(1 for item in news_items if item.get("sentiment") == "positive")
            negative_count = sum(1 for item in news_items if item.get("sentiment") == "negative")
            neutral_count = len(news_items) - positive_count - negative_count
            
            total_count = len(news_items)
            
            # 计算整体情绪
            if positive_count > negative_count * 1.5:
                overall_sentiment = "positive"
                confidence = positive_count / total_count
            elif negative_count > positive_count * 1.5:
                overall_sentiment = "negative"
                confidence = negative_count / total_count
            else:
                overall_sentiment = "neutral"
                confidence = max(positive_count, negative_count, neutral_count) / total_count
            
            return {
                "overall_sentiment": overall_sentiment,
                "confidence": confidence,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "total_count": total_count,
                "sentiment_distribution": {
                    "positive": positive_count / total_count,
                    "negative": negative_count / total_count,
                    "neutral": neutral_count / total_count
                }
            }
        except Exception as e:
            self.logger.error(f"❌ 情绪分析失败: {e}")
            return {"overall_sentiment": "neutral", "confidence": 0.5}
    
    async def _analyze_news_impact(self, news_data: Dict, sentiment_analysis: Dict) -> Dict[str, Any]:
        """分析新闻影响"""
        try:
            news_items = news_data.get("news_items", [])
            
            # 分析重要新闻事件
            important_events = []
            for item in news_items:
                title = item.get("title", "")
                if any(keyword in title for keyword in ["财报", "合作", "收购", "重组", "监管"]):
                    important_events.append({
                        "title": title,
                        "impact_level": "high",
                        "sentiment": item.get("sentiment", "neutral")
                    })
            
            # 计算影响强度
            impact_strength = len(important_events) / max(len(news_items), 1)
            
            return {
                "important_events": important_events,
                "impact_strength": impact_strength,
                "short_term_impact": "high" if impact_strength > 0.3 else "medium" if impact_strength > 0.1 else "low",
                "key_themes": self._extract_key_themes(news_items)
            }
        except Exception as e:
            self.logger.error(f"❌ 新闻影响分析失败: {e}")
            return {"impact_strength": 0.5, "short_term_impact": "medium"}
    
    def _extract_key_themes(self, news_items: List[Dict]) -> List[str]:
        """提取关键主题"""
        themes = []
        for item in news_items:
            title = item.get("title", "")
            if "财报" in title or "业绩" in title:
                themes.append("财务表现")
            elif "合作" in title or "协议" in title:
                themes.append("战略合作")
            elif "分析师" in title or "目标价" in title:
                themes.append("分析师观点")
            elif "监管" in title or "政策" in title:
                themes.append("监管政策")
        
        # 去重并返回
        return list(set(themes))
    
    async def _generate_ai_analysis(self, symbol: str, news_data: Dict, 
                                  sentiment_analysis: Dict, impact_analysis: Dict) -> str:
        """生成AI分析报告"""
        try:
            if self.llm_client:
                prompt = self.prompt_template.format(
                    symbol=symbol,
                    news_data=str(news_data),
                    sentiment_analysis=str(sentiment_analysis)
                )
                
                response = await self.llm_client.generate(
                    prompt=prompt,
                    context={"impact_analysis": impact_analysis}
                )
                
                return response.get("content", "AI分析生成失败")
            else:
                # 模拟AI分析
                sentiment = sentiment_analysis.get("overall_sentiment", "neutral")
                confidence = sentiment_analysis.get("confidence", 0.5)
                impact = impact_analysis.get("short_term_impact", "medium")
                
                return f"""
## {symbol} 新闻分析报告

### 新闻概况
- 新闻总数: {news_data.get('news_count', 0)}条
- 整体情绪: {sentiment}
- 情绪置信度: {confidence:.2%}

### 情绪分析
- 正面新闻: {sentiment_analysis.get('positive_count', 0)}条
- 负面新闻: {sentiment_analysis.get('negative_count', 0)}条
- 中性新闻: {sentiment_analysis.get('neutral_count', 0)}条

### 影响评估
- 短期影响: {impact}
- 重要事件: {len(impact_analysis.get('important_events', []))}个
- 关键主题: {', '.join(impact_analysis.get('key_themes', []))}

### 市场情绪预测
基于当前新闻分析，市场情绪{'偏向乐观' if sentiment == 'positive' else '偏向悲观' if sentiment == 'negative' else '相对中性'}，
短期内{'可能有正面影响' if sentiment == 'positive' else '可能有负面影响' if sentiment == 'negative' else '影响有限'}。
"""
        except Exception as e:
            self.logger.error(f"❌ AI分析生成失败: {e}")
            return f"AI分析生成失败: {str(e)}"
    
    def _extract_market_sentiment(self, sentiment_analysis: Dict) -> str:
        """提取市场情绪"""
        return sentiment_analysis.get("overall_sentiment", "neutral")
    
    def _calculate_impact_score(self, impact_analysis: Dict) -> float:
        """计算新闻影响得分"""
        try:
            impact_strength = impact_analysis.get("impact_strength", 0.5)
            important_events_count = len(impact_analysis.get("important_events", []))
            
            # 基础得分
            score = impact_strength * 0.7
            
            # 重要事件加分
            score += min(important_events_count * 0.1, 0.3)
            
            return min(score, 1.0)
        except:
            return 0.5
