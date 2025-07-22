"""
新闻工具
提供新闻获取和情绪分析功能
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import aiohttp

logger = logging.getLogger(__name__)

class NewsTools:
    """新闻工具类"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.data_service_url = "http://localhost:8003"  # Data Service URL
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5分钟缓存
    
    async def initialize(self):
        """初始化新闻工具"""
        try:
            logger.info("📰 初始化新闻工具...")
            
            # 创建HTTP会话
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # 测试数据服务连接
            await self._test_data_service()
            
            logger.info("✅ 新闻工具初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 新闻工具初始化失败: {e}")
            raise
    
    async def _test_data_service(self):
        """测试数据服务连接"""
        try:
            if self.session:
                async with self.session.get(f"{self.data_service_url}/health") as response:
                    if response.status == 200:
                        logger.info("✅ 数据服务连接正常")
                    else:
                        logger.warning(f"⚠️ 数据服务响应异常: {response.status}")
        except Exception as e:
            logger.warning(f"⚠️ 数据服务连接失败: {e}")
    
    def _get_cache_key(self, method: str, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [method]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        return ":".join(key_parts)
    
    def _is_cache_valid(self, cache_time: datetime) -> bool:
        """检查缓存是否有效"""
        return (datetime.now() - cache_time).total_seconds() < self.cache_ttl
    
    async def get_stock_news(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """获取股票新闻"""
        cache_key = self._get_cache_key("stock_news", symbol=symbol, days=days)
        
        # 检查缓存
        if cache_key in self.cache:
            cache_data, cache_time = self.cache[cache_key]
            if self._is_cache_valid(cache_time):
                logger.debug(f"📋 使用缓存新闻数据: {symbol}")
                return cache_data
        
        try:
            logger.info(f"📰 获取股票新闻: {symbol}")
            
            if self.session:
                # 调用数据服务API
                params = {"symbol": symbol, "days": days}
                async with self.session.get(
                    f"{self.data_service_url}/api/v1/stock/news",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # 缓存结果
                        self.cache[cache_key] = (data, datetime.now())
                        
                        return data
                    else:
                        error_text = await response.text()
                        raise Exception(f"数据服务错误: {response.status} - {error_text}")
            else:
                # 模拟数据（当数据服务不可用时）
                return await self._get_mock_news_data(symbol, days)
                
        except Exception as e:
            logger.error(f"❌ 获取股票新闻失败: {symbol} - {e}")
            # 返回模拟数据作为降级处理
            return await self._get_mock_news_data(symbol, days)
    
    async def analyze_sentiment(self, text: str, source: str = "news") -> Dict[str, Any]:
        """分析情绪"""
        try:
            logger.info(f"😊 分析情绪: {source}")
            
            # 简化的情绪分析
            sentiment_score = self._calculate_sentiment_score(text)
            sentiment_label = self._get_sentiment_label(sentiment_score)
            
            # 提取关键词
            keywords = self._extract_keywords(text)
            
            return {
                "success": True,
                "sentiment": {
                    "score": sentiment_score,
                    "label": sentiment_label,
                    "confidence": abs(sentiment_score)
                },
                "keywords": keywords,
                "source": source,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 情绪分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """计算情绪分数"""
        # 简化的情绪分析算法
        positive_words = [
            "上涨", "增长", "利好", "积极", "乐观", "看好", "买入", "推荐",
            "强劲", "优秀", "超预期", "突破", "创新高", "盈利", "收益"
        ]
        
        negative_words = [
            "下跌", "下降", "利空", "消极", "悲观", "看空", "卖出", "风险",
            "疲软", "糟糕", "低于预期", "跌破", "创新低", "亏损", "损失"
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.0
        
        # 计算情绪分数 (-1 到 1)
        score = (positive_count - negative_count) / max(total_words / 10, 1)
        return max(-1.0, min(1.0, score))
    
    def _get_sentiment_label(self, score: float) -> str:
        """获取情绪标签"""
        if score > 0.3:
            return "积极"
        elif score < -0.3:
            return "消极"
        else:
            return "中性"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简化的关键词提取
        important_words = [
            "业绩", "财报", "营收", "利润", "增长", "市场", "产品", "技术",
            "合作", "收购", "投资", "政策", "监管", "竞争", "创新", "发展"
        ]
        
        keywords = []
        text_lower = text.lower()
        
        for word in important_words:
            if word in text_lower:
                keywords.append(word)
        
        return keywords[:10]  # 最多返回10个关键词
    
    async def _get_mock_news_data(self, symbol: str, days: int) -> Dict[str, Any]:
        """获取模拟新闻数据"""
        mock_news = [
            {
                "title": f"{symbol}公司发布最新财报，业绩超预期",
                "content": f"{symbol}公司今日发布季度财报，营收和利润均超出市场预期，股价有望上涨。",
                "source": "财经新闻",
                "publish_time": (datetime.now() - timedelta(hours=2)).isoformat(),
                "sentiment": "积极"
            },
            {
                "title": f"分析师上调{symbol}目标价",
                "content": f"多家投行分析师上调{symbol}目标价，认为公司基本面强劲，具有投资价值。",
                "source": "投资研报",
                "publish_time": (datetime.now() - timedelta(hours=6)).isoformat(),
                "sentiment": "积极"
            },
            {
                "title": f"{symbol}面临行业竞争加剧",
                "content": f"{symbol}所在行业竞争日趋激烈，公司需要加强创新以保持竞争优势。",
                "source": "行业分析",
                "publish_time": (datetime.now() - timedelta(days=1)).isoformat(),
                "sentiment": "中性"
            }
        ]
        
        return {
            "success": True,
            "symbol": symbol,
            "days": days,
            "news": mock_news,
            "total": len(mock_news),
            "timestamp": datetime.now().isoformat(),
            "source": "mock"
        }
    
    async def reload(self):
        """重新加载新闻工具"""
        logger.info("🔄 重新加载新闻工具...")
        
        # 清空缓存
        self.cache.clear()
        
        # 重新测试连接
        await self._test_data_service()
        
        logger.info("✅ 新闻工具重新加载完成")
    
    async def cleanup(self):
        """清理资源"""
        logger.info("🧹 清理新闻工具资源...")
        
        if self.session:
            await self.session.close()
            self.session = None
        
        self.cache.clear()
        
        logger.info("✅ 新闻工具资源清理完成")
