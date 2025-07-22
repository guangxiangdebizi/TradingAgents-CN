#!/usr/bin/env python3
"""
国际化日志功能测试脚本
"""

import sys
import requests
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class I18nLoggingTester:
    """国际化日志测试器"""
    
    def __init__(self):
        self.data_service_url = "http://localhost:8002"
    
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
    
    def test_basic_i18n_logging(self):
        """测试基础国际化日志功能"""
        print("\n🌍 测试基础国际化日志功能")
        print("=" * 40)
        
        from backend.shared.i18n.logger import get_i18n_logger
        from backend.shared.i18n.config import SupportedLanguage
        
        # 测试中文日志
        print("📋 中文日志测试:")
        logger_zh = get_i18n_logger("test-zh", SupportedLanguage.ZH_CN)
        logger_zh.startup()
        logger_zh.database_connected()
        logger_zh.cache_hit("000858", "stock_info")
        logger_zh.data_fetched("000858", "tushare")
        logger_zh.data_saved("000858", "stock_info")
        
        # 测试英文日志
        print("\n📋 英文日志测试:")
        logger_en = get_i18n_logger("test-en", SupportedLanguage.EN_US)
        logger_en.startup()
        logger_en.database_connected()
        logger_en.cache_hit("000858", "stock_info")
        logger_en.data_fetched("000858", "tushare")
        logger_en.data_saved("000858", "stock_info")
        
        # 测试日文日志
        print("\n📋 日文日志测试:")
        logger_ja = get_i18n_logger("test-ja", SupportedLanguage.JA_JP)
        logger_ja.startup()
        logger_ja.database_connected()
        logger_ja.cache_hit("000858", "stock_info")
        logger_ja.data_fetched("000858", "tushare")
        logger_ja.data_saved("000858", "stock_info")
    
    def test_set_log_language_api(self, language: str):
        """测试设置日志语言API"""
        print(f"\n🔧 测试设置日志语言API: {language}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{self.data_service_url}/api/i18n/set-log-language",
                json={"language": language}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    lang_info = data.get("data", {})
                    print(f"✅ 日志语言设置成功: {lang_info.get('language')}")
                    print(f"   响应消息: {data.get('message', 'N/A')}")
                    return True
                else:
                    print(f"❌ 设置日志语言失败: {data.get('message', 'N/A')}")
                    return False
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def test_logging_with_api_calls(self, language: str):
        """测试API调用时的日志语言"""
        print(f"\n📊 测试 {language} 语言下的API调用日志")
        print("-" * 40)
        
        try:
            # 1. 设置日志语言
            self.test_set_log_language_api(language)
            
            # 2. 等待一下让设置生效
            time.sleep(1)
            
            # 3. 调用一些API来触发日志
            print("  📥 调用股票信息API...")
            response = requests.get(f"{self.data_service_url}/api/stock/info/000858")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ API调用成功: {data.get('message', 'N/A')}")
            
            print("  📥 调用强制刷新API...")
            response = requests.post(
                f"{self.data_service_url}/api/local-data/force-refresh",
                json={"symbol": "000858", "data_type": "stock_info"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ 强制刷新成功: {data.get('message', 'N/A')}")
            
            print("  📥 调用数据摘要API...")
            response = requests.get(f"{self.data_service_url}/api/local-data/summary")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ 数据摘要成功: {data.get('message', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def test_error_logging(self, language: str):
        """测试错误日志的国际化"""
        print(f"\n❌ 测试 {language} 语言下的错误日志")
        print("-" * 40)
        
        try:
            # 设置日志语言
            self.test_set_log_language_api(language)
            time.sleep(1)
            
            # 调用一个会产生错误的API
            print("  📥 调用无效股票代码API...")
            response = requests.get(f"{self.data_service_url}/api/stock/info/INVALID_SYMBOL")
            print(f"  📤 响应状态: {response.status_code}")
            
            if response.status_code != 200:
                data = response.json()
                print(f"  ❌ 错误消息: {data.get('message', 'N/A')}")
            
            return True
            
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def test_compatible_logging(self):
        """测试兼容模式日志"""
        print("\n🔄 测试兼容模式日志")
        print("=" * 40)
        
        from backend.shared.i18n.logger import get_compatible_logger
        from backend.shared.i18n.config import SupportedLanguage
        
        # 测试兼容模式（类似传统日志）
        print("📋 兼容模式日志测试:")
        compat_logger = get_compatible_logger("test-compat", SupportedLanguage.ZH_CN)
        compat_logger.info("这是一条兼容模式的信息日志")
        compat_logger.warning("这是一条兼容模式的警告日志")
        compat_logger.error("这是一条兼容模式的错误日志")
        
        # 测试参数格式化
        compat_logger.info("股票 %s 的价格是 %.2f", "000858", 123.45)
        compat_logger.info("处理了 {count} 条记录", count=100)
    
    def test_log_performance(self):
        """测试日志性能"""
        print("\n⚡ 测试日志性能")
        print("=" * 40)
        
        from backend.shared.i18n.logger import get_i18n_logger
        from backend.shared.i18n.config import SupportedLanguage
        
        logger = get_i18n_logger("test-perf", SupportedLanguage.ZH_CN)
        
        # 测试大量日志输出的性能
        start_time = time.time()
        for i in range(1000):
            logger.cache_hit(f"symbol_{i}", "stock_info")
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        print(f"✅ 1000条国际化日志耗时: {duration:.2f}ms")
        print(f"   平均每条日志: {duration/1000:.3f}ms")
    
    def run_full_test(self):
        """运行完整的国际化日志测试"""
        print("🧪 TradingAgents 国际化日志功能测试")
        print("=" * 50)
        
        # 1. 健康检查
        if not self.test_service_health():
            print("❌ 服务不可用，请先启动 Data Service")
            return
        
        # 2. 测试基础日志功能
        self.test_basic_i18n_logging()
        
        # 3. 测试API设置日志语言
        languages_to_test = ["zh-CN", "en-US", "ja-JP"]
        for lang in languages_to_test:
            self.test_logging_with_api_calls(lang)
        
        # 4. 测试错误日志
        for lang in ["zh-CN", "en-US"]:
            self.test_error_logging(lang)
        
        # 5. 测试兼容模式
        self.test_compatible_logging()
        
        # 6. 测试性能
        self.test_log_performance()
        
        print("\n🎉 国际化日志功能测试完成！")
        print("\n💡 提示:")
        print("   - 查看控制台输出可以看到不同语言的日志消息")
        print("   - 日志会根据设置的语言自动翻译")
        print("   - 支持中文、英文、日文等多种语言")

def main():
    """主函数"""
    tester = I18nLoggingTester()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "basic":
            tester.test_basic_i18n_logging()
        elif command == "api":
            lang = sys.argv[2] if len(sys.argv) > 2 else "zh-CN"
            tester.test_logging_with_api_calls(lang)
        elif command == "error":
            lang = sys.argv[2] if len(sys.argv) > 2 else "zh-CN"
            tester.test_error_logging(lang)
        elif command == "compat":
            tester.test_compatible_logging()
        elif command == "perf":
            tester.test_log_performance()
        else:
            print("❌ 未知命令")
    else:
        tester.run_full_test()

if __name__ == "__main__":
    main()
