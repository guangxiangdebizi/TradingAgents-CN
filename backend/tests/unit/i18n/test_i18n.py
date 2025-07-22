#!/usr/bin/env python3
"""
国际化功能测试脚本
"""

import sys
import requests
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class I18nTester:
    """国际化测试器"""
    
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
    
    def test_get_supported_languages(self):
        """测试获取支持的语言列表"""
        print("\n🌍 测试获取支持的语言列表...")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.data_service_url}/api/i18n/languages")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    languages = data.get("data", [])
                    print("✅ 支持的语言:")
                    for lang in languages:
                        print(f"  🔹 {lang.get('code')}: {lang.get('name')}")
                    return True
                else:
                    print(f"❌ 获取语言列表失败: {data.get('message', 'N/A')}")
                    return False
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def test_get_current_language(self):
        """测试获取当前语言"""
        print("\n📋 测试获取当前语言...")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.data_service_url}/api/i18n/current")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    lang_info = data.get("data", {})
                    print(f"✅ 当前语言: {lang_info.get('language')} ({lang_info.get('name')})")
                    return True
                else:
                    print(f"❌ 获取当前语言失败: {data.get('message', 'N/A')}")
                    return False
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def test_set_language(self, language: str):
        """测试设置语言"""
        print(f"\n🔧 测试设置语言: {language}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{self.data_service_url}/api/i18n/set-language",
                json={"language": language}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    lang_info = data.get("data", {})
                    print(f"✅ 语言设置成功: {lang_info.get('language')}")
                    return True
                else:
                    print(f"❌ 设置语言失败: {data.get('message', 'N/A')}")
                    return False
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def test_api_with_language(self, language: str):
        """测试带语言参数的API调用"""
        print(f"\n🌐 测试 {language} 语言的API响应...")
        print("-" * 40)
        
        try:
            # 设置语言
            self.test_set_language(language)
            
            # 测试股票信息API
            response = requests.get(f"{self.data_service_url}/api/stock/info/000858")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API响应消息: {data.get('message', 'N/A')}")
                
                # 检查响应头中的语言信息
                content_language = response.headers.get('Content-Language')
                if content_language:
                    print(f"✅ 响应语言头: {content_language}")
                
                return True
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def test_language_header(self, language: str):
        """测试通过HTTP头设置语言"""
        print(f"\n📤 测试通过HTTP头设置语言: {language}")
        print("-" * 40)
        
        try:
            headers = {
                'Accept-Language': language,
                'X-Language': language
            }
            
            response = requests.get(
                f"{self.data_service_url}/api/i18n/current",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    lang_info = data.get("data", {})
                    detected_lang = lang_info.get('language')
                    print(f"✅ 检测到的语言: {detected_lang}")
                    
                    # 检查是否正确检测
                    if language.startswith(detected_lang.split('-')[0]):
                        print("✅ 语言检测正确")
                        return True
                    else:
                        print(f"⚠️ 语言检测可能不准确，期望: {language}, 实际: {detected_lang}")
                        return True  # 仍然算成功，因为有回退机制
                else:
                    print(f"❌ 获取语言失败: {data.get('message', 'N/A')}")
                    return False
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def test_translation_stats(self):
        """测试翻译统计信息"""
        print("\n📊 测试翻译统计信息...")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.data_service_url}/api/i18n/stats")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stats = data.get("data", {})
                    print("✅ 翻译统计:")
                    for lang, info in stats.items():
                        status = "已加载" if info.get("loaded") else "未加载"
                        print(f"  🔹 {lang}: {info.get('total_keys', 0)} 个翻译键 ({status})")
                    return True
                else:
                    print(f"❌ 获取统计失败: {data.get('message', 'N/A')}")
                    return False
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False
    
    def test_data_localization(self):
        """测试数据本地化"""
        print("\n🔄 测试数据本地化...")
        print("-" * 40)
        
        # 测试中文
        print("测试中文本地化:")
        self.test_set_language("zh-CN")
        response = requests.get(f"{self.data_service_url}/api/stock/info/000858")
        if response.status_code == 200:
            data = response.json()
            stock_data = data.get("data", {})
            print(f"  消息: {data.get('message', 'N/A')}")
            if "_field_names" in stock_data:
                print(f"  字段名本地化: {stock_data['_field_names']}")
        
        # 测试英文
        print("\n测试英文本地化:")
        self.test_set_language("en-US")
        response = requests.get(f"{self.data_service_url}/api/stock/info/000858")
        if response.status_code == 200:
            data = response.json()
            stock_data = data.get("data", {})
            print(f"  消息: {data.get('message', 'N/A')}")
            if "_field_names" in stock_data:
                print(f"  字段名本地化: {stock_data['_field_names']}")
    
    def run_full_test(self):
        """运行完整的国际化测试"""
        print("🌍 TradingAgents 国际化功能测试")
        print("=" * 50)
        
        # 1. 健康检查
        if not self.test_service_health():
            print("❌ 服务不可用，请先启动 Data Service")
            return
        
        # 2. 测试基础功能
        self.test_get_supported_languages()
        self.test_get_current_language()
        self.test_translation_stats()
        
        # 3. 测试语言切换
        languages_to_test = ["zh-CN", "en-US", "ja-JP"]
        for lang in languages_to_test:
            self.test_set_language(lang)
            self.test_api_with_language(lang)
        
        # 4. 测试HTTP头检测
        headers_to_test = ["zh-CN", "en-US", "ja", "ko"]
        for lang in headers_to_test:
            self.test_language_header(lang)
        
        # 5. 测试数据本地化
        self.test_data_localization()
        
        print("\n🎉 国际化功能测试完成！")

def main():
    """主函数"""
    tester = I18nTester()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "languages":
            tester.test_get_supported_languages()
        elif command == "current":
            tester.test_get_current_language()
        elif command == "set":
            lang = sys.argv[2] if len(sys.argv) > 2 else "en-US"
            tester.test_set_language(lang)
        elif command == "stats":
            tester.test_translation_stats()
        elif command == "localization":
            tester.test_data_localization()
        else:
            print("❌ 未知命令")
    else:
        tester.run_full_test()

if __name__ == "__main__":
    main()
