#!/usr/bin/env python3
"""
TradingAgents 安装验证脚本
检查系统环境和配置是否正确
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_check(item, status, details=""):
    """打印检查结果"""
    icon = "✅" if status else "❌"
    print(f"{icon} {item:30} {details}")

def check_command(command):
    """检查命令是否可用"""
    try:
        result = subprocess.run([command, "--version"], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout.strip().split('\n')[0]
    except:
        return False, "未安装"

def check_file(filepath):
    """检查文件是否存在"""
    return Path(filepath).exists()

def check_env_file():
    """检查环境变量配置"""
    if not check_file(".env"):
        return False, "文件不存在"
    
    required_keys = ["DASHSCOPE_API_KEY", "TUSHARE_TOKEN"]
    optional_keys = ["DEEPSEEK_API_KEY", "OPENAI_API_KEY"]
    
    try:
        with open(".env", "r") as f:
            content = f.read()
        
        configured_required = 0
        configured_optional = 0
        
        for key in required_keys:
            if f"{key}=" in content and "your_" not in content:
                configured_required += 1
        
        for key in optional_keys:
            if f"{key}=" in content and "your_" not in content:
                configured_optional += 1
        
        return True, f"必需: {configured_required}/{len(required_keys)}, 可选: {configured_optional}/{len(optional_keys)}"
    
    except Exception as e:
        return False, f"读取失败: {e}"

def main():
    """主函数"""
    print("🔍 TradingAgents 安装验证")
    print("检查系统环境和配置是否满足运行要求")
    
    # 检查基础环境
    print_header("基础环境检查")
    
    # Python版本
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    python_ok = sys.version_info >= (3, 10)
    print_check("Python版本", python_ok, f"v{python_version} {'(满足要求)' if python_ok else '(需要3.10+)'}")
    
    # Docker
    docker_ok, docker_info = check_command("docker")
    print_check("Docker", docker_ok, docker_info)
    
    # Docker Compose
    compose_ok, compose_info = check_command("docker-compose")
    print_check("Docker Compose", compose_ok, compose_info)
    
    # 检查项目文件
    print_header("项目文件检查")
    
    files_to_check = [
        ("docker-compose.yml", "主配置文件"),
        ("docker-compose.dev.yml", "开发配置文件"),
        (".env.example", "环境变量示例"),
        ("scripts/quick-start.sh", "Linux启动脚本"),
        ("scripts/quick-start.bat", "Windows启动脚本"),
        ("scripts/debug-tools.py", "调试工具"),
        ("GETTING_STARTED.md", "启动指南"),
        ("TROUBLESHOOTING.md", "故障排除指南")
    ]
    
    for filepath, description in files_to_check:
        exists = check_file(filepath)
        print_check(description, exists, filepath if exists else "文件缺失")
    
    # 检查环境配置
    print_header("环境配置检查")
    
    env_ok, env_details = check_env_file()
    print_check("环境变量配置", env_ok, env_details)
    
    # 检查服务目录
    print_header("服务目录检查")
    
    services = [
        "api-gateway",
        "analysis-engine", 
        "data-service",
        "task-scheduler",
        "shared"
    ]
    
    for service in services:
        service_ok = check_file(service)
        print_check(f"{service} 服务", service_ok, "目录存在" if service_ok else "目录缺失")
        
        if service_ok and service != "shared":
            dockerfile_ok = check_file(f"{service}/Dockerfile")
            requirements_ok = check_file(f"{service}/requirements.txt")
            print_check(f"  └─ Dockerfile", dockerfile_ok)
            print_check(f"  └─ requirements.txt", requirements_ok)
    
    # 检查脚本权限（Linux/Mac）
    if os.name != 'nt':  # 非Windows系统
        print_header("脚本权限检查")
        
        scripts = ["scripts/quick-start.sh", "scripts/start-dev.sh"]
        for script in scripts:
            if check_file(script):
                is_executable = os.access(script, os.X_OK)
                print_check(f"{script}", is_executable, 
                          "可执行" if is_executable else "需要执行: chmod +x " + script)
    
    # 生成总结
    print_header("验证总结")
    
    # 基础环境评分
    basic_score = sum([python_ok, docker_ok, compose_ok])
    basic_total = 3
    
    # 配置评分
    config_score = 1 if env_ok else 0
    config_total = 1
    
    # 文件评分
    file_score = sum([check_file(f[0]) for f in files_to_check])
    file_total = len(files_to_check)
    
    total_score = basic_score + config_score + file_score
    total_possible = basic_total + config_total + file_total
    
    print(f"📊 总体评分: {total_score}/{total_possible} ({total_score/total_possible*100:.1f}%)")
    
    if total_score == total_possible:
        print("🎉 恭喜！系统已准备就绪，可以启动 TradingAgents 后端系统")
        print("\n🚀 下一步操作:")
        if os.name == 'nt':  # Windows
            print("   运行: scripts\\quick-start.bat")
        else:  # Linux/Mac
            print("   运行: ./scripts/quick-start.sh")
        print("   或者: docker-compose up -d")
    
    elif total_score >= total_possible * 0.8:
        print("⚠️ 系统基本就绪，但有一些配置需要完善")
        print("\n🔧 建议操作:")
        if not env_ok:
            print("   1. 配置 .env 文件中的API密钥")
        print("   2. 检查缺失的文件或目录")
        print("   3. 完成配置后重新运行验证")
    
    else:
        print("❌ 系统环境不满足要求，请先完成基础环境配置")
        print("\n📋 必需操作:")
        if not python_ok:
            print("   1. 安装 Python 3.10 或更高版本")
        if not docker_ok:
            print("   2. 安装 Docker Desktop")
        if not compose_ok:
            print("   3. 安装 Docker Compose")
        print("   4. 确保所有必需文件存在")
    
    print(f"\n📚 详细文档: GETTING_STARTED.md")
    print(f"🔧 故障排除: TROUBLESHOOTING.md")

if __name__ == "__main__":
    main()
