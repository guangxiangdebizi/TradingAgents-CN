#!/usr/bin/env python3
"""
安装CLI客户端依赖
"""

import subprocess
import sys
from pathlib import Path

def install_package(package):
    """安装单个包"""
    try:
        print(f"安装 {package}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package
        ], capture_output=True, text=True, check=True)
        print(f"✅ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 安装失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 TradingAgents CLI 依赖安装")
    print("=" * 40)
    
    # 核心依赖包
    core_packages = [
        "rich>=13.0.0",
        "typer>=0.9.0", 
        "aiohttp>=3.8.0",
        "loguru>=0.7.0"
    ]
    
    # 可选依赖包
    optional_packages = [
        "tabulate>=0.9.0",
        "tqdm>=4.65.0",
        "python-dateutil>=2.8.0"
    ]
    
    print("安装核心依赖...")
    core_success = 0
    for package in core_packages:
        if install_package(package):
            core_success += 1
    
    print(f"\n核心依赖安装结果: {core_success}/{len(core_packages)}")
    
    if core_success == len(core_packages):
        print("✅ 核心依赖安装完成!")
        
        # 安装可选依赖
        print("\n安装可选依赖...")
        optional_success = 0
        for package in optional_packages:
            if install_package(package):
                optional_success += 1
        
        print(f"\n可选依赖安装结果: {optional_success}/{len(optional_packages)}")
        
        print("\n🎉 依赖安装完成!")
        print("现在可以运行: python -m app")
        
    else:
        print("❌ 核心依赖安装失败，请手动安装:")
        for package in core_packages:
            print(f"  pip install {package}")
    
    # 尝试从requirements.txt安装
    req_file = Path("requirements.txt")
    if req_file.exists():
        print(f"\n发现 {req_file}，尝试安装...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(req_file)
            ], capture_output=True, text=True, check=True)
            print("✅ requirements.txt 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ requirements.txt 安装失败: {e}")

if __name__ == "__main__":
    main()
