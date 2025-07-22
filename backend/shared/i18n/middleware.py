#!/usr/bin/env python3
"""
国际化中间件
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Any
import json

from .manager import get_i18n_manager
from .config import SupportedLanguage

class I18nMiddleware(BaseHTTPMiddleware):
    """国际化中间件"""
    
    def __init__(self, app, auto_detect: bool = True):
        super().__init__(app)
        self.auto_detect = auto_detect
        self.i18n_manager = get_i18n_manager()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 检测语言
        if self.auto_detect:
            self._detect_and_set_language(request)
        
        # 处理请求
        response = await call_next(request)
        
        # 如果是JSON响应，进行国际化处理
        if isinstance(response, JSONResponse):
            response = await self._process_json_response(response)
        
        # 添加语言头
        response.headers["Content-Language"] = self.i18n_manager.get_language().value
        
        return response
    
    def _detect_and_set_language(self, request: Request):
        """检测并设置语言"""
        # 优先级：查询参数 > 头部 > Cookie > 默认
        
        # 1. 查询参数
        lang = request.query_params.get('lang') or request.query_params.get('language')
        if lang:
            if self.i18n_manager.set_language(lang):
                return
        
        # 2. 自定义头部
        lang = request.headers.get('X-Language') or request.headers.get('Accept-Language')
        if lang:
            detected_lang = self.i18n_manager.detect_language_from_header(lang)
            self.i18n_manager.set_language(detected_lang)
            return
        
        # 3. Cookie
        lang = request.cookies.get('language')
        if lang:
            if self.i18n_manager.set_language(lang):
                return
    
    async def _process_json_response(self, response: JSONResponse) -> JSONResponse:
        """处理JSON响应的国际化"""
        try:
            # 获取响应内容
            content = response.body.decode('utf-8')
            data = json.loads(content)
            
            # 处理标准API响应格式
            if isinstance(data, dict):
                # 翻译消息字段
                if 'message' in data and isinstance(data['message'], str):
                    data['message'] = self._translate_message(data['message'])
                
                # 翻译错误信息
                if 'error' in data and isinstance(data['error'], str):
                    data['error'] = self._translate_message(data['error'])
                
                # 翻译详细错误信息
                if 'detail' in data and isinstance(data['detail'], str):
                    data['detail'] = self._translate_message(data['detail'])
            
            # 创建新的响应
            new_content = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            return JSONResponse(
                content=data,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        except Exception:
            # 如果处理失败，返回原始响应
            return response
    
    def _translate_message(self, message: str) -> str:
        """翻译消息"""
        # 尝试匹配常见的消息模式
        message_mappings = {
            # 成功消息
            "获取股票信息成功": "api.success.stock_info",
            "获取股票数据成功": "api.success.stock_data",
            "获取基本面数据成功": "api.success.fundamentals",
            "获取新闻数据成功": "api.success.news",
            "强制刷新数据成功": "api.success.refresh",
            "清理旧数据成功": "api.success.cleanup",
            "获取本地数据摘要成功": "api.success.summary",
            "获取数据历史成功": "api.success.history",
            
            # 错误消息
            "未找到股票信息": "api.error.stock_not_found",
            "无效的股票代码": "api.error.invalid_symbol",
            "无效的日期格式": "api.error.invalid_date",
            "数据源不可用": "api.error.data_source_unavailable",
            "数据库错误": "api.error.database_error",
            "缓存错误": "api.error.cache_error",
            "网络错误": "api.error.network_error",
            "请求超时": "api.error.timeout",
            "认证失败": "api.error.authentication_failed",
            "权限不足": "api.error.permission_denied",
            "内部服务器错误": "api.error.internal_error",
        }
        
        # 检查是否有直接映射
        if message in message_mappings:
            return self.i18n_manager.translate(message_mappings[message])
        
        # 检查是否包含特定模式
        for pattern, key in message_mappings.items():
            if pattern in message:
                translated = self.i18n_manager.translate(key)
                return message.replace(pattern, translated)
        
        # 如果没有找到映射，返回原始消息
        return message


class I18nResponseHelper:
    """国际化响应助手"""
    
    def __init__(self):
        self.i18n_manager = get_i18n_manager()
    
    def success_response(self, message_key: str, data: Any = None, **kwargs) -> dict:
        """创建成功响应"""
        return {
            "success": True,
            "message": self.i18n_manager.translate(message_key, **kwargs),
            "data": data,
            "error_code": None,
            "timestamp": self._get_timestamp()
        }
    
    def error_response(self, message_key: str, error_code: str = None, **kwargs) -> dict:
        """创建错误响应"""
        return {
            "success": False,
            "message": self.i18n_manager.translate(message_key, **kwargs),
            "data": None,
            "error_code": error_code,
            "timestamp": self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 全局响应助手实例
i18n_response = I18nResponseHelper()
