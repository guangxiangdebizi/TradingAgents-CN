#!/usr/bin/env python3
"""
国际化管理器
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from threading import Lock

from .config import SupportedLanguage, I18nConfig

class I18nManager:
    """国际化管理器"""
    
    def __init__(self, config: I18nConfig = None):
        self.config = config or I18nConfig()
        self.current_language = self.config.default_language
        self.translations: Dict[SupportedLanguage, Dict[str, str]] = {}
        self._lock = Lock()
        self._load_translations()
    
    def _load_translations(self):
        """加载翻译文件"""
        translations_dir = Path(__file__).parent / "translations"
        
        for lang in SupportedLanguage:
            lang_file = translations_dir / f"{lang.value}.json"
            if lang_file.exists():
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations[lang] = json.load(f)
                except Exception as e:
                    print(f"⚠️ 加载翻译文件失败 {lang.value}: {e}")
                    self.translations[lang] = {}
            else:
                self.translations[lang] = {}
    
    def set_language(self, language: str | SupportedLanguage) -> bool:
        """设置当前语言"""
        try:
            if isinstance(language, str):
                language = I18nConfig.normalize_language(language)
            
            with self._lock:
                self.current_language = language
            return True
        except Exception:
            return False
    
    def get_language(self) -> SupportedLanguage:
        """获取当前语言"""
        return self.current_language
    
    def translate(self, key: str, language: SupportedLanguage = None, **kwargs) -> str:
        """翻译文本"""
        if language is None:
            language = self.current_language
        
        # 获取翻译
        translation = self._get_translation(key, language)
        
        # 如果没有找到翻译，尝试使用回退语言
        if translation == key and language != self.config.fallback_language:
            translation = self._get_translation(key, self.config.fallback_language)
        
        # 格式化参数
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError):
                pass  # 如果格式化失败，返回原始翻译
        
        return translation
    
    def _get_translation(self, key: str, language: SupportedLanguage) -> str:
        """获取指定语言的翻译"""
        if language not in self.translations:
            return key
        
        # 支持嵌套键（如 "api.success.message"）
        keys = key.split('.')
        current = self.translations[language]
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return key  # 未找到翻译
        
        return str(current) if current is not None else key
    
    def get_available_languages(self) -> Dict[str, str]:
        """获取可用语言列表"""
        from .config import LANGUAGE_NAMES
        
        result = {}
        current_lang = self.current_language
        
        for lang in SupportedLanguage:
            if lang in LANGUAGE_NAMES:
                display_name = LANGUAGE_NAMES[lang].get(current_lang, lang.value)
                result[lang.value] = display_name
        
        return result
    
    def detect_language_from_header(self, accept_language: str) -> SupportedLanguage:
        """从 HTTP Accept-Language 头检测语言"""
        if not accept_language:
            return self.config.default_language
        
        # 解析 Accept-Language 头
        languages = []
        for lang_range in accept_language.split(','):
            lang_range = lang_range.strip()
            if ';' in lang_range:
                lang, quality = lang_range.split(';', 1)
                try:
                    q = float(quality.split('=')[1])
                except (IndexError, ValueError):
                    q = 1.0
            else:
                lang, q = lang_range, 1.0
            
            languages.append((lang.strip(), q))
        
        # 按质量排序
        languages.sort(key=lambda x: x[1], reverse=True)
        
        # 尝试匹配支持的语言
        for lang_code, _ in languages:
            try:
                return I18nConfig.normalize_language(lang_code)
            except:
                continue
        
        return self.config.default_language
    
    def add_translation(self, language: SupportedLanguage, key: str, value: str):
        """动态添加翻译"""
        with self._lock:
            if language not in self.translations:
                self.translations[language] = {}
            
            # 支持嵌套键
            keys = key.split('.')
            current = self.translations[language]
            
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            current[keys[-1]] = value
    
    def get_translation_stats(self) -> Dict[str, Any]:
        """获取翻译统计信息"""
        stats = {}
        
        for lang in SupportedLanguage:
            if lang in self.translations:
                stats[lang.value] = {
                    "total_keys": self._count_keys(self.translations[lang]),
                    "loaded": True
                }
            else:
                stats[lang.value] = {
                    "total_keys": 0,
                    "loaded": False
                }
        
        return stats
    
    def _count_keys(self, translations: Dict) -> int:
        """递归计算翻译键的数量"""
        count = 0
        for value in translations.values():
            if isinstance(value, dict):
                count += self._count_keys(value)
            else:
                count += 1
        return count


# 全局实例
_i18n_manager: Optional[I18nManager] = None
_manager_lock = Lock()

def get_i18n_manager() -> I18nManager:
    """获取全局国际化管理器实例"""
    global _i18n_manager
    
    if _i18n_manager is None:
        with _manager_lock:
            if _i18n_manager is None:
                _i18n_manager = I18nManager()
    
    return _i18n_manager

def _(key: str, language: SupportedLanguage = None, **kwargs) -> str:
    """翻译函数的简化版本"""
    return get_i18n_manager().translate(key, language, **kwargs)
