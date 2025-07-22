#!/usr/bin/env python3
"""
国际化日志器
"""

import logging
import time
from typing import Any, Dict, Optional
from datetime import datetime

from .manager import get_i18n_manager
from .config import SupportedLanguage

class I18nLogger:
    """国际化日志器"""
    
    def __init__(self, name: str, language: SupportedLanguage = None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.i18n_manager = get_i18n_manager()
        self._language = language
        
        # 设置默认格式
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def set_language(self, language: SupportedLanguage):
        """设置日志语言"""
        self._language = language
    
    def get_language(self) -> SupportedLanguage:
        """获取当前日志语言"""
        if self._language:
            return self._language
        return self.i18n_manager.get_language()
    
    def _translate_log_message(self, key: str, **kwargs) -> str:
        """翻译日志消息"""
        language = self.get_language()
        return self.i18n_manager.translate(key, language, **kwargs)
    
    def _log(self, level: int, key: str, **kwargs):
        """内部日志方法"""
        try:
            message = self._translate_log_message(key, **kwargs)
            self.logger.log(level, message)
        except Exception as e:
            # 如果翻译失败，使用原始键和参数
            fallback_message = f"{key} {kwargs}" if kwargs else key
            self.logger.log(level, f"[Translation Error] {fallback_message}")
    
    def debug(self, key: str, **kwargs):
        """调试日志"""
        self._log(logging.DEBUG, key, **kwargs)
    
    def info(self, key: str, **kwargs):
        """信息日志"""
        self._log(logging.INFO, key, **kwargs)
    
    def warning(self, key: str, **kwargs):
        """警告日志"""
        self._log(logging.WARNING, key, **kwargs)
    
    def error(self, key: str, **kwargs):
        """错误日志"""
        self._log(logging.ERROR, key, **kwargs)
    
    def critical(self, key: str, **kwargs):
        """严重错误日志"""
        self._log(logging.CRITICAL, key, **kwargs)
    
    # 数据服务专用日志方法
    def startup(self):
        """服务启动日志"""
        self.info("log.data_service.startup")
    
    def startup_complete(self):
        """服务启动完成日志"""
        self.info("log.data_service.startup_complete")
    
    def shutdown(self):
        """服务关闭日志"""
        self.info("log.data_service.shutdown")
    
    def shutdown_complete(self):
        """服务关闭完成日志"""
        self.info("log.data_service.shutdown_complete")
    
    def database_connected(self):
        """数据库连接成功日志"""
        self.info("log.data_service.database_connected")
    
    def database_error(self, error: str):
        """数据库错误日志"""
        self.error("log.data_service.database_error", error=error)
    
    def redis_connected(self):
        """Redis连接成功日志"""
        self.info("log.data_service.redis_connected")
    
    def redis_error(self, error: str):
        """Redis错误日志"""
        self.error("log.data_service.redis_error", error=error)
    
    def cache_hit(self, symbol: str, data_type: str):
        """缓存命中日志"""
        self.debug("log.data_service.cache_hit", symbol=symbol, data_type=data_type)
    
    def cache_miss(self, symbol: str, data_type: str):
        """缓存未命中日志"""
        self.debug("log.data_service.cache_miss", symbol=symbol, data_type=data_type)
    
    def cache_expired(self, symbol: str, data_type: str):
        """缓存过期日志"""
        self.debug("log.data_service.cache_expired", symbol=symbol, data_type=data_type)
    
    def cache_updated(self, symbol: str, data_type: str):
        """缓存更新日志"""
        self.debug("log.data_service.cache_updated", symbol=symbol, data_type=data_type)
    
    def data_fetched(self, symbol: str, source: str):
        """数据获取成功日志"""
        self.info("log.data_service.data_fetched", symbol=symbol, source=source)
    
    def data_fetch_failed(self, symbol: str, error: str):
        """数据获取失败日志"""
        self.error("log.data_service.data_fetch_failed", symbol=symbol, error=error)
    
    def data_saved(self, symbol: str, data_type: str):
        """数据保存成功日志"""
        self.info("log.data_service.data_saved", symbol=symbol, data_type=data_type)
    
    def data_save_failed(self, symbol: str, error: str):
        """数据保存失败日志"""
        self.error("log.data_service.data_save_failed", symbol=symbol, error=error)
    
    def cleanup_started(self):
        """开始清理日志"""
        self.info("log.data_service.cleanup_started")
    
    def cleanup_completed(self, count: int):
        """清理完成日志"""
        self.info("log.data_service.cleanup_completed", count=count)
    
    def cleanup_failed(self, error: str):
        """清理失败日志"""
        self.error("log.data_service.cleanup_failed", error=error)
    
    def force_refresh(self, symbol: str, data_type: str):
        """强制刷新日志"""
        self.info("log.data_service.force_refresh", symbol=symbol, data_type=data_type)
    
    def api_request(self, method: str, path: str):
        """API请求日志"""
        self.debug("log.data_service.api_request", method=method, path=path)
    
    def api_response(self, status: int, message: str):
        """API响应日志"""
        self.debug("log.data_service.api_response", status=status, message=message)
    
    def validation_error(self, field: str, error: str):
        """验证错误日志"""
        self.warning("log.data_service.validation_error", field=field, error=error)
    
    def rate_limit_hit(self, source: str):
        """频率限制日志"""
        self.warning("log.data_service.rate_limit_hit", source=source)
    
    def timeout_error(self, url: str):
        """超时错误日志"""
        self.warning("log.data_service.timeout_error", url=url)
    
    def network_error(self, error: str):
        """网络错误日志"""
        self.error("log.data_service.network_error", error=error)
    
    def data_source_unavailable(self, source: str):
        """数据源不可用日志"""
        self.error("log.data_service.data_source_unavailable", source=source)
    
    def data_source_healthy(self, source: str):
        """数据源健康日志"""
        self.info("log.data_service.data_source_healthy", source=source)
    
    def data_source_unhealthy(self, source: str, error: str):
        """数据源异常日志"""
        self.error("log.data_service.data_source_unhealthy", source=source, error=error)
    
    # 数据管理器专用日志方法
    def manager_initialized(self):
        """数据管理器初始化成功"""
        self.info("log.data_manager.initialized")
    
    def manager_initialization_failed(self, error: str):
        """数据管理器初始化失败"""
        self.error("log.data_manager.initialization_failed", error=error)
    
    def processing_request(self, symbol: str, data_type: str):
        """处理数据请求"""
        self.info("log.data_manager.processing_request", symbol=symbol, data_type=data_type)
    
    def request_completed(self, symbol: str, duration: int):
        """数据请求完成"""
        self.info("log.data_manager.request_completed", symbol=symbol, duration=duration)
    
    def request_failed(self, symbol: str, error: str):
        """数据请求失败"""
        self.error("log.data_manager.request_failed", symbol=symbol, error=error)
    
    def cache_strategy(self, strategy: str, ttl: int):
        """缓存策略"""
        self.debug("log.data_manager.cache_strategy", strategy=strategy, ttl=ttl)
    
    def fallback_triggered(self, reason: str):
        """触发回退机制"""
        self.warning("log.data_manager.fallback_triggered", reason=reason)
    
    def batch_processing(self, count: int):
        """批量处理"""
        self.info("log.data_manager.batch_processing", count=count)
    
    def batch_completed(self, success: int, failed: int):
        """批量处理完成"""
        self.info("log.data_manager.batch_completed", success=success, failed=failed)

    # ===== Debug级别日志方法 =====

    # API调试日志
    def debug_api_request_received(self, method: str, path: str):
        """API请求接收"""
        self.debug("log.debug.api.request_received", method=method, path=path)

    def debug_api_request_params(self, params: str):
        """API请求参数"""
        self.debug("log.debug.api.request_params", params=params)

    def debug_api_request_headers(self, headers: str):
        """API请求头"""
        self.debug("log.debug.api.request_headers", headers=headers)

    def debug_api_response_prepared(self, status_code: int):
        """API响应准备"""
        self.debug("log.debug.api.response_prepared", status_code=status_code)

    def debug_api_response_data(self, data_size: int):
        """API响应数据"""
        self.debug("log.debug.api.response_data", data_size=data_size)

    def debug_api_response_sent(self, duration: int):
        """API响应发送"""
        self.debug("log.debug.api.response_sent", duration=duration)

    def debug_middleware_start(self, middleware: str):
        """中间件开始"""
        self.debug("log.debug.api.middleware_start", middleware=middleware)

    def debug_middleware_end(self, middleware: str, duration: int):
        """中间件完成"""
        self.debug("log.debug.api.middleware_end", middleware=middleware, duration=duration)

    def debug_validation_start(self, field: str):
        """验证开始"""
        self.debug("log.debug.api.validation_start", field=field)

    def debug_validation_passed(self, field: str):
        """验证通过"""
        self.debug("log.debug.api.validation_passed", field=field)

    def debug_validation_failed(self, field: str, error: str):
        """验证失败"""
        self.debug("log.debug.api.validation_failed", field=field, error=error)

    # 数据调试日志
    def debug_cache_check_start(self, symbol: str, data_type: str):
        """缓存检查开始"""
        self.debug("log.debug.data.cache_check_start", symbol=symbol, data_type=data_type)

    def debug_cache_check_result(self, result: str, symbol: str):
        """缓存检查结果"""
        self.debug("log.debug.data.cache_check_result", result=result, symbol=symbol)

    def debug_data_source_select(self, source: str, symbol: str):
        """数据源选择"""
        self.debug("log.debug.data.data_source_select", source=source, symbol=symbol)

    def debug_data_source_call(self, source: str, url: str):
        """数据源调用"""
        self.debug("log.debug.data.data_source_call", source=source, url=url)

    def debug_data_source_response(self, source: str, status: str, size: int):
        """数据源响应"""
        self.debug("log.debug.data.data_source_response", source=source, status=status, size=size)

    def debug_data_transform_start(self, from_format: str, to_format: str):
        """数据转换开始"""
        self.debug("log.debug.data.data_transform_start", from_format=from_format, to_format=to_format)

    def debug_data_transform_end(self, records: int):
        """数据转换完成"""
        self.debug("log.debug.data.data_transform_end", records=records)

    def debug_data_validate_start(self, data_type: str):
        """数据验证开始"""
        self.debug("log.debug.data.data_validate_start", data_type=data_type)

    def debug_data_validate_end(self, valid_count: int, total_count: int):
        """数据验证完成"""
        self.debug("log.debug.data.data_validate_end", valid_count=valid_count, total_count=total_count)

    def debug_cache_save_start(self, symbol: str, data_type: str):
        """缓存保存开始"""
        self.debug("log.debug.data.cache_save_start", symbol=symbol, data_type=data_type)

    def debug_cache_save_end(self, symbol: str, ttl: int):
        """缓存保存完成"""
        self.debug("log.debug.data.cache_save_end", symbol=symbol, ttl=ttl)

    def debug_db_save_start(self, collection: str, symbol: str):
        """数据库保存开始"""
        self.debug("log.debug.data.db_save_start", collection=collection, symbol=symbol)

    def debug_db_save_end(self, collection: str, count: int):
        """数据库保存完成"""
        self.debug("log.debug.data.db_save_end", collection=collection, count=count)

    # 系统调试日志
    def debug_memory_usage(self, used: int, total: int, percent: float):
        """内存使用情况"""
        self.debug("log.debug.system.memory_usage", used=used, total=total, percent=percent)

    def debug_cpu_usage(self, percent: float):
        """CPU使用情况"""
        self.debug("log.debug.system.cpu_usage", percent=percent)

    def debug_connection_pool(self, active: int, max_conn: int):
        """连接池状态"""
        self.debug("log.debug.system.connection_pool", active=active, max=max_conn)

    def debug_config_loaded(self, config_file: str, keys: int):
        """配置加载"""
        self.debug("log.debug.system.config_loaded", config_file=config_file, keys=keys)

    def debug_service_health_check(self, service: str, status: str):
        """服务健康检查"""
        self.debug("log.debug.system.service_health_check", service=service, status=status)

    # 性能调试日志
    def debug_query_start(self, query_type: str, symbol: str):
        """查询开始"""
        self.debug("log.debug.performance.query_start", query_type=query_type, symbol=symbol)

    def debug_query_end(self, query_type: str, duration: int):
        """查询完成"""
        self.debug("log.debug.performance.query_end", query_type=query_type, duration=duration)

    def debug_cache_performance(self, hit_rate: float, avg_time: float):
        """缓存性能"""
        self.debug("log.debug.performance.cache_performance", hit_rate=hit_rate, avg_time=avg_time)

    def debug_slow_query(self, query: str, duration: int, threshold: int):
        """慢查询警告"""
        self.warning("log.debug.performance.slow_query", query=query, duration=duration, threshold=threshold)


class I18nLoggerAdapter:
    """国际化日志适配器 - 用于兼容现有代码"""
    
    def __init__(self, logger: I18nLogger):
        self.logger = logger
    
    def debug(self, message: str, *args, **kwargs):
        """调试日志 - 兼容模式"""
        if args or kwargs:
            message = message % args if args else message.format(**kwargs)
        self.logger.logger.debug(message)
    
    def info(self, message: str, *args, **kwargs):
        """信息日志 - 兼容模式"""
        if args or kwargs:
            message = message % args if args else message.format(**kwargs)
        self.logger.logger.info(message)
    
    def warning(self, message: str, *args, **kwargs):
        """警告日志 - 兼容模式"""
        if args or kwargs:
            message = message % args if args else message.format(**kwargs)
        self.logger.logger.warning(message)
    
    def error(self, message: str, *args, **kwargs):
        """错误日志 - 兼容模式"""
        if args or kwargs:
            message = message % args if args else message.format(**kwargs)
        self.logger.logger.error(message)
    
    def critical(self, message: str, *args, **kwargs):
        """严重错误日志 - 兼容模式"""
        if args or kwargs:
            message = message % args if args else message.format(**kwargs)
        self.logger.logger.critical(message)


def get_i18n_logger(name: str, language: SupportedLanguage = None) -> I18nLogger:
    """获取国际化日志器"""
    return I18nLogger(name, language)

def get_compatible_logger(name: str, language: SupportedLanguage = None) -> I18nLoggerAdapter:
    """获取兼容的国际化日志器"""
    i18n_logger = I18nLogger(name, language)
    return I18nLoggerAdapter(i18n_logger)
