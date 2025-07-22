#!/usr/bin/env python3
"""
Memory Service测试
测试Embedding记忆系统的完整功能
"""

import asyncio
import pytest
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from memory_service.app.memory.memory_manager import MemoryManager
from memory_service.app.embedding.embedding_service import EmbeddingService
from memory_service.app.vector_db.chroma_manager import ChromaManager

class TestMemoryService:
    """Memory Service测试类"""
    
    @pytest.fixture
    async def memory_manager(self):
        """创建记忆管理器"""
        # 初始化组件
        chroma_manager = ChromaManager()
        await chroma_manager.initialize()
        
        embedding_service = EmbeddingService()
        await embedding_service.initialize()
        
        memory_manager = MemoryManager(
            chroma_manager=chroma_manager,
            embedding_service=embedding_service
        )
        await memory_manager.initialize()
        
        yield memory_manager
        
        # 清理
        await memory_manager.cleanup()
        await embedding_service.cleanup()
        await chroma_manager.cleanup()
    
    @pytest.mark.asyncio
    async def test_add_and_search_memory(self, memory_manager):
        """测试添加和搜索记忆"""
        print("\n🧪 测试添加和搜索记忆")
        
        # 添加测试记忆
        collection_name = "test_memory"
        situation = "科技股下跌，市场恐慌情绪蔓延"
        recommendation = "建议关注基本面良好的大型科技公司，如苹果、微软等"
        
        result = await memory_manager.add_memory(
            collection_name=collection_name,
            situation=situation,
            recommendation=recommendation,
            metadata={"test": True, "category": "tech_stocks"}
        )
        
        assert result is not None
        assert result["situation"] == situation
        assert result["recommendation"] == recommendation
        print(f"✅ 记忆添加成功: {result['memory_id']}")
        
        # 搜索相似记忆
        query = "技术股暴跌，投资者担忧"
        memories = await memory_manager.search_memory(
            collection_name=collection_name,
            query=query,
            n_results=1,
            similarity_threshold=0.0
        )
        
        assert len(memories) > 0
        memory = memories[0]
        assert memory["matched_situation"] == situation
        assert memory["recommendation"] == recommendation
        assert memory["similarity_score"] > 0.5  # 应该有较高相似度
        
        print(f"✅ 记忆搜索成功: 相似度 {memory['similarity_score']:.3f}")
        print(f"   匹配情况: {memory['matched_situation']}")
        print(f"   建议: {memory['recommendation']}")
    
    @pytest.mark.asyncio
    async def test_batch_add_memories(self, memory_manager):
        """测试批量添加记忆"""
        print("\n🧪 测试批量添加记忆")
        
        collection_name = "test_batch_memory"
        situations_and_advice = [
            ("高通胀环境，利率上升，科技股承压", "建议关注现金流稳定的大型科技公司"),
            ("市场波动加剧，投资者情绪谨慎", "建议分散投资，关注防御性板块"),
            ("新兴市场货币贬值，资金流出", "建议减少新兴市场敞口，增加发达市场配置"),
            ("央行政策转向宽松，流动性充裕", "建议增加成长股配置，关注科技和消费板块")
        ]
        
        result = await memory_manager.add_situations_batch(
            collection_name=collection_name,
            situations_and_advice=situations_and_advice
        )
        
        assert result is not None
        assert result["added_count"] == len(situations_and_advice)
        print(f"✅ 批量添加成功: {result['added_count']}条记忆")
        
        # 测试搜索
        query = "通胀上升时期的投资策略"
        memories = await memory_manager.search_memory(
            collection_name=collection_name,
            query=query,
            n_results=2
        )
        
        assert len(memories) > 0
        print(f"✅ 批量记忆搜索成功: 找到{len(memories)}条相关记忆")
        
        for i, memory in enumerate(memories, 1):
            print(f"   记忆{i} (相似度: {memory['similarity_score']:.3f}):")
            print(f"     情况: {memory['matched_situation']}")
            print(f"     建议: {memory['recommendation']}")
    
    @pytest.mark.asyncio
    async def test_collection_management(self, memory_manager):
        """测试集合管理"""
        print("\n🧪 测试集合管理")
        
        # 创建集合
        collection_name = "test_collection_mgmt"
        description = "测试集合管理功能"
        metadata = {"purpose": "testing", "created_by": "test_suite"}
        
        collection = await memory_manager.create_collection(
            name=collection_name,
            description=description,
            metadata=metadata
        )
        
        assert collection is not None
        assert collection["description"] == description
        print(f"✅ 集合创建成功: {collection_name}")
        
        # 获取集合列表
        collections = await memory_manager.list_collections()
        collection_names = [col["name"] for col in collections]
        assert collection_name in collection_names
        print(f"✅ 集合列表获取成功: 共{len(collections)}个集合")
        
        # 获取集合统计
        stats = await memory_manager.get_collection_stats(collection_name)
        assert stats is not None
        assert stats["name"] == collection_name
        assert stats["count"] == 0  # 新创建的集合应该为空
        print(f"✅ 集合统计获取成功: {stats}")
        
        # 删除集合
        await memory_manager.delete_collection(collection_name)
        print(f"✅ 集合删除成功: {collection_name}")
    
    @pytest.mark.asyncio
    async def test_tradingagents_compatibility(self, memory_manager):
        """测试与TradingAgents的兼容性"""
        print("\n🧪 测试TradingAgents兼容性")
        
        # 模拟TradingAgents的使用场景
        collection_name = "bull_memory"
        
        # 添加看涨分析师的历史记忆
        situations_and_advice = [
            ("苹果公司发布新产品，市场反应积极", "建议增加苹果股票配置，目标价位上调10%"),
            ("科技板块整体上涨，资金流入明显", "建议关注龙头科技股，适当增加仓位"),
            ("市场情绪乐观，风险偏好提升", "建议增加成长股配置，减少防御性资产")
        ]
        
        # 批量添加记忆
        await memory_manager.add_situations_batch(
            collection_name=collection_name,
            situations_and_advice=situations_and_advice
        )
        print(f"✅ 看涨分析师记忆添加成功: {len(situations_and_advice)}条")
        
        # 模拟当前市场情况
        current_situation = "科技股强势上涨，市场乐观情绪高涨，投资者风险偏好明显提升"
        
        # 使用TradingAgents兼容接口
        past_memories = await memory_manager.get_memories(
            collection_name=collection_name,
            current_situation=current_situation,
            n_matches=2
        )
        
        assert len(past_memories) > 0
        print(f"✅ TradingAgents兼容接口测试成功: 找到{len(past_memories)}条相关记忆")
        
        # 验证记忆格式
        for i, memory in enumerate(past_memories, 1):
            assert "matched_situation" in memory
            assert "recommendation" in memory
            assert "similarity_score" in memory
            
            print(f"   历史记忆{i} (相似度: {memory['similarity_score']:.3f}):")
            print(f"     情况: {memory['matched_situation']}")
            print(f"     建议: {memory['recommendation']}")

async def run_manual_test():
    """手动运行测试"""
    print("🧠 Memory Service 功能测试")
    print("=" * 60)
    
    try:
        # 初始化组件
        print("🔧 初始化测试组件...")
        chroma_manager = ChromaManager()
        await chroma_manager.initialize()
        
        embedding_service = EmbeddingService()
        await embedding_service.initialize()
        
        memory_manager = MemoryManager(
            chroma_manager=chroma_manager,
            embedding_service=embedding_service
        )
        await memory_manager.initialize()
        
        print("✅ 组件初始化完成")
        
        # 创建测试实例
        test_instance = TestMemoryService()
        
        # 运行测试
        await test_instance.test_add_and_search_memory(memory_manager)
        await test_instance.test_batch_add_memories(memory_manager)
        await test_instance.test_collection_management(memory_manager)
        await test_instance.test_tradingagents_compatibility(memory_manager)
        
        print("\n🎉 所有测试通过！")
        
        # 清理资源
        await memory_manager.cleanup()
        await embedding_service.cleanup()
        await chroma_manager.cleanup()
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行手动测试
    asyncio.run(run_manual_test())
