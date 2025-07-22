#!/usr/bin/env python3
"""
API调试中间件
"""

import time
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from .logger import get_i18n_logger

class APIDebugMiddleware(BaseHTTPMiddleware):
    """API调试中间件 - 记录详细的API调用信息"""
    
    def __init__(self, app, enable_debug: bool = True, log_headers: bool = False, log_body: bool = False):
        super().__init__(app)
        self.enable_debug = enable_debug
        self.log_headers = log_headers
        self.log_body = log_body
        self.debug_logger = get_i18n_logger("api-debug")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        if not self.enable_debug:
            return await call_next(request)
        
        start_time = time.time()
        
        # 记录请求开始
        self._log_request_start(request)
        
        # 记录请求详情
        await self._log_request_details(request)
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        duration = int((time.time() - start_time) * 1000)
        
        # 记录响应详情
        self._log_response_details(response, duration)
        
        return response
    
    def _log_request_start(self, request: Request):
        """记录请求开始"""
        self.debug_logger.debug_api_request_received(
            method=request.method,
            path=str(request.url.path)
        )
    
    async def _log_request_details(self, request: Request):
        """记录请求详情"""
        try:
            # 记录查询参数
            if request.query_params:
                params_str = str(dict(request.query_params))
                self.debug_logger.debug_api_request_params(params=params_str)
            
            # 记录请求头（如果启用）
            if self.log_headers:
                # 过滤敏感头部
                safe_headers = {}
                for key, value in request.headers.items():
                    if key.lower() not in ['authorization', 'cookie', 'x-api-key']:
                        safe_headers[key] = value
                    else:
                        safe_headers[key] = "***"
                
                headers_str = json.dumps(safe_headers, ensure_ascii=False)
                self.debug_logger.debug_api_request_headers(headers=headers_str)
            
            # 记录请求体（如果启用且是POST/PUT请求）
            if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.body()
                    if body:
                        # 限制body大小，避免日志过大
                        body_str = body.decode('utf-8')[:1000]
                        if len(body) > 1000:
                            body_str += "... (truncated)"
                        self.debug_logger.debug("log.debug.api.request_body", body=body_str)
                except Exception:
                    pass  # 忽略body读取错误
        
        except Exception as e:
            self.debug_logger.debug("log.debug.api.request_details_error", error=str(e))
    
    def _log_response_details(self, response: Response, duration: int):
        """记录响应详情"""
        try:
            # 记录响应状态
            self.debug_logger.debug_api_response_prepared(status_code=response.status_code)
            
            # 记录响应大小
            if hasattr(response, 'body') and response.body:
                data_size = len(response.body)
                self.debug_logger.debug_api_response_data(data_size=data_size)
            
            # 记录响应时间
            self.debug_logger.debug_api_response_sent(duration=duration)
            
            # 慢请求警告
            if duration > 1000:  # 超过1秒的请求
                self.debug_logger.debug_slow_query(
                    query=f"{response.status_code}",
                    duration=duration,
                    threshold=1000
                )
        
        except Exception as e:
            self.debug_logger.debug("log.debug.api.response_details_error", error=str(e))


class PerformanceMonitorMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""
    
    def __init__(self, app, enable_monitoring: bool = True):
        super().__init__(app)
        self.enable_monitoring = enable_monitoring
        self.debug_logger = get_i18n_logger("performance-monitor")
        self.request_count = 0
        self.total_time = 0
        self.slow_requests = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        if not self.enable_monitoring:
            return await call_next(request)
        
        start_time = time.time()
        
        # 记录查询开始
        self.debug_logger.debug_query_start(
            query_type="api_request",
            symbol=request.url.path
        )
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        duration = int((time.time() - start_time) * 1000)
        
        # 更新统计
        self.request_count += 1
        self.total_time += duration
        
        if duration > 500:  # 超过500ms的请求
            self.slow_requests += 1
        
        # 记录查询完成
        self.debug_logger.debug_query_end(
            query_type="api_request",
            duration=duration
        )
        
        # 每100个请求输出一次性能统计
        if self.request_count % 100 == 0:
            avg_time = self.total_time / self.request_count
            slow_rate = (self.slow_requests / self.request_count) * 100
            
            self.debug_logger.debug("log.debug.performance.api_summary",
                requests=self.request_count,
                avg_time=avg_time,
                slow_rate=slow_rate
            )
        
        return response


class ValidationDebugMiddleware(BaseHTTPMiddleware):
    """验证调试中间件"""
    
    def __init__(self, app, enable_validation_debug: bool = True):
        super().__init__(app)
        self.enable_validation_debug = enable_validation_debug
        self.debug_logger = get_i18n_logger("validation-debug")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        if not self.enable_validation_debug:
            return await call_next(request)
        
        # 记录中间件开始
        middleware_start = time.time()
        self.debug_logger.debug_middleware_start("ValidationDebugMiddleware")
        
        # 验证请求参数
        await self._validate_request(request)
        
        # 处理请求
        response = await call_next(request)
        
        # 验证响应
        self._validate_response(response)
        
        # 记录中间件完成
        middleware_duration = int((time.time() - middleware_start) * 1000)
        self.debug_logger.debug_middleware_end("ValidationDebugMiddleware", middleware_duration)
        
        return response
    
    async def _validate_request(self, request: Request):
        """验证请求"""
        try:
            # 验证路径参数
            if hasattr(request, 'path_params') and request.path_params:
                for key, value in request.path_params.items():
                    self.debug_logger.debug_validation_start(f"path_param.{key}")
                    if value:
                        self.debug_logger.debug_validation_passed(f"path_param.{key}")
                    else:
                        self.debug_logger.debug_validation_failed(f"path_param.{key}", "empty_value")
            
            # 验证查询参数
            if request.query_params:
                for key, value in request.query_params.items():
                    self.debug_logger.debug_validation_start(f"query_param.{key}")
                    if value:
                        self.debug_logger.debug_validation_passed(f"query_param.{key}")
                    else:
                        self.debug_logger.debug_validation_failed(f"query_param.{key}", "empty_value")
        
        except Exception as e:
            self.debug_logger.debug("log.debug.api.validation_error", error=str(e))
    
    def _validate_response(self, response: Response):
        """验证响应"""
        try:
            # 验证响应状态码
            self.debug_logger.debug_validation_start("response.status_code")
            if 200 <= response.status_code < 300:
                self.debug_logger.debug_validation_passed("response.status_code")
            elif 400 <= response.status_code < 500:
                self.debug_logger.debug_validation_failed("response.status_code", "client_error")
            elif response.status_code >= 500:
                self.debug_logger.debug_validation_failed("response.status_code", "server_error")
        
        except Exception as e:
            self.debug_logger.debug("log.debug.api.response_validation_error", error=str(e))
