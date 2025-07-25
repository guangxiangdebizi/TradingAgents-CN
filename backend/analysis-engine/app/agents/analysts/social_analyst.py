"""
社交媒体分析师智能体
移植自tradingagents，负责社交媒体情绪分析和散户情绪评估
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..base.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class SocialAnalyst(BaseAgent):
    """
    社交媒体分析师智能体
    专注于社交媒体情绪分析、散户情绪评估和网络舆情监控
    """
    
    def __init__(self, llm_client=None, data_client=None):
        super().__init__(
            name="SocialAnalyst",
            description="专业的社交媒体分析师，擅长网络舆情和散户情绪分析",
            llm_client=llm_client,
            data_client=data_client
        )
        self.prompt_template = None
    
    async def _load_prompts(self):
        """加载社交媒体分析提示词模板"""
        self.prompt_template = """
你是一位专业的社交媒体分析师，具有丰富的网络舆情分析和散户情绪评估经验。

请对股票 {symbol} 的社交媒体讨论进行全面分析，包括：

## 分析要求：
1. **讨论热度分析**：讨论量、关注度变化趋势
2. **情绪倾向分析**：散户情绪的正负面分布
3. **关键话题识别**：热门讨论话题和关注焦点
4. **影响力分析**：重要意见领袖的观点
5. **趋势预测**：基于社交媒体数据的短期趋势预测

## 社交媒体数据：
{social_data}

## 情绪统计：
{sentiment_stats}

## 输出格式：
请提供详细的社交媒体分析报告，包含具体的数据分析和趋势判断。

