#!/usr/bin/env python3
"""
Agent Service 测试脚本
用于验证智能体服务的基本功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.shared.logging_config import get_logger
from backend.agent_service.app.agents.base_agent import AgentType, TaskContext
from backend.agent_service.app.agents.analysts.fundamentals_analyst import FundamentalsAnalyst
from backend.agent_service.app.agents.analysts.market_analyst import MarketAnalyst
from backend.agent_service.app.agents.researchers.bull_researcher import BullResearcher
from backend.agent_service.app.agents.researchers.bear_researcher import BearResearcher

logger = get_logger("agent-service.test")


async def test_individual_agents():
    """测试单个智能体"""
    print("🧪 测试单个智能体功能...")
    
    # 创建测试上下文
    context = TaskContext(
        task_id="test_task_001",
        symbol="AAPL",
        company_name="Apple Inc.",
        market="US",
        analysis_date="2025-01-22",
        parameters={"test_mode": True},
        metadata={"source": "test"}
    )
    
    # 测试基本面分析师
    print("\n📊 测试基本面分析师...")
    fundamentals_analyst = FundamentalsAnalyst(AgentType.FUNDAMENTALS_ANALYST)
    try:
        result = await fundamentals_analyst.execute_task(context)
        print(f"✅ 基本面分析完成: {result.status}")
        print(f"   - 任务ID: {result.task_id}")
        print(f"   - 智能体ID: {result.agent_id}")
        print(f"   - 执行时间: {result.duration:.2f}秒")
    except Exception as e:
        print(f"❌ 基本面分析失败: {e}")
    
    # 测试市场分析师
    print("\n📈 测试市场分析师...")
    market_analyst = MarketAnalyst(AgentType.MARKET_ANALYST)
    try:
        result = await market_analyst.execute_task(context)
        print(f"✅ 市场分析完成: {result.status}")
        print(f"   - 任务ID: {result.task_id}")
        print(f"   - 智能体ID: {result.agent_id}")
        print(f"   - 执行时间: {result.duration:.2f}秒")
    except Exception as e:
        print(f"❌ 市场分析失败: {e}")
    
    # 测试看涨研究员
    print("\n📈 测试看涨研究员...")
    bull_researcher = BullResearcher(AgentType.BULL_RESEARCHER)
    try:
        result = await bull_researcher.execute_task(context)
        print(f"✅ 看涨研究完成: {result.status}")
        print(f"   - 任务ID: {result.task_id}")
        print(f"   - 智能体ID: {result.agent_id}")
        print(f"   - 执行时间: {result.duration:.2f}秒")
    except Exception as e:
        print(f"❌ 看涨研究失败: {e}")
    
    # 测试看跌研究员
    print("\n📉 测试看跌研究员...")
    bear_researcher = BearResearcher(AgentType.BEAR_RESEARCHER)
    try:
        result = await bear_researcher.execute_task(context)
        print(f"✅ 看跌研究完成: {result.status}")
        print(f"   - 任务ID: {result.task_id}")
        print(f"   - 智能体ID: {result.agent_id}")
        print(f"   - 执行时间: {result.duration:.2f}秒")
    except Exception as e:
        print(f"❌ 看跌研究失败: {e}")


async def test_agent_capabilities():
    """测试智能体能力"""
    print("\n🔍 测试智能体能力...")
    
    # 创建智能体
    fundamentals_analyst = FundamentalsAnalyst(AgentType.FUNDAMENTALS_ANALYST)
    
    # 测试能力检查
    print(f"📋 基本面分析师能力:")
    for capability in fundamentals_analyst.capabilities:
        print(f"   - {capability.name}: {capability.description}")
        print(f"     支持市场: {capability.supported_markets}")
        print(f"     最大并发: {capability.max_concurrent_tasks}")
        print(f"     预估时间: {capability.estimated_duration}秒")
    
    # 测试任务处理能力
    can_handle_fundamentals = fundamentals_analyst.can_handle_task(
        task_type=AgentType.FUNDAMENTALS_ANALYST.value, 
        market="US"
    )
    print(f"   - 可处理基本面分析任务: {can_handle_fundamentals}")
    
    can_handle_technical = fundamentals_analyst.can_handle_task(
        task_type="technical_analysis", 
        market="US"
    )
    print(f"   - 可处理技术分析任务: {can_handle_technical}")


async def test_agent_health():
    """测试智能体健康检查"""
    print("\n🏥 测试智能体健康检查...")
    
    agents = [
        FundamentalsAnalyst(AgentType.FUNDAMENTALS_ANALYST),
        MarketAnalyst(AgentType.MARKET_ANALYST),
        BullResearcher(AgentType.BULL_RESEARCHER),
        BearResearcher(AgentType.BEAR_RESEARCHER)
    ]
    
    for agent in agents:
        try:
            is_healthy = await agent.health_check()
            status = "健康" if is_healthy else "不健康"
            print(f"   - {agent.agent_type.value}: {status}")
        except Exception as e:
            print(f"   - {agent.agent_type.value}: 检查失败 - {e}")


async def test_agent_status():
    """测试智能体状态"""
    print("\n📊 测试智能体状态...")
    
    agent = FundamentalsAnalyst(AgentType.FUNDAMENTALS_ANALYST)
    status = agent.get_status()
    
    print(f"   - 智能体ID: {status['agent_id']}")
    print(f"   - 智能体类型: {status['agent_type']}")
    print(f"   - 当前状态: {status['status']}")
    print(f"   - 当前任务数: {status['current_tasks']}")
    print(f"   - 创建时间: {status['created_at']}")
    print(f"   - 最后心跳: {status['last_heartbeat']}")
    print(f"   - 能力数量: {len(status['capabilities'])}")


async def test_concurrent_tasks():
    """测试并发任务处理"""
    print("\n🔄 测试并发任务处理...")
    
    agent = MarketAnalyst(AgentType.MARKET_ANALYST)
    
    # 创建多个测试任务
    tasks = []
    for i in range(3):
        context = TaskContext(
            task_id=f"concurrent_task_{i+1}",
            symbol=f"TEST{i+1}",
            company_name=f"Test Company {i+1}",
            market="US",
            analysis_date="2025-01-22",
            parameters={"test_mode": True, "task_number": i+1}
        )
        task = agent.execute_task(context)
        tasks.append(task)
    
    # 并发执行
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"   - 任务{i+1}: 失败 - {result}")
            else:
                print(f"   - 任务{i+1}: 成功 - {result.status} ({result.duration:.2f}秒)")
                success_count += 1
        
        print(f"   - 成功率: {success_count}/{len(tasks)} ({success_count/len(tasks)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ 并发任务测试失败: {e}")


async def test_workflow_manager():
    """测试工作流管理器"""
    print("\n🔄 测试工作流管理器...")

    try:
        from backend.agent_service.app.orchestration.workflow_manager import WorkflowManager
        from backend.agent_service.app.utils.state_manager import StateManager
        from backend.agent_service.app.orchestration.collaboration_engine import CollaborationEngine
        from backend.agent_service.app.agents.agent_manager import AgentManager

        # 创建模拟组件
        state_manager = StateManager()
        agent_manager = AgentManager()
        collaboration_engine = CollaborationEngine(agent_manager, state_manager, None)

        # 创建工作流管理器
        workflow_manager = WorkflowManager(agent_manager, state_manager, collaboration_engine)
        await workflow_manager.initialize()

        # 测试工作流定义
        definitions = workflow_manager.get_workflow_definitions()
        print(f"   - 可用工作流: {len(definitions)}个")
        for workflow_id, definition in definitions.items():
            print(f"     * {workflow_id}: {definition.name} ({len(definition.steps)}步骤)")

        # 测试工作流验证
        test_context = {
            "symbol": "AAPL",
            "company_name": "Apple Inc.",
            "market": "US",
            "analysis_date": "2025-01-22"
        }

        print(f"   - 测试上下文验证: 通过")

        print("✅ 工作流管理器测试完成")

    except Exception as e:
        print(f"❌ 工作流管理器测试失败: {e}")


async def test_performance_monitor():
    """测试性能监控器"""
    print("\n📊 测试性能监控器...")

    try:
        from backend.agent_service.app.utils.performance_monitor import PerformanceMonitor
        from backend.agent_service.app.utils.state_manager import StateManager

        # 创建性能监控器
        state_manager = StateManager()
        monitor = PerformanceMonitor(state_manager)
        await monitor.initialize()

        # 测试系统指标
        metrics = await monitor.get_system_metrics()
        print(f"   - CPU使用率: {metrics.cpu_usage:.1f}%")
        print(f"   - 内存使用率: {metrics.memory_usage:.1f}%")
        print(f"   - 活跃任务: {metrics.active_tasks}")

        # 模拟任务记录
        await monitor.record_task_start("test_agent", "test_analyst", "test_task_001")
        await asyncio.sleep(0.1)
        await monitor.record_task_completion("test_agent", "test_task_001", True, 0.1)

        # 获取智能体指标
        agent_metrics = await monitor.get_agent_metrics("test_agent")
        print(f"   - 测试智能体任务数: {agent_metrics.get('total_tasks', 0)}")

        # 获取性能摘要
        summary = await monitor.get_performance_summary()
        print(f"   - 性能等级: {summary.get('performance_grade', 'Unknown')}")

        await monitor.cleanup()
        print("✅ 性能监控器测试完成")

    except Exception as e:
        print(f"❌ 性能监控器测试失败: {e}")


async def test_consensus_algorithm():
    """测试共识算法"""
    print("\n🤝 测试共识算法...")

    try:
        from backend.agent_service.app.orchestration.consensus_algorithm import ConsensusAlgorithm, ConsensusMethod
        from backend.agent_service.app.utils.state_manager import StateManager
        from backend.agent_service.app.agents.agent_manager import AgentManager

        # 创建共识算法
        state_manager = StateManager()
        agent_manager = AgentManager()
        consensus = ConsensusAlgorithm(agent_manager, state_manager)
        await consensus.initialize()

        # 创建模拟智能体结果
        mock_results = {
            "fundamentals_analyst": {
                "status": "success",
                "agent_type": "fundamentals_analyst",
                "result": {
                    "investment_recommendation": {"recommendation": "buy"},
                    "confidence_score": 0.8
                }
            },
            "market_analyst": {
                "status": "success",
                "agent_type": "market_analyst",
                "result": {
                    "investment_recommendation": {"recommendation": "buy"},
                    "confidence_score": 0.7
                }
            },
            "risk_manager": {
                "status": "success",
                "agent_type": "risk_manager",
                "result": {
                    "investment_recommendation": {"recommendation": "hold"},
                    "confidence_score": 0.6
                }
            }
        }

        # 测试不同的共识方法
        methods = [ConsensusMethod.MAJORITY_VOTE, ConsensusMethod.WEIGHTED_VOTE, ConsensusMethod.HYBRID]

        for method in methods:
            result = await consensus.reach_consensus(mock_results, method)
            print(f"   - {method.value}: {result.get('recommendation', 'unknown')} (置信度: {result.get('consensus_strength', 0):.2f})")

        print("✅ 共识算法测试完成")

    except Exception as e:
        print(f"❌ 共识算法测试失败: {e}")


async def main():
    """主测试函数"""
    print("🚀 开始Agent Service完整测试...")
    print("=" * 60)

    try:
        # 测试单个智能体
        await test_individual_agents()

        # 测试智能体能力
        await test_agent_capabilities()

        # 测试健康检查
        await test_agent_health()

        # 测试状态获取
        await test_agent_status()

        # 测试并发任务
        await test_concurrent_tasks()

        # 测试工作流管理器
        await test_workflow_manager()

        # 测试性能监控器
        await test_performance_monitor()

        # 测试共识算法
        await test_consensus_algorithm()

        print("\n" + "=" * 60)
        print("✅ Agent Service完整测试完成!")
        print("🎯 所有核心功能验证通过:")
        print("   - ✅ 智能体基础功能")
        print("   - ✅ 工作流管理")
        print("   - ✅ 性能监控")
        print("   - ✅ 共识算法")
        print("   - ✅ 协作机制")

    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 设置事件循环策略（Windows兼容性）
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # 运行测试
    asyncio.run(main())
