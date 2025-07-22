#!/usr/bin/env python3
"""
Debug级别日志功能测试脚本
"""

import sys
import os
import requests
import time
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class DebugLoggingTester:
    """Debug日志测试器"""
    
    def __init__(self):
        self.data_service_url = "http://localhost:8002"
        # 设置日志级别为DEBUG以查看debug日志
        logging.basicConfig(level=logging.DEBUG)
    
    def test_service_health(self):
        """测试服务健康状态"""
        print("🔍 测试 Data Service 健康状态...")
        try:
            response = requests.get(f"{self.data_service_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Data Service 健康")
                return True
            else:
                print(f"❌ Data Service 不健康: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Data Service 连接失败: {e}")
            return False
    
    def test_debug_logging_basic(self):
        """测试基础debug日志功能"""
        print("\n🐛 测试基础Debug日志功能")
        print("=" * 40)
        
        from backend.shared.i18n.logger import get_i18n_logger
        from backend.shared.i18n.config import SupportedLanguage
        
        # 创建debug日志器
        debug_logger = get_i18n_logger("test-debug", SupportedLanguage.ZH_CN)
        
        print("📋 中文Debug日志测试:")
        debug_logger.debug_api_request_received("GET", "/api/test")
        debug_logger.debug_validation_start("symbol")
        debug_logger.debug_validation_passed("symbol")
        debug_logger.debug_cache_check_start("000858", "stock_info")
        debug_logger.debug_cache_check_result("hit", "000858")
        debug_logger.debug_data_source_select("tushare", "000858")
        debug_logger.debug_data_source_call("tushare", "http://api.tushare.pro/stock/info")
        debug_logger.debug_data_source_response("tushare", "success", 1024)
        debug_logger.debug_data_transform_start("raw_data", "formatted_data")
        debug_logger.debug_data_transform_end(100)
        debug_logger.debug_cache_save_start("000858", "stock_info")
        debug_logger.debug_cache_save_end("000858", 3600)
        debug_logger.debug_api_response_prepared(200)
        debug_logger.debug_api_response_sent(150)
        
        # 切换到英文
        print("\n📋 英文Debug日志测试:")
        debug_logger.set_language(SupportedLanguage.EN_US)
        debug_logger.debug_api_request_received("POST", "/api/data")
        debug_logger.debug_validation_start("date_range")
        debug_logger.debug_validation_failed("date_range", "invalid_format")
        debug_logger.debug_cache_check_start("AAPL", "stock_data")
        debug_logger.debug_cache_check_result("miss", "AAPL")
        debug_logger.debug_data_source_select("yfinance", "AAPL")
        debug_logger.debug_slow_query("SELECT * FROM stocks", 2500, 1000)
    
    def test_api_debug_logging(self):
        """测试API调用的debug日志"""
        print("\n🌐 测试API调用Debug日志")
        print("=" * 40)
        
        # 设置环境变量启用debug模式
        os.environ["DEBUG"] = "true"
        
        try:
            print("📥 调用股票信息API (应该产生详细debug日志)...")
            
            # 调用API
            response = requests.get(f"{self.data_service_url}/api/stock/info/000858")
            
            print(f"📤 API响应状态: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API调用成功: {data.get('message', 'N/A')}")
            else:
                print(f"❌ API调用失败: {response.text}")
            
            print("\n💡 提示: 查看控制台输出应该能看到详细的debug日志，包括:")
            print("   - 📥 API请求接收")
            print("   - 🔍 参数验证")
            print("   - 📦 缓存检查")
            print("   - 🎯 数据源选择")
            print("   - 📞 数据源调用")
            print("   - 🔄 数据转换")
            print("   - 💾 缓存保存")
            print("   - 📤 响应发送")
            
        except Exception as e:
            print(f"❌ API调用异常: {e}")
        finally:
            # 恢复环境变量
            os.environ.pop("DEBUG", None)
    
    def test_performance_debug_logging(self):
        """测试性能debug日志"""
        print("\n⚡ 测试性能Debug日志")
        print("=" * 40)
        
        from backend.shared.i18n.logger import get_i18n_logger
        from backend.shared.i18n.config import SupportedLanguage
        
        debug_logger = get_i18n_logger("perf-test", SupportedLanguage.ZH_CN)
        
        print("📊 性能监控日志测试:")
        
        # 模拟查询性能日志
        debug_logger.debug_query_start("stock_data_query", "000858")
        time.sleep(0.1)  # 模拟查询时间
        debug_logger.debug_query_end("stock_data_query", 100)
        
        # 模拟缓存性能日志
        debug_logger.debug_cache_performance(85.5, 25.3)
        
        # 模拟慢查询警告
        debug_logger.debug_slow_query("complex_analysis_query", 1500, 1000)
        
        # 模拟系统资源监控
        debug_logger.debug_memory_usage(512, 1024, 50.0)
        debug_logger.debug_cpu_usage(75.2)
        debug_logger.debug_connection_pool(8, 10)
    
    def test_error_debug_logging(self):
        """测试错误情况的debug日志"""
        print("\n❌ 测试错误Debug日志")
        print("=" * 40)
        
        try:
            print("📥 调用无效股票代码API (应该产生错误debug日志)...")
            
            response = requests.get(f"{self.data_service_url}/api/stock/info/INVALID_SYMBOL_123")
            
            print(f"📤 API响应状态: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ 预期的错误响应: {response.status_code}")
                data = response.json()
                print(f"错误消息: {data.get('message', 'N/A')}")
            
            print("\n💡 提示: 应该能看到错误相关的debug日志，包括:")
            print("   - 🔍 验证失败日志")
            print("   - ❌ 数据源响应错误")
            print("   - 📤 错误响应准备")
            
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    def test_middleware_debug_logging(self):
        """测试中间件debug日志"""
        print("\n🔄 测试中间件Debug日志")
        print("=" * 40)
        
        # 设置debug模式
        os.environ["DEBUG"] = "true"
        
        try:
            print("📥 调用API测试中间件debug日志...")
            
            # 带参数的API调用
            response = requests.get(
                f"{self.data_service_url}/api/stock/info/000858",
                params={"lang": "zh-CN", "format": "json"},
                headers={"User-Agent": "DebugTest/1.0", "Accept": "application/json"}
            )
            
            print(f"📤 响应状态: {response.status_code}")
            
            print("\n💡 提示: 应该能看到中间件相关的debug日志，包括:")
            print("   - 🔄 中间件开始/完成")
            print("   - 📋 请求参数记录")
            print("   - 📄 请求头记录")
            print("   - ⏱️ 处理时间统计")
            print("   - 🏥 性能监控")
            
        except Exception as e:
            print(f"❌ 中间件测试异常: {e}")
        finally:
            os.environ.pop("DEBUG", None)
    
    def test_language_switch_debug(self):
        """测试语言切换的debug日志"""
        print("\n🌍 测试语言切换Debug日志")
        print("=" * 40)
        
        try:
            # 设置为中文
            print("📋 设置日志语言为中文...")
            response = requests.post(
                f"{self.data_service_url}/api/i18n/set-log-language",
                json={"language": "zh-CN"}
            )
            if response.status_code == 200:
                print("✅ 中文日志语言设置成功")
            
            # 调用API查看中文debug日志
            print("📥 调用API (中文debug日志)...")
            requests.get(f"{self.data_service_url}/api/stock/info/000858")
            
            time.sleep(1)
            
            # 设置为英文
            print("\n📋 设置日志语言为英文...")
            response = requests.post(
                f"{self.data_service_url}/api/i18n/set-log-language",
                json={"language": "en-US"}
            )
            if response.status_code == 200:
                print("✅ 英文日志语言设置成功")
            
            # 调用API查看英文debug日志
            print("📥 调用API (英文debug日志)...")
            requests.get(f"{self.data_service_url}/api/stock/info/000858")
            
            print("\n💡 提示: 对比上面两次API调用的debug日志，应该能看到语言差异")
            
        except Exception as e:
            print(f"❌ 语言切换测试异常: {e}")
    
    def run_full_test(self):
        """运行完整的debug日志测试"""
        print("🐛 TradingAgents Debug日志功能测试")
        print("=" * 50)
        
        # 1. 健康检查
        if not self.test_service_health():
            print("❌ 服务不可用，请先启动 Data Service")
            return
        
        # 2. 测试基础debug日志
        self.test_debug_logging_basic()
        
        # 3. 测试API debug日志
        self.test_api_debug_logging()
        
        # 4. 测试性能debug日志
        self.test_performance_debug_logging()
        
        # 5. 测试错误debug日志
        self.test_error_debug_logging()
        
        # 6. 测试中间件debug日志
        self.test_middleware_debug_logging()
        
        # 7. 测试语言切换debug日志
        self.test_language_switch_debug()
        
        print("\n🎉 Debug日志功能测试完成！")
        print("\n💡 重要提示:")
        print("   - 要看到API的debug日志，需要设置环境变量 DEBUG=true")
        print("   - Debug日志默认只在DEBUG级别输出")
        print("   - 生产环境建议关闭debug日志以提高性能")
        print("   - 可以通过API动态切换日志语言")

def main():
    """主函数"""
    tester = DebugLoggingTester()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "basic":
            tester.test_debug_logging_basic()
        elif command == "api":
            tester.test_api_debug_logging()
        elif command == "performance":
            tester.test_performance_debug_logging()
        elif command == "error":
            tester.test_error_debug_logging()
        elif command == "middleware":
            tester.test_middleware_debug_logging()
        elif command == "language":
            tester.test_language_switch_debug()
        else:
            print("❌ 未知命令")
    else:
        tester.run_full_test()

if __name__ == "__main__":
    main()