## 投资建议：
基于社交媒体情绪给出散户情绪预测和相关投资建议。
"""
    
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行社交媒体分析
        
        Args:
            symbol: 股票代码
            context: 分析上下文
            
        Returns:
            社交媒体分析结果
        """
        self._log_analysis_start(symbol)
        
        try:
            # 1. 获取社交媒体数据
            social_data = await self._get_social_data(symbol, context)
            
            # 2. 执行情绪统计
            sentiment_stats = await self._analyze_sentiment_stats(social_data)
            
            # 3. 分析讨论热度
            heat_analysis = await self._analyze_discussion_heat(social_data)
            
            # 4. 识别关键话题
            topic_analysis = await self._identify_key_topics(social_data)
            
            # 5. 生成AI分析报告
            ai_analysis = await self._generate_ai_analysis(
                symbol, social_data, sentiment_stats, heat_analysis, topic_analysis
            )
            
            # 6. 整合分析结果
            result = {
                "analysis_type": "social_analysis",
                "symbol": symbol,
                "analyst": self.name,
                "timestamp": datetime.now().isoformat(),
                "social_data_summary": social_data.get("summary", ""),
                "sentiment_stats": sentiment_stats,
                "heat_analysis": heat_analysis,
                "topic_analysis": topic_analysis,
                "ai_analysis": ai_analysis,
                "retail_sentiment": self._extract_retail_sentiment(sentiment_stats),
                "discussion_trend": self._extract_discussion_trend(heat_analysis)
            }
            
            self._log_analysis_complete(symbol, f"散户情绪: {result['retail_sentiment']}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ [{self.name}] 分析失败: {symbol} - {e}")
            return {
                "analysis_type": "social_analysis",
                "symbol": symbol,
                "analyst": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_social_data(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取社交媒体数据"""
        try:
            if self.data_client:
                data = await self.data_client.get_social_media_data(
                    symbol=symbol,
                    platforms=["weibo", "xueqiu", "eastmoney", "twitter"],
                    days=context.get("social_days", 3)
                )
                return data
            else:
                # 模拟社交媒体数据
                return {
                    "symbol": symbol,
                    "total_mentions": 1250,
                    "platforms": {
                        "weibo": {"mentions": 400, "sentiment_avg": 0.6},
                        "xueqiu": {"mentions": 350, "sentiment_avg": 0.7},
                        "eastmoney": {"mentions": 300, "sentiment_avg": 0.5},
                        "twitter": {"mentions": 200, "sentiment_avg": 0.65}
                    },
                    "posts": [
                        {
                            "platform": "xueqiu",
                            "content": f"{symbol}这波上涨很稳，基本面支撑强劲",
                            "sentiment": 0.8,
                            "likes": 156,
                            "comments": 23,
                            "timestamp": "2025-07-24T15:30:00"
                        },
                        {
                            "platform": "weibo",
                            "content": f"看好{symbol}长期发展，短期可能有调整",
                            "sentiment": 0.6,
                            "likes": 89,
                            "comments": 12,
                            "timestamp": "2025-07-24T14:20:00"
                        },
                        {
                            "platform": "eastmoney",
                            "content": f"{symbol}技术面突破，可以关注",
                            "sentiment": 0.7,
                            "likes": 234,
                            "comments": 45,
                            "timestamp": "2025-07-24T13:15:00"
                        }
                    ],
                    "summary": f"获取到{symbol}在多个平台的1250条讨论"
                }
        except Exception as e:
            self.logger.error(f"❌ 获取社交媒体数据失败: {e}")
            return {"error": str(e)}
    
    async def _analyze_sentiment_stats(self, social_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析情绪统计"""
        try:
            if "error" in social_data:
                return {"overall_sentiment": 0.5, "sentiment_distribution": {}}
            
            posts = social_data.get("posts", [])
            platforms = social_data.get("platforms", {})
            
            if not posts:
                return {"overall_sentiment": 0.5, "sentiment_distribution": {}}
            
            # 计算整体情绪
            total_sentiment = sum(post.get("sentiment", 0.5) for post in posts)
            overall_sentiment = total_sentiment / len(posts)
            
            # 按平台统计情绪
            platform_sentiment = {}
            for platform, data in platforms.items():
                platform_sentiment[platform] = {
                    "mentions": data.get("mentions", 0),
                    "avg_sentiment": data.get("sentiment_avg", 0.5)
                }
            
            # 情绪分布统计
            positive_count = sum(1 for post in posts if post.get("sentiment", 0.5) > 0.6)
            negative_count = sum(1 for post in posts if post.get("sentiment", 0.5) < 0.4)
            neutral_count = len(posts) - positive_count - negative_count
            
            return {
                "overall_sentiment": overall_sentiment,
                "platform_sentiment": platform_sentiment,
                "sentiment_distribution": {
                    "positive": positive_count / len(posts),
                    "negative": negative_count / len(posts),
                    "neutral": neutral_count / len(posts)
                },
                "total_posts": len(posts),
                "sentiment_trend": "上升" if overall_sentiment > 0.6 else "下降" if overall_sentiment < 0.4 else "稳定"
            }
        except Exception as e:
            self.logger.error(f"❌ 情绪统计分析失败: {e}")
            return {"overall_sentiment": 0.5}
    
    async def _analyze_discussion_heat(self, social_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析讨论热度"""
        try:
            total_mentions = social_data.get("total_mentions", 0)
            platforms = social_data.get("platforms", {})
            posts = social_data.get("posts", [])
            
            # 计算平均互动量
            total_likes = sum(post.get("likes", 0) for post in posts)
            total_comments = sum(post.get("comments", 0) for post in posts)
            avg_engagement = (total_likes + total_comments) / max(len(posts), 1)
            
            # 热度等级
            if total_mentions > 1000:
                heat_level = "高"
            elif total_mentions > 500:
                heat_level = "中"
            else:
                heat_level = "低"
            
            return {
                "total_mentions": total_mentions,
                "heat_level": heat_level,
                "avg_engagement": avg_engagement,
                "platform_distribution": {
                    platform: data.get("mentions", 0) 
                    for platform, data in platforms.items()
                },
                "engagement_stats": {
                    "total_likes": total_likes,
                    "total_comments": total_comments,
                    "avg_engagement": avg_engagement
                }
            }
        except Exception as e:
            self.logger.error(f"❌ 讨论热度分析失败: {e}")
            return {"heat_level": "中", "total_mentions": 0}
    
    async def _identify_key_topics(self, social_data: Dict[str, Any]) -> Dict[str, Any]:
        """识别关键话题"""
        try:
            posts = social_data.get("posts", [])
            
            # 简单的关键词提取
            keywords = {}
            for post in posts:
                content = post.get("content", "")
                # 统计关键词频率
                for keyword in ["上涨", "下跌", "买入", "卖出", "看好", "看空", "突破", "支撑", "阻力"]:
                    if keyword in content:
                        keywords[keyword] = keywords.get(keyword, 0) + 1
            
            # 排序获取热门话题
            top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "top_keywords": top_keywords,
                "keyword_stats": keywords,
                "main_topics": [kw[0] for kw in top_keywords[:3]]
            }
        except Exception as e:
            self.logger.error(f"❌ 关键话题识别失败: {e}")
            return {"top_keywords": [], "main_topics": []}
    
    async def _generate_ai_analysis(self, symbol: str, social_data: Dict, 
                                  sentiment_stats: Dict, heat_analysis: Dict, 
                                  topic_analysis: Dict) -> str:
        """生成AI分析报告"""
        try:
            if self.llm_client:
                prompt = self.prompt_template.format(
                    symbol=symbol,
                    social_data=str(social_data),
                    sentiment_stats=str(sentiment_stats)
                )
                
                response = await self.llm_client.generate(
                    prompt=prompt,
                    context={
                        "heat_analysis": heat_analysis,
                        "topic_analysis": topic_analysis
                    }
                )
                
                return response.get("content", "AI分析生成失败")
            else:
                # 模拟AI分析
                sentiment = sentiment_stats.get("overall_sentiment", 0.5)
                heat_level = heat_analysis.get("heat_level", "中")
                main_topics = topic_analysis.get("main_topics", [])
                
                return f"""
## {symbol} 社交媒体分析报告

### 讨论热度分析
- 总讨论量: {social_data.get('total_mentions', 0)}条
- 热度等级: {heat_level}
- 平均互动量: {heat_analysis.get('avg_engagement', 0):.1f}

### 散户情绪分析
- 整体情绪得分: {sentiment:.2f}
- 情绪趋势: {sentiment_stats.get('sentiment_trend', '稳定')}
- 正面情绪占比: {sentiment_stats.get('sentiment_distribution', {}).get('positive', 0):.1%}

### 热门话题
- 主要讨论话题: {', '.join(main_topics) if main_topics else '无明显热点'}
- 关键词分布: {dict(topic_analysis.get('top_keywords', [])[:3])}

### 平台分布
{self._format_platform_distribution(social_data.get('platforms', {}))}

### 散户情绪预测
基于当前社交媒体分析，散户情绪{'偏向乐观' if sentiment > 0.6 else '偏向悲观' if sentiment < 0.4 else '相对中性'}，
讨论热度{heat_level}，短期内{'可能推动股价上涨' if sentiment > 0.6 and heat_level == '高' else '对股价影响有限'}。
"""
        except Exception as e:
            self.logger.error(f"❌ AI分析生成失败: {e}")
            return f"AI分析生成失败: {str(e)}"
    
    def _format_platform_distribution(self, platforms: Dict) -> str:
        """格式化平台分布信息"""
        if not platforms:
            return "- 暂无平台数据"
        
        lines = []
        for platform, data in platforms.items():
            mentions = data.get("mentions", 0)
            sentiment = data.get("sentiment_avg", 0.5)
            lines.append(f"- {platform}: {mentions}条讨论，情绪得分{sentiment:.2f}")
        
        return "\n".join(lines)
    
    def _extract_retail_sentiment(self, sentiment_stats: Dict) -> str:
        """提取散户情绪"""
        sentiment = sentiment_stats.get("overall_sentiment", 0.5)
        if sentiment > 0.6:
            return "乐观"
        elif sentiment < 0.4:
            return "悲观"
        else:
            return "中性"
    
    def _extract_discussion_trend(self, heat_analysis: Dict) -> str:
        """提取讨论趋势"""
        return heat_analysis.get("heat_level", "中")
