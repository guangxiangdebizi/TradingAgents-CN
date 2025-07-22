#!/usr/bin/env python3
"""
国际化配置
"""

from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass

class SupportedLanguage(Enum):
    """支持的语言"""
    ZH_CN = "zh-CN"  # 简体中文
    ZH_TW = "zh-TW"  # 繁体中文
    EN_US = "en-US"  # 美式英语
    EN_GB = "en-GB"  # 英式英语
    JA_JP = "ja-JP"  # 日语
    KO_KR = "ko-KR"  # 韩语

@dataclass
class I18nConfig:
    """国际化配置"""
    default_language: SupportedLanguage = SupportedLanguage.ZH_CN
    fallback_language: SupportedLanguage = SupportedLanguage.EN_US
    auto_detect: bool = True
    cache_translations: bool = True
    
    # 语言映射（支持简化的语言代码）
    LANGUAGE_MAPPING = {
        "zh": SupportedLanguage.ZH_CN,
        "zh-cn": SupportedLanguage.ZH_CN,
        "zh-hans": SupportedLanguage.ZH_CN,
        "zh-tw": SupportedLanguage.ZH_TW,
        "zh-hant": SupportedLanguage.ZH_TW,
        "en": SupportedLanguage.EN_US,
        "en-us": SupportedLanguage.EN_US,
        "en-gb": SupportedLanguage.EN_GB,
        "ja": SupportedLanguage.JA_JP,
        "ja-jp": SupportedLanguage.JA_JP,
        "ko": SupportedLanguage.KO_KR,
        "ko-kr": SupportedLanguage.KO_KR,
    }
    
    @classmethod
    def normalize_language(cls, lang_code: str) -> SupportedLanguage:
        """标准化语言代码"""
        if not lang_code:
            return cls().default_language
        
        lang_code = lang_code.lower().strip()
        
        # 直接匹配
        if lang_code in cls.LANGUAGE_MAPPING:
            return cls.LANGUAGE_MAPPING[lang_code]
        
        # 尝试匹配语言部分（如 zh-CN-xxx -> zh）
        lang_part = lang_code.split('-')[0]
        if lang_part in cls.LANGUAGE_MAPPING:
            return cls.LANGUAGE_MAPPING[lang_part]
        
        # 默认返回中文
        return cls().default_language

# 语言显示名称
LANGUAGE_NAMES = {
    SupportedLanguage.ZH_CN: {
        SupportedLanguage.ZH_CN: "简体中文",
        SupportedLanguage.ZH_TW: "簡體中文",
        SupportedLanguage.EN_US: "Simplified Chinese",
        SupportedLanguage.EN_GB: "Simplified Chinese",
        SupportedLanguage.JA_JP: "簡体字中国語",
        SupportedLanguage.KO_KR: "중국어 간체",
    },
    SupportedLanguage.ZH_TW: {
        SupportedLanguage.ZH_CN: "繁体中文",
        SupportedLanguage.ZH_TW: "繁體中文",
        SupportedLanguage.EN_US: "Traditional Chinese",
        SupportedLanguage.EN_GB: "Traditional Chinese",
        SupportedLanguage.JA_JP: "繁体字中国語",
        SupportedLanguage.KO_KR: "중국어 번체",
    },
    SupportedLanguage.EN_US: {
        SupportedLanguage.ZH_CN: "英语（美式）",
        SupportedLanguage.ZH_TW: "英語（美式）",
        SupportedLanguage.EN_US: "English (US)",
        SupportedLanguage.EN_GB: "English (US)",
        SupportedLanguage.JA_JP: "英語（アメリカ）",
        SupportedLanguage.KO_KR: "영어 (미국)",
    },
    SupportedLanguage.EN_GB: {
        SupportedLanguage.ZH_CN: "英语（英式）",
        SupportedLanguage.ZH_TW: "英語（英式）",
        SupportedLanguage.EN_US: "English (UK)",
        SupportedLanguage.EN_GB: "English (UK)",
        SupportedLanguage.JA_JP: "英語（イギリス）",
        SupportedLanguage.KO_KR: "영어 (영국)",
    },
    SupportedLanguage.JA_JP: {
        SupportedLanguage.ZH_CN: "日语",
        SupportedLanguage.ZH_TW: "日語",
        SupportedLanguage.EN_US: "Japanese",
        SupportedLanguage.EN_GB: "Japanese",
        SupportedLanguage.JA_JP: "日本語",
        SupportedLanguage.KO_KR: "일본어",
    },
    SupportedLanguage.KO_KR: {
        SupportedLanguage.ZH_CN: "韩语",
        SupportedLanguage.ZH_TW: "韓語",
        SupportedLanguage.EN_US: "Korean",
        SupportedLanguage.EN_GB: "Korean",
        SupportedLanguage.JA_JP: "韓国語",
        SupportedLanguage.KO_KR: "한국어",
    },
}
