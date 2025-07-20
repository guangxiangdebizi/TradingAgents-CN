#!/usr/bin/env python3
"""
TradingAgents 调试工具
提供系统诊断、日志分析、性能测试等功能
"""

import asyncio
import json
import time
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import httpx
import argparse

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class DebugTools:
    """调试工具类"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.services = {
            "api-gateway": "http://localhost:8000",
            "analysis-engine": "http://localhost:8001", 
            "data-service": "http://localhost:8002",
            "task-api": "http://localhost:8003",
            "flower": "http://localhost:5555"
        }
    
    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print(f"{'='*60}")
    
    def print_section(self, title: str):
        """打印章节"""
        print(f"\n📋 {title}")
        print("-" * 40)
    
    async def check_services_health(self):
        """检查所有服务健康状态"""
        self.print_header("服务健康检查")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for service_name, url in self.services.items():
                try:
                    health_url = f"{url}/health" if service_name != "flower" else url
                    response = await client.get(health_url)
                    
                    if response.status_code == 200:
                        print(f"✅ {service_name:15} - 健康")
                        if service_name != "flower":
                            data = response.json()
                            if "dependencies" in data:
                                for dep, status in data["dependencies"].items():
                                    status_icon = "✅" if status == "healthy" else "❌"
                                    print(f"   └─ {dep:12} - {status_icon} {status}")
                    else:
                        print(f"❌ {service_name:15} - HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ {service_name:15} - 连接失败: {str(e)[:50]}")
    
    async def test_api_endpoints(self):
        """测试API接口"""
        self.print_header("API接口测试")
        
        test_cases = [
            {
                "name": "健康检查",
                "method": "GET",
                "url": "/health",
                "expected_status": 200
            },
            {
                "name": "系统状态",
                "method": "GET", 
                "url": "/api/config/status",
                "expected_status": 200
            },
            {
                "name": "模型配置",
                "method": "GET",
                "url": "/api/config/models", 
                "expected_status": 200
            },
            {
                "name": "股票信息",
                "method": "GET",
                "url": "/api/stock/info/000858",
                "expected_status": 200
            }
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for test in test_cases:
                try:
                    url = f"{self.base_url}{test['url']}"
                    
                    if test["method"] == "GET":
                        response = await client.get(url)
                    elif test["method"] == "POST":
                        response = await client.post(url, json=test.get("data", {}))
                    
                    if response.status_code == test["expected_status"]:
                        print(f"✅ {test['name']:15} - 通过")
                    else:
                        print(f"❌ {test['name']:15} - HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ {test['name']:15} - 失败: {str(e)[:50]}")
    
    def check_docker_status(self):
        """检查Docker状态"""
        self.print_header("Docker状态检查")
        
        try:
            # 检查Docker是否运行
            result = subprocess.run(
                ["docker", "info"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ Docker 运行正常")
            else:
                print("❌ Docker 未运行")
                return
                
        except Exception as e:
            print(f"❌ Docker 检查失败: {e}")
            return
        
        # 检查容器状态
        try:
            result = subprocess.run(
                ["docker-compose", "ps"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("\n📊 容器状态:")
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # 跳过标题行
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            container_name = parts[0]
                            status = " ".join(parts[1:])
                            status_icon = "✅" if "Up" in status else "❌"
                            print(f"  {status_icon} {container_name:25} - {status}")
            else:
                print("❌ 无法获取容器状态")
                
        except Exception as e:
            print(f"❌ 容器状态检查失败: {e}")
    
    def check_ports(self):
        """检查端口占用"""
        self.print_header("端口占用检查")
        
        ports = [8000, 8001, 8002, 8003, 5555, 27017, 6379, 9000, 9001]
        
        for port in ports:
            try:
                result = subprocess.run(
                    ["netstat", "-an"], 
                    capture_output=True, 
                    text=True,
                    timeout=5
                )
                
                if f":{port}" in result.stdout:
                    print(f"✅ 端口 {port:5} - 已占用")
                else:
                    print(f"❌ 端口 {port:5} - 未占用")
                    
            except Exception:
                # Windows 系统使用不同的命令
                try:
                    result = subprocess.run(
                        ["netstat", "-an"], 
                        capture_output=True, 
                        text=True,
                        timeout=5,
                        shell=True
                    )
                    
                    if f":{port}" in result.stdout:
                        print(f"✅ 端口 {port:5} - 已占用")
                    else:
                        print(f"❌ 端口 {port:5} - 未占用")
                        
                except Exception as e:
                    print(f"⚠️ 端口 {port:5} - 检查失败: {e}")
    
    def show_logs(self, service: str = None, lines: int = 50):
        """显示服务日志"""
        self.print_header(f"服务日志 - {service or '所有服务'}")
        
        try:
            cmd = ["docker-compose", "logs", "--tail", str(lines)]
            if service:
                cmd.append(service)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"❌ 获取日志失败: {result.stderr}")
                
        except Exception as e:
            print(f"❌ 日志获取失败: {e}")
    
    async def performance_test(self):
        """性能测试"""
        self.print_header("性能测试")
        
        # 测试API响应时间
        self.print_section("API响应时间测试")
        
        test_urls = [
            "/health",
            "/api/config/status",
            "/api/stock/info/000858"
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for url in test_urls:
                times = []
                
                for i in range(5):
                    start_time = time.time()
                    try:
                        response = await client.get(f"{self.base_url}{url}")
                        end_time = time.time()
                        
                        if response.status_code == 200:
                            times.append((end_time - start_time) * 1000)
                        
                    except Exception:
                        pass
                
                if times:
                    avg_time = sum(times) / len(times)
                    min_time = min(times)
                    max_time = max(times)
                    
                    print(f"📊 {url:25} - 平均: {avg_time:.1f}ms, 最小: {min_time:.1f}ms, 最大: {max_time:.1f}ms")
                else:
                    print(f"❌ {url:25} - 测试失败")
    
    def system_info(self):
        """显示系统信息"""
        self.print_header("系统信息")
        
        # Python版本
        print(f"🐍 Python版本: {sys.version}")
        
        # 操作系统
        import platform
        print(f"💻 操作系统: {platform.system()} {platform.release()}")
        
        # Docker版本
        try:
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"🐳 Docker版本: {result.stdout.strip()}")
        except Exception:
            print("🐳 Docker版本: 未安装或无法检测")
        
        # Docker Compose版本
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"📦 Docker Compose版本: {result.stdout.strip()}")
        except Exception:
            print("📦 Docker Compose版本: 未安装或无法检测")
    
    async def run_full_diagnosis(self):
        """运行完整诊断"""
        print("🔍 TradingAgents 系统诊断工具")
        print(f"⏰ 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 系统信息
        self.system_info()
        
        # Docker状态
        self.check_docker_status()
        
        # 端口检查
        self.check_ports()
        
        # 服务健康检查
        await self.check_services_health()
        
        # API测试
        await self.test_api_endpoints()
        
        # 性能测试
        await self.performance_test()
        
        print(f"\n🎉 诊断完成！")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="TradingAgents 调试工具")
    parser.add_argument("--action", choices=[
        "health", "api", "docker", "ports", "logs", "perf", "full"
    ], default="full", help="执行的操作")
    parser.add_argument("--service", help="指定服务名称（用于日志查看）")
    parser.add_argument("--lines", type=int, default=50, help="日志行数")
    
    args = parser.parse_args()
    
    debug_tools = DebugTools()
    
    if args.action == "health":
        await debug_tools.check_services_health()
    elif args.action == "api":
        await debug_tools.test_api_endpoints()
    elif args.action == "docker":
        debug_tools.check_docker_status()
    elif args.action == "ports":
        debug_tools.check_ports()
    elif args.action == "logs":
        debug_tools.show_logs(args.service, args.lines)
    elif args.action == "perf":
        await debug_tools.performance_test()
    elif args.action == "full":
        await debug_tools.run_full_diagnosis()


if __name__ == "__main__":
    asyncio.run(main())
