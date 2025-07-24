#!/usr/bin/env python3
"""
Backend Trading CLI Client 安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Backend Trading CLI Client"

# 读取requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="trading-cli",
    version="1.0.0",
    description="Backend Trading CLI Client - 类似TradingAgents的命令行客户端",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Backend Team",
    author_email="backend@tradingagents.cn",
    url="https://github.com/your-org/backend-trading-cli",
    
    packages=find_packages(),
    py_modules=["trading_cli", "config"],

    install_requires=read_requirements(),

    entry_points={
        "console_scripts": [
            "trading-cli=app.main:cli_main",
            "tcli=app.main:cli_main",
            "tradingagents=app.main:cli_main",
        ],
    },

    include_package_data=True,
    package_data={
        "app": ["*.txt"],
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    python_requires=">=3.8",
    
    keywords="trading, stock analysis, cli, backend, microservices",
    
    project_urls={
        "Bug Reports": "https://github.com/your-org/backend-trading-cli/issues",
        "Source": "https://github.com/your-org/backend-trading-cli",
        "Documentation": "https://docs.tradingagents.cn/cli/",
    },
)
