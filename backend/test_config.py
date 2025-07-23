#!/usr/bin/env python3
"""
测试配置加载
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.shared.utils.config import get_config
from backend.shared.clients.data_client import DataClient
from backend.shared.clients.llm_client import LLMClient

def test_config():
    """测试配置加载"""
    print("🔧 测试配置加载...")
    
    config = get_config()
    
    print("\n📋 环境变量:")
    print(f"  DATA-SERVICE_HOST: {config.get('DATA-SERVICE_HOST')}")
    print(f"  DATA-SERVICE_PORT: {config.get('DATA-SERVICE_PORT')}")
    print(f"  LLM-SERVICE_HOST: {config.get('LLM-SERVICE_HOST')}")
    print(f"  LLM-SERVICE_PORT: {config.get('LLM-SERVICE_PORT')}")
    
    print("\n🌐 服务URL:")
    print(f"  data-service: {config.get_service_url('data-service')}")
    print(f"  llm-service: {config.get_service_url('llm-service')}")
    
    print("\n📡 客户端配置:")
    data_client = DataClient()
    llm_client = LLMClient()
    
    print(f"  DataClient base_url: {data_client.base_url}")
    print(f"  LLMClient base_url: {llm_client.base_url}")

if __name__ == "__main__":
    test_config()
