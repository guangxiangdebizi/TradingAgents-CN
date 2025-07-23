#!/usr/bin/env python3
"""
Backend微服务状态检查脚本
"""

import requests
import time
from typing import List, Tuple


def check_service_health(name: str, url: str, timeout: int = 5) -> Tuple[str, bool, str]:
    """
    检查单个服务的健康状态
    
    Returns:
        (service_name, is_healthy, status_message)
    """
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return name, True, "✅ 正常运行"
        else:
            return name, False, f"❌ HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return name, False, "❌ 连接失败"
    except requests.exceptions.Timeout:
        return name, False, "❌ 连接超时"
    except Exception as e:
        return name, False, f"❌ 错误: {str(e)[:50]}"


def check_all_services():
    """检查所有Backend微服务状态"""
    
    services = [
        ("Data Service", "http://localhost:8002/health"),
        ("Analysis Engine", "http://localhost:8001/health"),
        ("LLM Service", "http://localhost:8004/health"),
        ("Memory Service", "http://localhost:8006/health"),
        ("Agent Service", "http://localhost:8008/health"),
        ("API Gateway", "http://localhost:8000/health")
    ]
    
    print("🔍 Backend微服务状态检查")
    print("=" * 50)
    
    healthy_count = 0
    total_count = len(services)
    
    for name, url in services:
        service_name, is_healthy, status = check_service_health(name, url)
        print(f"{service_name:15} | {status}")
        
        if is_healthy:
            healthy_count += 1
    
    print("=" * 50)
    print(f"状态总结: {healthy_count}/{total_count} 服务正常运行")
    
    if healthy_count == total_count:
        print("🎉 所有服务运行正常！")
    elif healthy_count == 0:
        print("⚠️ 所有服务都未启动，请按照启动指引启动服务")
    else:
        print("⚠️ 部分服务未启动，请检查未运行的服务")
    
    return healthy_count, total_count


def check_dependencies():
    """检查外部依赖（数据库等）"""
    print("\n🗄️ 外部依赖检查")
    print("=" * 50)
    
    dependencies = [
        ("MongoDB", "mongodb://localhost:27017"),
        ("Redis", "redis://localhost:6379")
    ]
    
    # 简单的端口检查
    import socket
    
    for name, url in dependencies:
        try:
            if "mongodb" in url:
                host, port = "localhost", 27017
            elif "redis" in url:
                host, port = "localhost", 6379
            else:
                continue
                
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"{name:15} | ✅ 端口 {port} 可访问")
            else:
                print(f"{name:15} | ❌ 端口 {port} 不可访问")
                
        except Exception as e:
            print(f"{name:15} | ❌ 检查失败: {str(e)[:30]}")


def main():
    """主函数"""
    print("Backend微服务状态检查工具")
    print("时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # 检查外部依赖
    check_dependencies()
    
    # 检查微服务
    healthy_count, total_count = check_all_services()
    
    # 给出建议
    print("\n💡 建议:")
    if healthy_count == 0:
        print("1. 请先启动MongoDB和Redis服务")
        print("2. 按照 README_STARTUP.md 中的顺序启动微服务")
        print("3. 从Data Service开始，逐个启动服务")
    elif healthy_count < total_count:
        print("1. 检查未启动的服务日志")
        print("2. 确认端口没有被占用")
        print("3. 检查 .backend_env 配置文件")
    else:
        print("1. 所有服务运行正常，可以开始开发或测试")
        print("2. 可以访问 http://localhost:8000 使用API网关")


if __name__ == "__main__":
    main()
