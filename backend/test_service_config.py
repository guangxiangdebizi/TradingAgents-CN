#!/usr/bin/env python3
"""
测试服务配置
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.shared.utils.config import get_config

def test_service_config():
    """测试服务配置"""
    print("🔧 测试服务配置...")
    
    config = get_config()
    
    services = [
        "analysis-engine",
        "data-service", 
        "llm-service",
        "agent-service"
    ]
    
    print("\n📋 环境变量检查:")
    for service in services:
        host_key = f"{service.upper()}_HOST"
        port_key = f"{service.upper()}_PORT"
        
        host = config.get(host_key)
        port = config.get(port_key)
        
        print(f"  {service}:")
        print(f"    {host_key}: {host}")
        print(f"    {port_key}: {port}")
    
    print("\n🌐 服务URL:")
    for service in services:
        url = config.get_service_url(service)
        print(f"  {service}: {url}")

if __name__ == "__main__":
    test_service_config()
