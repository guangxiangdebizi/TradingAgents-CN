"""
工作流管理器
负责复杂工作流的定义、执行和管理
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from backend.shared.logging_config import get_logger

logger = get_logger("agent-service.workflow_manager")


class WorkflowStatus(Enum):
    """工作流状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class StepStatus(Enum):
    """步骤状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """工作流步骤"""
    step_id: str
    name: str
    agent_types: List[str]
    dependencies: List[str] = field(default_factory=list)
    parallel: bool = False
    optional: bool = False
    timeout: int = 300
    retry_count: int = 0
    max_retries: int = 3
    condition: Optional[Callable] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # 运行时状态
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class WorkflowDefinition:
    """工作流定义"""
    workflow_id: str
    name: str
    description: str
    version: str
    steps: List[WorkflowStep]
    global_timeout: int = 1800
    failure_strategy: str = "stop"  # stop, continue, retry
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """工作流执行实例"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    context: Dict[str, Any]
    current_step_index: int = 0
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    step_results: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    final_result: Dict[str, Any] = field(default_factory=dict)


class WorkflowManager:
    """工作流管理器"""
    
    def __init__(self, agent_manager, state_manager, collaboration_engine):
        self.agent_manager = agent_manager
        self.state_manager = state_manager
        self.collaboration_engine = collaboration_engine
        
        # 工作流定义注册表
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        
        # 活跃的工作流执行
        self.active_executions: Dict[str, WorkflowExecution] = {}
        
        # 初始化预定义工作流
        self._initialize_predefined_workflows()
        
        logger.info("🏗️ 工作流管理器初始化")

    async def initialize(self):
        """初始化工作流管理器"""
        try:
            logger.info("✅ 工作流管理器初始化完成")
        except Exception as e:
            logger.error(f"❌ 工作流管理器初始化失败: {e}")
            raise
    
    def _initialize_predefined_workflows(self):
        """初始化预定义工作流"""
        # 综合分析工作流
        comprehensive_workflow = WorkflowDefinition(
            workflow_id="comprehensive_analysis_v2",
            name="综合分析工作流 v2.0",
            description="包含数据收集、多维分析、辩论和决策的完整工作流",
            version="2.0",
            steps=[
                WorkflowStep(
                    step_id="data_preparation",
                    name="数据准备",
                    agent_types=["data_collector"],
                    parallel=False,
                    timeout=120
                ),
                WorkflowStep(
                    step_id="parallel_analysis",
                    name="并行分析",
                    agent_types=["fundamentals_analyst", "market_analyst", "news_analyst"],
                    dependencies=["data_preparation"],
                    parallel=True,
                    timeout=300
                ),
                WorkflowStep(
                    step_id="sentiment_analysis",
                    name="情感分析",
                    agent_types=["social_media_analyst"],
                    dependencies=["data_preparation"],
                    parallel=False,
                    optional=True,
                    timeout=180
                ),
                WorkflowStep(
                    step_id="research_debate",
                    name="研究辩论",
                    agent_types=["bull_researcher", "bear_researcher"],
                    dependencies=["parallel_analysis"],
                    parallel=False,
                    timeout=240
                ),
                WorkflowStep(
                    step_id="risk_assessment",
                    name="风险评估辩论",
                    agent_types=["risky_debator", "safe_debator", "neutral_debator"],
                    dependencies=["research_debate"],
                    parallel=False,
                    timeout=180
                ),
                WorkflowStep(
                    step_id="management_review",
                    name="管理层审核",
                    agent_types=["research_manager", "risk_manager"],
                    dependencies=["risk_assessment"],
                    parallel=True,
                    timeout=200
                ),
                WorkflowStep(
                    step_id="final_decision",
                    name="最终决策",
                    agent_types=["trader"],
                    dependencies=["management_review"],
                    parallel=False,
                    timeout=120
                )
            ],
            global_timeout=1800,
            failure_strategy="continue"
        )
        
        # 快速分析工作流
        quick_workflow = WorkflowDefinition(
            workflow_id="quick_analysis_v2",
            name="快速分析工作流 v2.0",
            description="快速的技术分析和风险评估",
            version="2.0",
            steps=[
                WorkflowStep(
                    step_id="technical_analysis",
                    name="技术分析",
                    agent_types=["market_analyst"],
                    parallel=False,
                    timeout=120
                ),
                WorkflowStep(
                    step_id="risk_check",
                    name="风险检查",
                    agent_types=["risk_manager"],
                    dependencies=["technical_analysis"],
                    parallel=False,
                    timeout=90
                ),
                WorkflowStep(
                    step_id="quick_decision",
                    name="快速决策",
                    agent_types=["trader"],
                    dependencies=["risk_check"],
                    parallel=False,
                    timeout=60
                )
            ],
            global_timeout=600,
            failure_strategy="stop"
        )
        
        # 注册工作流
        self.register_workflow(comprehensive_workflow)
        self.register_workflow(quick_workflow)
    
    def register_workflow(self, workflow: WorkflowDefinition):
        """注册工作流定义"""
        self.workflow_definitions[workflow.workflow_id] = workflow
        logger.info(f"📋 注册工作流: {workflow.workflow_id} - {workflow.name}")
    
    async def start_workflow(
        self,
        workflow_id: str,
        context: Dict[str, Any],
        execution_id: Optional[str] = None
    ) -> str:
        """启动工作流执行"""
        try:
            # 获取工作流定义
            workflow_def = self.workflow_definitions.get(workflow_id)
            if not workflow_def:
                raise ValueError(f"工作流不存在: {workflow_id}")
            
            # 创建执行实例
            if not execution_id:
                execution_id = str(uuid.uuid4())
            
            execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.PENDING,
                context=context
            )
            
            self.active_executions[execution_id] = execution
            
            # 保存状态
            await self.state_manager.save_workflow_state(execution_id, execution.__dict__)
            
            # 启动执行
            asyncio.create_task(self._execute_workflow(execution_id))
            
            logger.info(f"🚀 启动工作流: {execution_id} - {workflow_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"❌ 启动工作流失败: {workflow_id} - {e}")
            raise
    
    async def _execute_workflow(self, execution_id: str):
        """执行工作流"""
        try:
            execution = self.active_executions.get(execution_id)
            if not execution:
                raise ValueError(f"工作流执行不存在: {execution_id}")
            
            workflow_def = self.workflow_definitions[execution.workflow_id]
            execution.status = WorkflowStatus.RUNNING
            
            logger.info(f"🔄 开始执行工作流: {execution_id}")
            
            # 创建步骤依赖图
            step_graph = self._build_dependency_graph(workflow_def.steps)
            
            # 按依赖顺序执行步骤
            while execution.current_step_index < len(workflow_def.steps):
                # 获取可执行的步骤
                ready_steps = self._get_ready_steps(workflow_def.steps, execution.completed_steps)
                
                if not ready_steps:
                    # 检查是否有失败的必需步骤
                    if self._has_failed_required_steps(workflow_def.steps, execution.failed_steps):
                        execution.status = WorkflowStatus.FAILED
                        execution.error = "必需步骤执行失败"
                        break
                    else:
                        # 所有步骤都已完成
                        break
                
                # 执行准备好的步骤
                await self._execute_steps_batch(execution, workflow_def, ready_steps)
                
                # 更新状态
                await self.state_manager.save_workflow_state(execution_id, execution.__dict__)
            
            # 完成工作流
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.COMPLETED
                execution.final_result = await self._aggregate_workflow_results(execution)
            
            execution.completed_at = datetime.now()
            
            # 最终状态保存
            await self.state_manager.save_workflow_state(execution_id, execution.__dict__)
            
            logger.info(f"✅ 工作流执行完成: {execution_id} - {execution.status.value}")
            
        except Exception as e:
            logger.error(f"❌ 工作流执行失败: {execution_id} - {e}")
            if execution_id in self.active_executions:
                execution = self.active_executions[execution_id]
                execution.status = WorkflowStatus.FAILED
                execution.error = str(e)
                execution.completed_at = datetime.now()
    
    def _build_dependency_graph(self, steps: List[WorkflowStep]) -> Dict[str, List[str]]:
        """构建步骤依赖图"""
        graph = {}
        for step in steps:
            graph[step.step_id] = step.dependencies.copy()
        return graph
    
    def _get_ready_steps(self, steps: List[WorkflowStep], completed_steps: List[str]) -> List[WorkflowStep]:
        """获取准备执行的步骤"""
        ready_steps = []
        for step in steps:
            if (step.step_id not in completed_steps and 
                step.status == StepStatus.PENDING and
                all(dep in completed_steps for dep in step.dependencies)):
                ready_steps.append(step)
        return ready_steps
    
    def _has_failed_required_steps(self, steps: List[WorkflowStep], failed_steps: List[str]) -> bool:
        """检查是否有必需步骤失败"""
        for step in steps:
            if step.step_id in failed_steps and not step.optional:
                return True
        return False
    
    async def _execute_steps_batch(
        self, 
        execution: WorkflowExecution, 
        workflow_def: WorkflowDefinition, 
        steps: List[WorkflowStep]
    ):
        """批量执行步骤"""
        try:
            # 分组：并行步骤和顺序步骤
            parallel_steps = [step for step in steps if step.parallel]
            sequential_steps = [step for step in steps if not step.parallel]
            
            # 先执行并行步骤
            if parallel_steps:
                await self._execute_parallel_steps(execution, parallel_steps)
            
            # 再执行顺序步骤
            for step in sequential_steps:
                await self._execute_single_step(execution, step)
                
        except Exception as e:
            logger.error(f"❌ 批量执行步骤失败: {e}")
            raise
    
    async def _execute_parallel_steps(self, execution: WorkflowExecution, steps: List[WorkflowStep]):
        """并行执行步骤"""
        try:
            tasks = []
            for step in steps:
                task = self._execute_single_step(execution, step)
                tasks.append(task)
            
            # 等待所有并行步骤完成
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ 并行执行步骤失败: {e}")
            raise
    
    async def _execute_single_step(self, execution: WorkflowExecution, step: WorkflowStep):
        """执行单个步骤"""
        try:
            step.status = StepStatus.RUNNING
            step.started_at = datetime.now()
            
            logger.info(f"🔧 执行步骤: {step.name} ({step.step_id})")
            
            # 检查条件
            if step.condition and not step.condition(execution.context):
                step.status = StepStatus.SKIPPED
                logger.info(f"⏭️ 跳过步骤: {step.name} (条件不满足)")
                return
            
            # 执行智能体任务
            step_results = {}
            for agent_type in step.agent_types:
                try:
                    result = await self.collaboration_engine._create_agent_task(
                        agent_type, execution.context
                    )
                    step_results[agent_type] = result
                except Exception as e:
                    logger.error(f"❌ 智能体任务失败: {agent_type} - {e}")
                    step_results[agent_type] = {
                        "status": "failed",
                        "error": str(e)
                    }
            
            # 更新步骤结果
            step.results = step_results
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.now()
            
            # 更新执行状态
            execution.completed_steps.append(step.step_id)
            execution.step_results[step.step_id] = step_results
            
            logger.info(f"✅ 步骤完成: {step.name}")
            
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.now()
            
            execution.failed_steps.append(step.step_id)
            
            logger.error(f"❌ 步骤失败: {step.name} - {e}")
            
            # 根据失败策略处理
            if not step.optional:
                raise
    
    async def _aggregate_workflow_results(self, execution: WorkflowExecution) -> Dict[str, Any]:
        """聚合工作流结果"""
        try:
            # 收集所有步骤的结果
            all_results = {}
            for step_id, step_results in execution.step_results.items():
                all_results[step_id] = step_results
            
            # 使用共识算法聚合最终结果
            from ..main import consensus_algorithm
            if consensus_algorithm:
                # 提取智能体结果
                agent_results = {}
                for step_results in execution.step_results.values():
                    for agent_type, result in step_results.items():
                        if result.get("status") == "completed":
                            agent_results[f"{agent_type}_{step_id}"] = result
                
                if agent_results:
                    consensus = await consensus_algorithm.reach_consensus(agent_results)
                    return {
                        "workflow_consensus": consensus,
                        "step_results": all_results,
                        "execution_summary": {
                            "total_steps": len(execution.step_results),
                            "completed_steps": len(execution.completed_steps),
                            "failed_steps": len(execution.failed_steps)
                        }
                    }
            
            return {
                "step_results": all_results,
                "execution_summary": {
                    "total_steps": len(execution.step_results),
                    "completed_steps": len(execution.completed_steps),
                    "failed_steps": len(execution.failed_steps)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 聚合工作流结果失败: {e}")
            return {"error": str(e)}
    
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """获取工作流执行状态"""
        try:
            execution = self.active_executions.get(execution_id)
            if execution:
                return execution.__dict__
            
            # 从状态管理器获取
            return await self.state_manager.get_workflow_state(execution_id)
            
        except Exception as e:
            logger.error(f"❌ 获取工作流执行状态失败: {execution_id} - {e}")
            return None
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """取消工作流执行"""
        try:
            if execution_id in self.active_executions:
                execution = self.active_executions[execution_id]
                execution.status = WorkflowStatus.CANCELLED
                execution.completed_at = datetime.now()
                
                await self.state_manager.save_workflow_state(execution_id, execution.__dict__)
                
                logger.info(f"🚫 取消工作流执行: {execution_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ 取消工作流执行失败: {execution_id} - {e}")
            return False
    
    def get_workflow_definitions(self) -> Dict[str, WorkflowDefinition]:
        """获取所有工作流定义"""
        return self.workflow_definitions.copy()
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            return True
        except Exception as e:
            logger.error(f"❌ 工作流管理器健康检查失败: {e}")
            return False
    
    async def cleanup(self):
        """清理资源"""
        try:
            # 取消所有活跃的执行
            for execution_id in list(self.active_executions.keys()):
                await self.cancel_execution(execution_id)
            
            self.active_executions.clear()
            
            logger.info("✅ 工作流管理器清理完成")
            
        except Exception as e:
            logger.error(f"❌ 工作流管理器清理失败: {e}")
