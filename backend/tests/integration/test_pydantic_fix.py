#!/usr/bin/env python3
"""
测试 Pydantic 命名空间冲突修复
"""

import sys
import warnings
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_pydantic_models():
    """测试 Pydantic 模型是否有命名空间冲突"""
    print("🧪 测试 Pydantic 模型命名空间冲突修复")
    print("=" * 50)
    
    # 捕获警告
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        try:
            # 导入可能有问题的模型
            from backend.shared.models.analysis import (
                AnalysisRequest, AnalysisProgress, AnalysisResult, 
                ExportRequest, APIResponse, HealthCheck
            )
            
            print("✅ 成功导入所有分析模型")
            
            # 测试创建模型实例
            analysis_request = AnalysisRequest(
                stock_code="000858",
                model_version="test-version"  # 这个字段之前会引起警告
            )
            
            print(f"✅ 成功创建 AnalysisRequest 实例")
            print(f"   股票代码: {analysis_request.stock_code}")
            print(f"   模型版本: {analysis_request.model_version}")
            
            # 检查是否有警告
            pydantic_warnings = [warning for warning in w 
                               if "model_" in str(warning.message) and "protected namespace" in str(warning.message)]
            
            if pydantic_warnings:
                print(f"\n⚠️ 仍有 {len(pydantic_warnings)} 个 Pydantic 警告:")
                for warning in pydantic_warnings:
                    print(f"   {warning.message}")
                    print(f"   文件: {warning.filename}:{warning.lineno}")
                return False
            else:
                print("\n✅ 没有 Pydantic 命名空间冲突警告")
                return True
                
        except Exception as e:
            print(f"❌ 导入模型失败: {e}")
            return False

def test_other_models():
    """测试其他可能的模型"""
    print("\n🔍 测试其他数据模型")
    print("-" * 30)
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        try:
            from backend.shared.models.data import (
                StockDataRequest, StockInfo, StockPrice, 
                MarketData, NewsItem, FundamentalData
            )
            
            print("✅ 成功导入所有数据模型")
            
            # 检查警告
            pydantic_warnings = [warning for warning in w 
                               if "model_" in str(warning.message) and "protected namespace" in str(warning.message)]
            
            if pydantic_warnings:
                print(f"⚠️ 数据模型有 {len(pydantic_warnings)} 个警告")
                return False
            else:
                print("✅ 数据模型没有命名空间冲突")
                return True
                
        except Exception as e:
            print(f"❌ 导入数据模型失败: {e}")
            return False

def test_fastapi_startup():
    """测试 FastAPI 启动时的警告"""
    print("\n🚀 测试 FastAPI 应用启动")
    print("-" * 30)
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        try:
            # 模拟导入 FastAPI 应用
            from fastapi import FastAPI
            from backend.shared.models.analysis import APIResponse
            
            app = FastAPI()
            
            @app.get("/test", response_model=APIResponse)
            async def test_endpoint():
                return APIResponse(success=True, message="测试")
            
            print("✅ 成功创建 FastAPI 应用和路由")
            
            # 检查警告
            pydantic_warnings = [warning for warning in w 
                               if "model_" in str(warning.message) and "protected namespace" in str(warning.message)]
            
            if pydantic_warnings:
                print(f"⚠️ FastAPI 启动有 {len(pydantic_warnings)} 个警告")
                for warning in pydantic_warnings:
                    print(f"   {warning.message}")
                return False
            else:
                print("✅ FastAPI 启动没有命名空间冲突警告")
                return True
                
        except Exception as e:
            print(f"❌ FastAPI 测试失败: {e}")
            return False

def show_pydantic_info():
    """显示 Pydantic 版本信息"""
    print("\n📋 Pydantic 环境信息")
    print("-" * 30)
    
    try:
        import pydantic
        print(f"Pydantic 版本: {pydantic.VERSION}")
        
        # 检查是否是 v2
        if hasattr(pydantic, 'BaseModel'):
            model = pydantic.BaseModel
            if hasattr(model, 'model_config'):
                print("✅ 使用 Pydantic v2")
            else:
                print("⚠️ 使用 Pydantic v1")
        
        # 显示保护命名空间的默认设置
        try:
            from pydantic import ConfigDict
            print("✅ 支持 ConfigDict (Pydantic v2)")
        except ImportError:
            print("⚠️ 不支持 ConfigDict (可能是 Pydantic v1)")
            
    except Exception as e:
        print(f"❌ 获取 Pydantic 信息失败: {e}")

def main():
    """主函数"""
    print("🔧 TradingAgents Pydantic 命名空间冲突修复验证")
    print("=" * 60)
    
    # 显示环境信息
    show_pydantic_info()
    
    # 运行测试
    test1_passed = test_pydantic_models()
    test2_passed = test_other_models()
    test3_passed = test_fastapi_startup()
    
    # 总结
    print("\n📊 测试结果总结")
    print("=" * 30)
    print(f"分析模型测试: {'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"数据模型测试: {'✅ 通过' if test2_passed else '❌ 失败'}")
    print(f"FastAPI 测试: {'✅ 通过' if test3_passed else '❌ 失败'}")
    
    if all([test1_passed, test2_passed, test3_passed]):
        print("\n🎉 所有测试通过！Pydantic 命名空间冲突已修复")
        print("\n💡 修复方法:")
        print("   在 AnalysisRequest 类中添加了:")
        print("   model_config = {'protected_namespaces': ()}")
        print("\n   这告诉 Pydantic v2 不要保护 'model_' 命名空间")
        return True
    else:
        print("\n❌ 部分测试失败，可能还有其他命名空间冲突")
        print("\n🔧 建议:")
        print("   1. 检查其他使用 'model_' 开头字段的 Pydantic 模型")
        print("   2. 在相关模型中添加 model_config = {'protected_namespaces': ()}")
        print("   3. 或者重命名字段，避免使用 'model_' 前缀")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
