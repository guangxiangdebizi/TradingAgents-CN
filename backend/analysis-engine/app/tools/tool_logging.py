#!/usr/bin/env python3
"""
工具调用日志系统
基于tradingagents的日志设计
"""

import time
import logging
import functools
from typing import Any, Callable, Dict, Optional
from datetime import datetime
import json

# 创建专用的工具日志记录器
tool_logger = logging.getLogger('tradingagents.tools')
tool_logger.setLevel(logging.INFO)

# 如果没有处理器，添加一个控制台处理器
if not tool_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(name)s - %(message)s'
    )
    handler.setFormatter(formatter)
    tool_logger.addHandler(handler)

def log_tool_call(tool_name: str = None, log_args: bool = True, log_result: bool = False):
    """
    工具调用日志装饰器
    
    Args:
        tool_name: 工具名称，如果为None则使用函数名
        log_args: 是否记录参数
        log_result: 是否记录结果
    """
    def decorator(func: Callable) -> Callable:
        name = tool_name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 准备参数信息
            args_info = None
            if log_args:
                try:
                    # 只记录关键参数，避免敏感信息
                    safe_kwargs = {}
                    for key, value in kwargs.items():
                        if key.lower() in ['password', 'token', 'key', 'secret']:
                            safe_kwargs[key] = '***'
                        else:
                            safe_kwargs[key] = str(value)[:100]  # 限制长度
                    args_info = {
                        'args_count': len(args),
                        'kwargs': safe_kwargs
                    }
                except Exception:
                    args_info = {'args_count': len(args), 'kwargs_count': len(kwargs)}
            
            # 记录工具调用开始
            tool_logger.info(
                f"🔧 [工具调用] {name} - 开始",
                extra={
                    'tool_name': name,
                    'event_type': 'tool_call_start',
                    'timestamp': datetime.now().isoformat(),
                    'args_info': args_info if log_args else None
                }
            )
            
            try:
                # 执行工具函数
                result = func(*args, **kwargs)
                
                # 计算执行时间
                duration = time.time() - start_time
                
                # 准备结果信息
                result_info = None
                if log_result and result is not None:
                    result_str = str(result)
                    result_info = result_str[:200] + '...' if len(result_str) > 200 else result_str
                
                # 记录工具调用成功
                tool_logger.info(
                    f"✅ [工具调用] {name} - 完成 (耗时: {duration:.2f}s)",
                    extra={
                        'tool_name': name,
                        'event_type': 'tool_call_success',
                        'duration': duration,
                        'result_info': result_info if log_result else None,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # 记录工具调用失败
                tool_logger.error(
                    f"❌ [工具调用] {name} - 失败 (耗时: {duration:.2f}s): {str(e)}",
                    extra={
                        'tool_name': name,
                        'event_type': 'tool_call_error',
                        'duration': duration,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    },
                    exc_info=True
                )
                
                raise
        
        return wrapper
    return decorator

def log_async_tool_call(tool_name: str = None, log_args: bool = True, log_result: bool = False):
    """
    异步工具调用日志装饰器
    
    Args:
        tool_name: 工具名称，如果为None则使用函数名
        log_args: 是否记录参数
        log_result: 是否记录结果
    """
    def decorator(func: Callable) -> Callable:
        name = tool_name or func.__name__
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 准备参数信息
            args_info = None
            if log_args:
                try:
                    # 只记录关键参数，避免敏感信息
                    safe_kwargs = {}
                    for key, value in kwargs.items():
                        if key.lower() in ['password', 'token', 'key', 'secret']:
                            safe_kwargs[key] = '***'
                        else:
                            safe_kwargs[key] = str(value)[:100]  # 限制长度
                    args_info = {
                        'args_count': len(args),
                        'kwargs': safe_kwargs
                    }
                except Exception:
                    args_info = {'args_count': len(args), 'kwargs_count': len(kwargs)}
            
            # 记录工具调用开始
            tool_logger.info(
                f"🔧 [异步工具调用] {name} - 开始",
                extra={
                    'tool_name': name,
                    'event_type': 'async_tool_call_start',
                    'timestamp': datetime.now().isoformat(),
                    'args_info': args_info if log_args else None
                }
            )
            
            try:
                # 执行异步工具函数
                result = await func(*args, **kwargs)
                
                # 计算执行时间
                duration = time.time() - start_time
                
                # 准备结果信息
                result_info = None
                if log_result and result is not None:
                    result_str = str(result)
                    result_info = result_str[:200] + '...' if len(result_str) > 200 else result_str
                
                # 记录工具调用成功
                tool_logger.info(
                    f"✅ [异步工具调用] {name} - 完成 (耗时: {duration:.2f}s)",
                    extra={
                        'tool_name': name,
                        'event_type': 'async_tool_call_success',
                        'duration': duration,
                        'result_info': result_info if log_result else None,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # 记录工具调用失败
                tool_logger.error(
                    f"❌ [异步工具调用] {name} - 失败 (耗时: {duration:.2f}s): {str(e)}",
                    extra={
                        'tool_name': name,
                        'event_type': 'async_tool_call_error',
                        'duration': duration,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    },
                    exc_info=True
                )
                
                raise
        
        return wrapper
    return decorator

def log_llm_call(provider: str = None, model: str = None):
    """
    LLM调用日志装饰器
    
    Args:
        provider: LLM提供商
        model: 模型名称
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 从参数中提取provider和model信息
            actual_provider = provider or kwargs.get('provider', 'unknown')
            actual_model = model or kwargs.get('model', 'unknown')
            
            # 记录LLM调用开始
            tool_logger.info(
                f"🤖 [LLM调用] {actual_provider}/{actual_model} - 开始",
                extra={
                    'llm_provider': actual_provider,
                    'llm_model': actual_model,
                    'event_type': 'llm_call_start',
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            try:
                # 执行LLM调用
                result = await func(*args, **kwargs)
                
                # 计算执行时间
                duration = time.time() - start_time
                
                # 记录LLM调用成功
                tool_logger.info(
                    f"✅ [LLM调用] {actual_provider}/{actual_model} - 完成 (耗时: {duration:.2f}s)",
                    extra={
                        'llm_provider': actual_provider,
                        'llm_model': actual_model,
                        'event_type': 'llm_call_success',
                        'duration': duration,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                tool_logger.error(
                    f"❌ [LLM调用] {actual_provider}/{actual_model} - 失败 (耗时: {duration:.2f}s): {str(e)}",
                    extra={
                        'llm_provider': actual_provider,
                        'llm_model': actual_model,
                        'event_type': 'llm_call_error',
                        'duration': duration,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    },
                    exc_info=True
                )
                
                raise
        
        return wrapper
    return decorator

# 便捷函数
def log_tool_usage(tool_name: str, symbol: str = None, **extra_data):
    """
    记录工具使用情况的便捷函数
    
    Args:
        tool_name: 工具名称
        symbol: 股票代码（可选）
        **extra_data: 额外的数据
    """
    extra = {
        'tool_name': tool_name,
        'event_type': 'tool_usage',
        'timestamp': datetime.now().isoformat(),
        **extra_data
    }
    
    if symbol:
        extra['symbol'] = symbol
    
    tool_logger.info(f"📋 [工具使用] {tool_name}", extra=extra)

def log_analysis_start(analysis_type: str, symbol: str, **extra_data):
    """
    记录分析开始的便捷函数
    
    Args:
        analysis_type: 分析类型
        symbol: 股票代码
        **extra_data: 额外的数据
    """
    extra = {
        'analysis_type': analysis_type,
        'symbol': symbol,
        'event_type': 'analysis_start',
        'timestamp': datetime.now().isoformat(),
        **extra_data
    }
    
    tool_logger.info(f"🔍 [分析开始] {analysis_type} - {symbol}", extra=extra)

def log_analysis_complete(analysis_type: str, symbol: str, duration: float = None, **extra_data):
    """
    记录分析完成的便捷函数
    
    Args:
        analysis_type: 分析类型
        symbol: 股票代码
        duration: 分析耗时
        **extra_data: 额外的数据
    """
    extra = {
        'analysis_type': analysis_type,
        'symbol': symbol,
        'event_type': 'analysis_complete',
        'timestamp': datetime.now().isoformat(),
        **extra_data
    }
    
    if duration is not None:
        extra['duration'] = duration
    
    tool_logger.info(f"✅ [分析完成] {analysis_type} - {symbol}", extra=extra)
