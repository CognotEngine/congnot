# 任务队列模块

import asyncio
import logging
from typing import Dict, Any, Optional
from uuid import uuid4
from pydantic import BaseModel
from core.module.module_interface import Module, ModuleMetadata
from core.module.module_manager import module_manager
from core.workflow_manager import WorkflowManager
from core.execution_queue import ExecutionQueue, Task, TaskStatus, create_execution_queue

# 设置日志
logger = logging.getLogger(__name__)

# 任务队列模块API接口
class TaskQueueModuleAPI:
    def __init__(self, task_queue_manager):
        self.task_queue_manager = task_queue_manager
    
    async def enqueue_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """将工作流任务添加到队列"""
        return await self.task_queue_manager.enqueue_workflow(workflow_data)
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        return self.task_queue_manager.get_job_status(job_id)
    
    def get_queue_info(self) -> Dict[str, Any]:
        """获取队列信息"""
        return self.task_queue_manager.get_queue_info()
    
    def get_queue_tasks(self) -> Dict[str, Any]:
        """获取队列中的所有任务"""
        return self.task_queue_manager.get_queue_tasks()

# 任务队列管理器类
class TaskQueueManager:
    def __init__(self, workflow_manager: WorkflowManager):
        self.workflow_manager = workflow_manager
        self.execution_queue = create_execution_queue(on_queue_updated=self._on_queue_updated)
        self.tasks: Dict[str, Dict[str, Any]] = {}
        
        # 设置执行队列的回调函数
        self.execution_queue.on_task_start = self._on_task_start
        self.execution_queue.on_task_complete = self._on_task_complete
        self.execution_queue.on_task_fail = self._on_task_fail
    
    async def _on_task_start(self, task_id: str, node_id: str, node_type: str):
        logger.info(f"Task {task_id} started on node {node_id} (type: {node_type})")
        # 更新任务状态
        for workflow_task_id, workflow_task_data in self.tasks.items():
            if task_id in workflow_task_data['node_tasks'].values():
                workflow_task_data['status'] = 'running'
                break
    
    async def _on_task_complete(self, task_id: str, node_id: str, result: Any, execution_time: float):
        logger.info(f"Task {task_id} completed on node {node_id} in {execution_time} seconds")
        # 检查是否所有节点任务都已完成
        for workflow_task_id, workflow_task_data in self.tasks.items():
            if task_id in workflow_task_data['node_tasks'].values():
                # 检查该工作流的所有节点任务是否都已完成
                all_completed = all(
                    self.execution_queue.tasks.get(node_task_id, TaskStatus.PENDING).status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                    for node_task_id in workflow_task_data['node_tasks'].values()
                )
                
                if all_completed:
                    # 检查是否有失败的任务
                    any_failed = any(
                        self.execution_queue.tasks.get(node_task_id, TaskStatus.PENDING).status == TaskStatus.FAILED
                        for node_task_id in workflow_task_data['node_tasks'].values()
                    )
                    
                    workflow_task_data['status'] = 'completed' if not any_failed else 'failed'
                    workflow_task_data['completed_at'] = asyncio.get_event_loop().time()
                    break
    
    async def _on_task_fail(self, task_id: str, node_id: str, error: Exception):
        logger.error(f"Task {task_id} failed on node {node_id}: {str(error)}")
        # 标记包含此节点的工作流为失败
        for workflow_task_id, workflow_task_data in self.tasks.items():
            if task_id in workflow_task_data['node_tasks'].values():
                workflow_task_data['status'] = 'failed'
                workflow_task_data['error'] = str(error)
                break
    
    def _on_queue_updated(self):
        """队列更新时的回调"""
        logger.debug(f"Queue updated: {self.execution_queue.get_statistics()}")
    
    async def add_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> str:
        """添加工作流到队列"""
        try:
            # 验证工作流数据
            if not self.workflow_manager.validate_workflow(workflow_data):
                raise ValueError(f"Invalid workflow data for workflow {workflow_id}")
            
            # 生成唯一任务ID
            task_id = str(uuid4())
            
            # 解析工作流节点和连接，构建任务依赖图
            tasks_to_add = []
            node_id_to_task_id = {}
            
            # 首先收集所有节点和它们的依赖关系
            node_dependencies = {}
            all_nodes = {}
            
            for node in workflow_data['nodes']:
                node_id = node['id']
                all_nodes[node_id] = node
                
                # 收集该节点依赖的所有节点ID
                deps = set()
                for input_name, input_data in node.get('inputs', {}).items():
                    if isinstance(input_data, dict) and '$ref' in input_data:
                        ref_node_id = input_data['$ref'].split('.')[0]
                        deps.add(ref_node_id)
                
                node_dependencies[node_id] = deps
            
            # 拓扑排序节点，确保按依赖顺序处理
            sorted_nodes = []
            visited = set()
            temp = set()
            
            def dfs(node_id):
                if node_id in temp:
                    raise ValueError(f"Circular dependency detected in workflow: {node_id}")
                if node_id not in visited:
                    temp.add(node_id)
                    for dep in node_dependencies[node_id]:
                        dfs(dep)
                    temp.remove(node_id)
                    visited.add(node_id)
                    sorted_nodes.append(node_id)
            
            # 对所有未访问的节点执行DFS
            for node_id in node_dependencies:
                if node_id not in visited:
                    dfs(node_id)
            
            # 按照拓扑排序的顺序创建任务
            for node_id in sorted_nodes:
                node = all_nodes[node_id]
                
                # 构建任务输入（包含来自其他节点的引用）
                inputs = {}
                for input_name, input_data in node.get('inputs', {}).items():
                    if isinstance(input_data, dict) and '$ref' in input_data:
                        # 这是一个对其他节点输出的引用
                        ref_node_id = input_data['$ref'].split('.')[0]
                        inputs[input_name] = {'$ref': f"{node_id_to_task_id[ref_node_id]}.result"}
                    else:
                        # 这是一个直接输入值
                        inputs[input_name] = input_data
                
                # 确定任务依赖
                dependencies = []
                for input_name, input_data in node.get('inputs', {}).items():
                    if isinstance(input_data, dict) and '$ref' in input_data:
                        ref_node_id = input_data['$ref'].split('.')[0]
                        dependencies.append(node_id_to_task_id[ref_node_id])
                
                # 创建任务（Task类会自动生成task_id）
                task = Task(
                    node_id=node_id,
                    node_type=node['type'],
                    inputs=inputs,
                    dependencies=dependencies,
                    priority=node.get('priority', 50)  # 默认优先级为50
                )
                tasks_to_add.append(task)
                node_id_to_task_id[node_id] = task.task_id
            
            # 记录任务信息
            self.tasks[task_id] = {
                'workflow_id': workflow_id,
                'status': 'queued',
                'created_at': asyncio.get_event_loop().time(),
                'node_tasks': node_id_to_task_id
            }
            
            # 将所有任务添加到执行队列
            for task in tasks_to_add:
                self.execution_queue.add_task(task)
            
            logger.info(f"Workflow {workflow_id} added to queue with task_id {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error adding workflow {workflow_id} to queue: {str(e)}")
            raise
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if task_id not in self.tasks:
            return None
        
        # 获取详细的节点任务状态
        task_data = self.tasks[task_id].copy()
        task_data['node_task_statuses'] = {}
        
        for node_id, node_task_id in task_data['node_tasks'].items():
            execution_task = self.execution_queue.tasks.get(node_task_id)
            if execution_task:
                task_data['node_task_statuses'][node_id] = {
                    'status': execution_task.status.value,
                    'result': execution_task.result,
                    'error': execution_task.error,
                    'execution_time': execution_task.execution_time
                }
        
        return task_data
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        try:
            if task_id not in self.tasks:
                return False
            
            # 标记任务为已取消
            self.tasks[task_id]['status'] = 'cancelled'
            logger.info(f"Task {task_id} marked as cancelled")
            
            # 这里可以添加实际取消执行中任务的逻辑
            # 目前ExecutionQueue类还没有实现取消任务的功能
            
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling task {task_id}: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取队列统计信息"""
        stats = self.execution_queue.get_statistics()
        stats['total_workflows'] = len(self.tasks)
        stats['workflow_status'] = {}
        
        for task_id, task_data in self.tasks.items():
            status = task_data['status']
            stats['workflow_status'][status] = stats['workflow_status'].get(status, 0) + 1
        
        return stats
    
    async def start(self):
        """启动队列处理"""
        await self.execution_queue.start()
    
    async def stop(self):
        """停止队列处理"""
        await self.execution_queue.stop()
    
    async def wait_until_complete(self):
        """等待所有任务完成"""
        await self.execution_queue.wait_until_complete()
    
    # 兼容旧接口
    async def enqueue_workflow(self, workflow_data: Dict[str, Any], retry_config: Optional[Dict[str, Any]] = None) -> str:
        """将工作流任务添加到队列"""
        workflow_id = str(uuid4())  # 生成临时工作流ID
        task_id = await self.add_workflow(workflow_id, workflow_data)
        return task_id
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        try:
            task_data = asyncio.run(self.get_task_status(job_id))
            if not task_data:
                return {
                    "job_id": job_id,
                    "status": "not_found",
                    "result": None,
                    "error": "Task not found"
                }
            
            # 转换为旧接口格式
            result = None
            if task_data['status'] == 'completed':
                # 收集所有节点的结果
                result = {}
                for node_id, node_status in task_data.get('node_task_statuses', {}).items():
                    if node_status['result']:
                        result[node_id] = node_status['result']
            
            return {
                "job_id": job_id,
                "status": task_data['status'],
                "result": result,
                "error": task_data.get('error')
            }
        except Exception as e:
            logger.error(f"Error getting job status: {str(e)}")
            return {
                "job_id": job_id,
                "status": "error",
                "result": None,
                "error": str(e)
            }
    
    def get_queue_info(self) -> Dict[str, Any]:
        """获取队列信息"""
        stats = self.get_statistics()
        return {
            "queued": stats.get('pending', 0),
            "started": stats.get('running', 0),
            "finished": stats.get('completed', 0),
            "failed": stats.get('failed', 0),
            "redis_available": False  # 使用ExecutionQueue，不需要Redis
        }
    
    def get_queue_tasks(self) -> Dict[str, Any]:
        """获取队列中的所有任务"""
        queued_tasks = [task_id for task_id, data in self.tasks.items() if data['status'] == 'queued']
        started_tasks = [task_id for task_id, data in self.tasks.items() if data['status'] == 'running']
        finished_tasks = [task_id for task_id, data in self.tasks.items() if data['status'] == 'completed']
        failed_tasks = [task_id for task_id, data in self.tasks.items() if data['status'] == 'failed']
        
        return {
            "queued": queued_tasks,
            "started": started_tasks,
            "finished": finished_tasks,
            "failed": failed_tasks,
            "redis_available": False
        }

# 任务队列模块实现
class TaskQueueModule(Module):
    def __init__(self):
        self.metadata = ModuleMetadata(
            id="task_queue",
            name="Task Queue Module",
            version="1.0.0",
            description="Task queue management module for workflow execution",
            dependencies=["workflow"]
        )
        self.workflow_manager = None
        self.task_queue_manager = None
    
    async def activate(self):
        logger.info(f"Activating {self.metadata.name} (v{self.metadata.version})")
        
        # 获取工作流模块API
        from core.module.module_manager import module_manager
        workflow_module_api = module_manager.get_module_api('workflow')
        if not workflow_module_api:
            raise Exception("Workflow module not found")
        
        # 创建任务队列管理器
        self.task_queue_manager = TaskQueueManager(workflow_module_api['workflow_manager'])
        logger.info(f"{self.metadata.name} activated successfully")
    
    async def deactivate(self):
        logger.info(f"Deactivating {self.metadata.name}")
        # 清理资源
        if self.task_queue_manager:
            await self.task_queue_manager.stop()
        logger.info(f"{self.metadata.name} deactivated successfully")
    
    def get_api(self):
        if not self.task_queue_manager:
            raise Exception("Task queue manager not initialized")
        return TaskQueueModuleAPI(self.task_queue_manager)

# 注册任务队列模块
module_manager.register_module(TaskQueueModule())
