#!/usr/bin/env python3
"""
简单的国际化功能测试
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_basic_i18n():
    """测试基础国际化功能"""
    print("🌍 测试基础国际化功能")
    print("=" * 40)
    
    from backend.shared.i18n import get_i18n_manager, _
    
    i18n = get_i18n_manager()
    
    # 测试中文
    print("📋 中文测试:")
    i18n.set_language("zh-CN")
    print(f"  当前语言: {i18n.get_language().value}")
    print(f"  通用翻译: {_('common.success')}")
    print(f"  API翻译: {_('api.success.stock_info')}")
    print(f"  错误翻译: {_('api.error.stock_not_found')}")
    
    # 测试英文
    print("\n📋 英文测试:")
    i18n.set_language("en-US")
    print(f"  当前语言: {i18n.get_language().value}")
    print(f"  通用翻译: {_('common.success')}")
    print(f"  API翻译: {_('api.success.stock_info')}")
    print(f"  错误翻译: {_('api.error.stock_not_found')}")
    
    # 测试日文
    print("\n📋 日文测试:")
    i18n.set_language("ja-JP")
    print(f"  当前语言: {i18n.get_language().value}")
    print(f"  通用翻译: {_('common.success')}")
    print(f"  API翻译: {_('api.success.stock_info')}")
    print(f"  错误翻译: {_('api.error.stock_not_found')}")
    
    # 测试参数化翻译
    print("\n📋 参数化翻译测试:")
    i18n.set_language("zh-CN")
    print(f"  中文: {_('time.minutes_ago', minutes=5)}")
    i18n.set_language("en-US")
    print(f"  英文: {_('time.minutes_ago', minutes=5)}")
    i18n.set_language("ja-JP")
    print(f"  日文: {_('time.minutes_ago', minutes=5)}")

def test_language_detection():
    """测试语言检测"""
    print("\n🔍 测试语言检测")
    print("=" * 40)
    
    from backend.shared.i18n import get_i18n_manager
    from backend.shared.i18n.config import I18nConfig
    
    i18n = get_i18n_manager()
    
    test_headers = [
        "zh-CN,zh;q=0.9,en;q=0.8",
        "en-US,en;q=0.9",
        "ja-JP,ja;q=0.9,en;q=0.8",
        "ko-KR,ko;q=0.9",
        "fr-FR,fr;q=0.9",  # 不支持的语言
    ]
    
    for header in test_headers:
        detected = i18n.detect_language_from_header(header)
        print(f"  {header} -> {detected.value}")

def test_data_localization():
    """测试数据本地化"""
    print("\n🔄 测试数据本地化")
    print("=" * 40)
    
    from backend.shared.i18n.utils import (
        format_currency, format_percentage, format_volume,
        translate_market_type, localize_stock_data
    )
    from backend.shared.i18n.config import SupportedLanguage
    
    # 测试货币格式化
    print("💰 货币格式化:")
    amount = 1234567.89
    for lang in [SupportedLanguage.ZH_CN, SupportedLanguage.EN_US, SupportedLanguage.JA_JP]:
        formatted = format_currency(amount, "CNY", lang)
        print(f"  {lang.value}: {formatted}")
    
    # 测试成交量格式化
    print("\n📊 成交量格式化:")
    volume = 12345678
    for lang in [SupportedLanguage.ZH_CN, SupportedLanguage.EN_US, SupportedLanguage.JA_JP]:
        formatted = format_volume(volume, lang)
        print(f"  {lang.value}: {formatted}")
    
    # 测试百分比格式化
    print("\n📈 百分比格式化:")
    percentage = 5.67
    for lang in [SupportedLanguage.ZH_CN, SupportedLanguage.EN_US, SupportedLanguage.JA_JP]:
        formatted = format_percentage(percentage, lang)
        print(f"  {lang.value}: {formatted}")
    
    # 测试市场类型翻译
    print("\n🏢 市场类型翻译:")
    market_types = ["A股", "港股", "美股"]
    for market in market_types:
        for lang in [SupportedLanguage.ZH_CN, SupportedLanguage.EN_US, SupportedLanguage.JA_JP]:
            translated = translate_market_type(market, lang)
            print(f"  {market} ({lang.value}): {translated}")

def test_translation_stats():
    """测试翻译统计"""
    print("\n📊 测试翻译统计")
    print("=" * 40)
    
    from backend.shared.i18n import get_i18n_manager
    
    i18n = get_i18n_manager()
    stats = i18n.get_translation_stats()
    
    print("翻译统计:")
    for lang, info in stats.items():
        status = "✅ 已加载" if info.get("loaded") else "❌ 未加载"
        print(f"  {lang}: {info.get('total_keys', 0)} 个翻译键 {status}")

def test_available_languages():
    """测试可用语言"""
    print("\n🌍 测试可用语言")
    print("=" * 40)
    
    from backend.shared.i18n import get_i18n_manager
    
    i18n = get_i18n_manager()
    
    # 测试不同语言下的语言列表显示
    for lang_code in ["zh-CN", "en-US", "ja-JP"]:
        i18n.set_language(lang_code)
        languages = i18n.get_available_languages()
        print(f"\n{lang_code} 视角下的语言列表:")
        for code, name in languages.items():
            print(f"  {code}: {name}")

def main():
    """主函数"""
    print("🧪 TradingAgents 国际化功能测试")
    print("=" * 50)
    
    try:
        test_basic_i18n()
        test_language_detection()
        test_data_localization()
        test_translation_stats()
        test_available_languages()
        
        print("\n🎉 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
