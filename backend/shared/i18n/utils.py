#!/usr/bin/env python3
"""
国际化工具函数
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import re

from .manager import get_i18n_manager
from .config import SupportedLanguage

def format_currency(amount: float, currency: str = "CNY", language: SupportedLanguage = None) -> str:
    """格式化货币"""
    i18n = get_i18n_manager()
    if language is None:
        language = i18n.get_language()
    
    # 货币符号映射
    currency_symbols = {
        "CNY": {"zh-CN": "¥", "zh-TW": "¥", "en-US": "¥", "en-GB": "¥", "ja-JP": "¥", "ko-KR": "¥"},
        "USD": {"zh-CN": "$", "zh-TW": "$", "en-US": "$", "en-GB": "$", "ja-JP": "$", "ko-KR": "$"},
        "HKD": {"zh-CN": "HK$", "zh-TW": "HK$", "en-US": "HK$", "en-GB": "HK$", "ja-JP": "HK$", "ko-KR": "HK$"},
        "JPY": {"zh-CN": "¥", "zh-TW": "¥", "en-US": "¥", "en-GB": "¥", "ja-JP": "¥", "ko-KR": "¥"},
        "KRW": {"zh-CN": "₩", "zh-TW": "₩", "en-US": "₩", "en-GB": "₩", "ja-JP": "₩", "ko-KR": "₩"},
    }
    
    symbol = currency_symbols.get(currency, {}).get(language.value, currency)
    
    # 格式化数字
    if language.value.startswith("zh"):
        # 中文：使用万、亿单位
        if amount >= 100000000:  # 亿
            return f"{symbol}{amount/100000000:.2f}亿"
        elif amount >= 10000:  # 万
            return f"{symbol}{amount/10000:.2f}万"
        else:
            return f"{symbol}{amount:,.2f}"
    else:
        # 英文：使用千分位分隔符
        return f"{symbol}{amount:,.2f}"

def format_percentage(value: float, language: SupportedLanguage = None) -> str:
    """格式化百分比"""
    if language is None:
        language = get_i18n_manager().get_language()
    
    if value > 0:
        prefix = "+" if language.value.startswith("en") else "+"
    else:
        prefix = ""
    
    return f"{prefix}{value:.2f}%"

def format_volume(volume: int, language: SupportedLanguage = None) -> str:
    """格式化成交量"""
    if language is None:
        language = get_i18n_manager().get_language()
    
    if language.value.startswith("zh"):
        # 中文：使用万、亿单位
        if volume >= 100000000:  # 亿
            return f"{volume/100000000:.2f}亿"
        elif volume >= 10000:  # 万
            return f"{volume/10000:.2f}万"
        else:
            return f"{volume:,}"
    else:
        # 英文：使用千分位分隔符
        if volume >= 1000000000:  # B
            return f"{volume/1000000000:.2f}B"
        elif volume >= 1000000:  # M
            return f"{volume/1000000:.2f}M"
        elif volume >= 1000:  # K
            return f"{volume/1000:.2f}K"
        else:
            return f"{volume:,}"

def format_relative_time(dt: datetime, language: SupportedLanguage = None) -> str:
    """格式化相对时间"""
    i18n = get_i18n_manager()
    if language is None:
        language = i18n.get_language()
    
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return i18n.translate("time.days_ago", language, days=diff.days)
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return i18n.translate("time.hours_ago", language, hours=hours)
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return i18n.translate("time.minutes_ago", language, minutes=minutes)
    else:
        return i18n.translate("time.now", language)

def translate_market_type(market_type: str, language: SupportedLanguage = None) -> str:
    """翻译市场类型"""
    i18n = get_i18n_manager()
    
    market_mappings = {
        "A股": "market.a_stock",
        "港股": "market.hk_stock", 
        "美股": "market.us_stock",
        "数字货币": "market.crypto",
        "A-Share": "market.a_stock",
        "HK Stock": "market.hk_stock",
        "US Stock": "market.us_stock",
        "Cryptocurrency": "market.crypto"
    }
    
    key = market_mappings.get(market_type)
    if key:
        return i18n.translate(key, language)
    
    return market_type

def translate_data_source(source: str, language: SupportedLanguage = None) -> str:
    """翻译数据源"""
    i18n = get_i18n_manager()
    
    source_mappings = {
        "tushare": "data_source.tushare",
        "akshare": "data_source.akshare",
        "yfinance": "data_source.yfinance",
        "finnhub": "data_source.finnhub",
        "baostock": "data_source.baostock"
    }
    
    key = source_mappings.get(source.lower())
    if key:
        return i18n.translate(key, language)
    
    return source

def translate_recommendation(recommendation: str, language: SupportedLanguage = None) -> str:
    """翻译投资建议"""
    i18n = get_i18n_manager()
    
    rec_mappings = {
        "买入": "analysis.recommendation.buy",
        "卖出": "analysis.recommendation.sell",
        "持有": "analysis.recommendation.hold",
        "强烈买入": "analysis.recommendation.strong_buy",
        "强烈卖出": "analysis.recommendation.strong_sell",
        "buy": "analysis.recommendation.buy",
        "sell": "analysis.recommendation.sell",
        "hold": "analysis.recommendation.hold",
        "strong_buy": "analysis.recommendation.strong_buy",
        "strong_sell": "analysis.recommendation.strong_sell"
    }
    
    key = rec_mappings.get(recommendation.lower())
    if key:
        return i18n.translate(key, language)
    
    return recommendation

def localize_stock_data(data: Dict[str, Any], language: SupportedLanguage = None) -> Dict[str, Any]:
    """本地化股票数据"""
    if not isinstance(data, dict):
        return data
    
    i18n = get_i18n_manager()
    if language is None:
        language = i18n.get_language()
    
    localized = data.copy()
    
    # 翻译字段名
    field_mappings = {
        "symbol": "data.stock.symbol",
        "name": "data.stock.name",
        "market": "data.stock.market",
        "industry": "data.stock.industry",
        "sector": "data.stock.sector",
        "market_cap": "data.stock.market_cap",
        "currency": "data.stock.currency",
        "price": "data.stock.price",
        "change": "data.stock.change",
        "change_percent": "data.stock.change_percent",
        "volume": "data.stock.volume",
        "amount": "data.stock.amount",
        "open": "data.stock.open",
        "high": "data.stock.high",
        "low": "data.stock.low",
        "close": "data.stock.close"
    }
    
    # 如果需要翻译字段名（通常用于前端显示）
    if language != SupportedLanguage.ZH_CN:
        localized["_field_names"] = {}
        for field, key in field_mappings.items():
            if field in data:
                localized["_field_names"][field] = i18n.translate(key, language)
    
    # 格式化数值
    if "market_cap" in localized and isinstance(localized["market_cap"], (int, float)):
        currency = localized.get("currency", "CNY")
        localized["market_cap_formatted"] = format_currency(localized["market_cap"], currency, language)
    
    if "volume" in localized and isinstance(localized["volume"], int):
        localized["volume_formatted"] = format_volume(localized["volume"], language)
    
    if "change_percent" in localized and isinstance(localized["change_percent"], (int, float)):
        localized["change_percent_formatted"] = format_percentage(localized["change_percent"], language)
    
    # 翻译市场类型
    if "market" in localized:
        localized["market_translated"] = translate_market_type(localized["market"], language)
    
    return localized

def get_language_from_request_header(accept_language: str) -> SupportedLanguage:
    """从请求头获取语言"""
    return get_i18n_manager().detect_language_from_header(accept_language)

def validate_language_code(lang_code: str) -> bool:
    """验证语言代码是否有效"""
    try:
        from .config import I18nConfig
        I18nConfig.normalize_language(lang_code)
        return True
    except:
        return False

def get_supported_languages() -> List[Dict[str, str]]:
    """获取支持的语言列表"""
    i18n = get_i18n_manager()
    languages = i18n.get_available_languages()
    
    result = []
    for code, name in languages.items():
        result.append({
            "code": code,
            "name": name,
            "native_name": name  # 可以添加原生语言名称
        })
    
    return result
