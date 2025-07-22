#!/usr/bin/env python3
"""
API密钥配置助手 - 帮助用户快速配置新的美股数据源
"""

import os
import sys
from pathlib import Path

class APIKeySetupHelper:
    """API密钥配置助手"""
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.env_file = self.backend_dir / ".env"
        self.env_example_file = self.backend_dir / ".env.example"
    
    def print_welcome(self):
        """打印欢迎信息"""
        print("🔑 TradingAgents 美股数据源API密钥配置助手")
        print("=" * 60)
        print("📊 我们将帮助您配置以下美股数据源的API密钥：")
        print("1. ✅ Alpha Vantage (推荐) - Yahoo Finance的优秀替代")
        print("2. ✅ Twelve Data (强烈推荐) - 访问稳定，支持全球市场")
        print("3. ✅ FinnHub - 现有的美股数据源")
        print()
    
    def check_existing_env(self):
        """检查现有的.env文件"""
        if self.env_file.exists():
            print("📄 发现现有的.env文件")
            
            # 读取现有配置
            with open(self.env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查已配置的API密钥
            existing_keys = {}
            for line in content.split('\n'):
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.split('=', 1)
                    if 'API_KEY' in key or 'TOKEN' in key:
                        existing_keys[key.strip()] = value.strip()
            
            if existing_keys:
                print("🔍 已配置的API密钥:")
                for key, value in existing_keys.items():
                    if value and value != f"your_{key.lower()}_here":
                        status = "✅ 已配置"
                        masked_value = f"{value[:8]}..." if len(value) > 8 else "***"
                    else:
                        status = "❌ 未配置"
                        masked_value = "未设置"
                    print(f"  {key}: {status} ({masked_value})")
            
            return True
        else:
            print("📄 未发现.env文件，将从.env.example创建")
            return False
    
    def create_env_from_example(self):
        """从.env.example创建.env文件"""
        if not self.env_example_file.exists():
            print("❌ 错误：未找到.env.example文件")
            return False
        
        try:
            # 复制.env.example到.env
            with open(self.env_example_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ 已从.env.example创建.env文件")
            return True
        except Exception as e:
            print(f"❌ 创建.env文件失败: {e}")
            return False
    
    def show_api_key_instructions(self):
        """显示API密钥获取说明"""
        print("\n🔗 API密钥获取指南")
        print("=" * 60)
        
        print("\n1. 📈 Alpha Vantage (完全免费，推荐)")
        print("   🌐 获取地址: https://www.alphavantage.co/support/#api-key")
        print("   📋 步骤:")
        print("      1) 访问上述网址")
        print("      2) 输入您的邮箱地址")
        print("      3) 点击 'GET FREE API KEY'")
        print("      4) 查收邮件获取API密钥")
        print("   ✨ 特点: 每天500次请求，每分钟5次，支持实时和历史数据")
        
        print("\n2. 🌟 Twelve Data (访问稳定，强烈推荐)")
        print("   🌐 获取地址: https://twelvedata.com/")
        print("   📋 步骤:")
        print("      1) 访问上述网址")
        print("      2) 点击 'Get free API key'")
        print("      3) 注册账户并验证邮箱")
        print("      4) 登录后在控制台获取API Key")
        print("   ✨ 特点: 每天800次请求，支持全球市场，访问稳定")


        
        print("\n3. 📊 FinnHub (现有数据源)")
        print("   🌐 获取地址: https://finnhub.io/")
        print("   📋 步骤:")
        print("      1) 访问上述网址并注册")
        print("      2) 在控制台获取API Key")
        print("   ✨ 特点: 免费版每分钟60次请求")
    
    def interactive_setup(self):
        """交互式配置"""
        print("\n⚙️ 交互式API密钥配置")
        print("=" * 60)
        
        # 读取当前.env文件
        if not self.env_file.exists():
            print("❌ .env文件不存在，请先运行创建步骤")
            return
        
        with open(self.env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 需要配置的API密钥
        api_keys = {
            'ALPHA_VANTAGE_API_KEY': {
                'name': 'Alpha Vantage',
                'description': '免费美股数据源，每天500次请求'
            },
            'TWELVE_DATA_API_KEY': {
                'name': 'Twelve Data',
                'description': '全球市场数据，每天800次请求，访问稳定'
            },
            'FINNHUB_API_KEY': {
                'name': 'FinnHub',
                'description': '美股数据源，每分钟60次请求'
            }
        }
        
        updated = False
        new_lines = []
        
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if key in api_keys:
                    info = api_keys[key]
                    current_value = value if value != f"your_{key.lower()}_here" else ""
                    
                    print(f"\n🔑 配置 {info['name']} API Key")
                    print(f"   📝 说明: {info['description']}")
                    
                    if current_value:
                        print(f"   📋 当前值: {current_value[:8]}...")
                        choice = input("   ❓ 是否更新？(y/N): ").strip().lower()
                        if choice not in ['y', 'yes']:
                            new_lines.append(line)
                            continue
                    
                    new_value = input(f"   🔤 请输入 {info['name']} API Key (回车跳过): ").strip()
                    
                    if new_value:
                        new_lines.append(f"{key}={new_value}\n")
                        updated = True
                        print(f"   ✅ {info['name']} API Key 已设置")
                    else:
                        new_lines.append(line)
                        print(f"   ⏭️ 跳过 {info['name']} API Key")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        # 保存更新的配置
        if updated:
            try:
                with open(self.env_file, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                print("\n✅ API密钥配置已保存到.env文件")
            except Exception as e:
                print(f"\n❌ 保存配置失败: {e}")
        else:
            print("\n📋 没有更新任何配置")
    
    def test_configuration(self):
        """测试配置"""
        print("\n🧪 测试API密钥配置")
        print("=" * 60)
        
        # 加载环境变量
        if self.env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(self.env_file)
        
        # 检查配置的API密钥
        api_keys = {
            'ALPHA_VANTAGE_API_KEY': 'Alpha Vantage',
            'TWELVE_DATA_API_KEY': 'Twelve Data',
            'FINNHUB_API_KEY': 'FinnHub'
        }
        
        configured_count = 0
        for key, name in api_keys.items():
            value = os.getenv(key)
            if value and value != f"your_{key.lower()}_here":
                print(f"✅ {name}: 已配置")
                configured_count += 1
            else:
                print(f"❌ {name}: 未配置")
        
        print(f"\n📊 配置状态: {configured_count}/{len(api_keys)} 个API密钥已配置")
        
        if configured_count > 0:
            print("\n🚀 建议运行测试脚本验证API密钥:")
            print("   python backend/test_new_us_data_sources.py")
        else:
            print("\n⚠️ 建议至少配置一个API密钥以获得更好的美股数据服务")
    
    def run_setup(self):
        """运行完整的配置流程"""
        self.print_welcome()
        
        # 检查现有配置
        has_env = self.check_existing_env()
        
        # 如果没有.env文件，创建一个
        if not has_env:
            if not self.create_env_from_example():
                return
        
        # 显示获取指南
        self.show_api_key_instructions()
        
        # 询问是否进行交互式配置
        print("\n" + "=" * 60)
        choice = input("❓ 是否现在进行交互式API密钥配置？(Y/n): ").strip().lower()
        
        if choice in ['', 'y', 'yes']:
            self.interactive_setup()
        else:
            print("📝 您可以手动编辑 backend/.env 文件来配置API密钥")
        
        # 测试配置
        self.test_configuration()
        
        print("\n🎉 API密钥配置助手完成！")
        print("💡 提示: 重启Data Service以使新配置生效")

def main():
    """主函数"""
    try:
        helper = APIKeySetupHelper()
        helper.run_setup()
    except KeyboardInterrupt:
        print("\n\n👋 配置已取消")
    except Exception as e:
        print(f"\n❌ 配置过程中出现错误: {e}")

if __name__ == "__main__":
    main()
