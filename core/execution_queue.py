

import asyncio
import logging
import heapq
from typing import Dict, List, Optional, Callable, Any, Tuple
from enum import Enum
from uuid import uuid4

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    
    PENDING = "pending"  
    RUNNING = "running"  
    COMPLETED = "completed"  
    FAILED = "failed"  

class Task:
    
    
    def __init__(self,
                 task_id: Optional[str] = None,
                 node_id: str = "",
                 node_type: str = "",
                 inputs: Dict[str, Any] = None,
                 dependencies: List[str] = None,
                 priority: int = 50):
        
        self.task_id = task_id or str(uuid4())
        self.node_id = node_id
        self.node_type = node_type
        self.inputs = inputs or {}
        self.dependencies = dependencies or []
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.execution_time: Optional[float] = None
        
    def __str__(self) -> str:
        return f"Task(id={self.task_id}, node={self.node_id}, status={self.status.value})"

class ExecutionQueue:
    
    
    def __init__(self,
                 max_workers: int = 4,
                 on_task_start: Optional[Callable] = None,
                 on_task_complete: Optional[Callable] = None,
                 on_task_fail: Optional[Callable] = None,
                 on_queue_updated: Optional[Callable] = None):
        """初始化队列
        
        Args:
            max_workers: 最大工作线程数
            on_task_start: 任务开始回调
            on_task_complete: 任务完成回调
            on_task_fail: 任务失败回调
            on_queue_updated: 队列更新回调
        """
        self.max_workers = max_workers
        self.tasks: Dict[str, Task] = {}
        self.priority_queue: List[Tuple[int, int, Task]] = []  # 使用堆队列实现优先级
        self.priority_counter = 0  # 用于保持插入顺序
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: int = 0
        self.completed_tasks: int = 0
        self.failed_tasks: int = 0
        
        # 优化依赖跟踪：task_id -> [依赖此任务的任务列表]
        self.dependency_graph: Dict[str, List[str]] = {}
        
        # 回调函数
        self.on_task_start = on_task_start
        self.on_task_complete = on_task_complete
        self.on_task_fail = on_task_fail
        self.on_queue_updated = on_queue_updated
        
        # 事件和状态
        self.is_running = False
        self.all_tasks_completed = asyncio.Event()
        self.workers = []
    
    def add_task(self, task: Task, priority: int = 0) -> str:
        """添加任务到队列
        
        Args:
            task: Task对象
            priority: 优先级，数字越小优先级越高
            
        Returns:
            任务ID
        """
        self.tasks[task.task_id] = task
        
        # 构建依赖图
        for dep in task.dependencies:
            if dep not in self.dependency_graph:
                self.dependency_graph[dep] = []
            self.dependency_graph[dep].append(task.task_id)
        
        # 检查依赖是否满足
        if not task.dependencies or all(dep in self.tasks and self.tasks[dep].status == TaskStatus.COMPLETED for dep in task.dependencies):
            # 将任务加入优先级队列
            heapq.heappush(self.priority_queue, (priority, self.priority_counter, task))
            self.priority_counter += 1
            
            if self.on_queue_updated:
                self.on_queue_updated()
        
        return task.task_id
        
    async def start(self) -> None:
        """启动队列处理"""
        if self.is_running:
            return
            
        self.is_running = True
        self.all_tasks_completed.clear()
        
        # 将所有无依赖的任务加入优先级队列
        for task in self.tasks.values():
            if not task.dependencies:
                task.status = TaskStatus.PENDING
                heapq.heappush(self.priority_queue, (0, self.priority_counter, task))
                self.priority_counter += 1
        
        # 创建工作线程
        self.workers = [asyncio.create_task(self.worker()) for _ in range(self.max_workers)]
        
        if self.on_queue_updated:
            self.on_queue_updated()
    
    async def stop(self) -> None:
        """停止队列处理"""
        self.is_running = False
        
        # 取消所有工作线程
        for worker in self.workers:
            worker.cancel()
        
        # 等待所有工作线程结束
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers = []
    
    async def wait_until_complete(self) -> None:
        """等待所有任务完成"""
        await self.all_tasks_completed.wait()
    
    async def worker(self) -> None:
        
        while self.is_running:
            try:
                # 从优先级队列获取任务
                if not self.priority_queue:
                    await asyncio.sleep(0.1)
                    continue
                
                _, _, task = heapq.heappop(self.priority_queue)
                await self.execute_task(task)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(1)  # 避免错误循环
    
    async def execute_task(self, task: Task) -> None:
        
        if task.status != TaskStatus.PENDING:
            return
        
        try:
            
            self.running_tasks += 1
            task.status = TaskStatus.RUNNING
            
            
            if self.on_task_start:
                await self.on_task_start(task.task_id, task.node_id, task.node_type)
            
            logger.info(f"Starting task execution: {task}")
            
            # 执行任务的实际逻辑（可以被继承类重写）
            result = await self._execute_task_logic(task)
            
            # 更新任务状态
            task.status = TaskStatus.COMPLETED
            task.result = result
            
            logger.info(f"Task execution completed: {task}")
            
            
            if self.on_task_complete:
                await self.on_task_complete(task.task_id, task.node_id, task.result, task.execution_time)
            
            
            self.completed_tasks += 1
            
            
            await self._check_dependencies(task.task_id)
            
        except Exception as e:
            
            task.status = TaskStatus.FAILED
            task.error = str(e)
            
            logger.error(f"Task execution failed: {task}, error: {e}")
            
            
            if self.on_task_fail:
                await self.on_task_fail(task.task_id, task.node_id, str(e))
            
            
            self.failed_tasks += 1
        finally:
            self.running_tasks -= 1
            
            # 通知队列更新
            if self.on_queue_updated:
                self.on_queue_updated()
            
            if self._all_tasks_processed():
                self.all_tasks_completed.set()
    
    async def _check_dependencies(self, completed_task_id: str) -> None:
        """检查是否有依赖于已完成任务的任务可以执行
        
        使用依赖图优化：只检查直接依赖于已完成任务的任务
        """
        # 获取所有依赖于已完成任务的任务
        dependent_tasks = self.dependency_graph.get(completed_task_id, [])
        
        for task_id in dependent_tasks:
            task = self.tasks.get(task_id)
            if task and task.status == TaskStatus.PENDING:
                # 检查该任务的所有依赖是否都已完成
                if all(dep in self.tasks and self.tasks[dep].status == TaskStatus.COMPLETED for dep in task.dependencies):
                    # 将任务加入优先级队列
                    heapq.heappush(self.priority_queue, (0, self.priority_counter, task))
                    self.priority_counter += 1
    
    async def _execute_task_logic(self, task: Task) -> Dict[str, Any]:
        """任务执行的实际逻辑（使用插件系统执行节点函数）
        
        Args:
            task: 要执行的任务
            
        Returns:
            任务执行结果
        """
        from core.module.plugin_manager import plugin_manager
        
        # 获取节点管理器插件API
        node_manager_api = plugin_manager.get_module_api('node_manager')
        if not node_manager_api:
            raise ValueError(f"Node manager plugin not activated")
        
        # 获取节点函数
        node_function = node_manager_api.get_node_function(task.node_type)
        if not node_function:
            raise ValueError(f"Node function not found for node type: {task.node_type}")
        
        # 执行节点函数
        result = node_function(**task.inputs)
        
        # 如果结果是异步函数，等待执行完成
        if hasattr(result, '__await__'):
            result = await result
        
        return result
    
    def _all_tasks_processed(self) -> bool:
        """检查是否所有任务都已处理"""
        processed = sum(1 for task in self.tasks.values() 
                       if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED])
        return processed == len(self.tasks)
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        
        task = self.tasks.get(task_id)
        return task.status if task else None
    
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        
        task = self.tasks.get(task_id)
        return task.result if task and task.status == TaskStatus.COMPLETED else None
    
    def get_statistics(self) -> Dict[str, int]:
        
        return {
            "total": len(self.tasks),
            "running": self.running_tasks,
            "completed": self.completed_tasks,
            "failed": self.failed_tasks,
            "pending": len(self.tasks) - self.completed_tasks - self.failed_tasks - self.running_tasks
        }

def create_execution_queue(max_workers: int = 4,
                          on_task_start: Optional[Callable] = None,
                          on_task_complete: Optional[Callable] = None,
                          on_task_fail: Optional[Callable] = None,
                          on_queue_updated: Optional[Callable] = None) -> ExecutionQueue:
    
    return ExecutionQueue(
        max_workers=max_workers,
        on_task_start=on_task_start,
        on_task_complete=on_task_complete,
        on_task_fail=on_task_fail,
        on_queue_updated=on_queue_updated
    )

async def test_execution_queue():
    
    
    
    queue = create_execution_queue(max_workers=2)
    
    
    async def on_start(task_id, node_id, node_type):
        print(f"Task started: {task_id} (node: {node_id}, type: {node_type})")
    
    async def on_complete(task_id, node_id, result, execution_time):
        print(f"Task completed: {task_id} (node: {node_id}, result: {result}, execution time: {execution_time}s)")
    
    async def on_fail(task_id, node_id, error):
        print(f"Task failed: {task_id} (node: {node_id}, error: {error})")
    
    def on_queue_updated():
        print(f"Queue updated: {queue.get_statistics()}")
    
    
    queue.on_task_start = on_start
    queue.on_task_complete = on_complete
    queue.on_task_fail = on_fail
    queue.on_queue_updated = on_queue_updated
    
    
    task1 = Task(node_id="node1", node_type="input", inputs={"value": "Hello"})
    task2 = Task(node_id="node2", node_type="input", inputs={"value": "World"})
    task3 = Task(node_id="node3", node_type="processing", 
                inputs={"a": {"$ref": "task1.result"}, "b": {"$ref": "task2.result"}},
                dependencies=[task1.task_id, task2.task_id])
    task4 = Task(node_id="node4", node_type="output", 
                inputs={"value": {"$ref": "task3.result"}},
                dependencies=[task3.task_id])
    
    queue.add_task(task1)
    queue.add_task(task2)
    queue.add_task(task3)
    queue.add_task(task4)
    
    
    print("Starting task processing...")
    await queue.start()
    await queue.wait_until_complete()
    await queue.stop()
    
    
    print(f"\nExecution statistics: {queue.get_statistics()}")
    
    
    print("\nAll task results:")
    for task_id, task in queue.tasks.items():
        print(f"  {task_id}: status={task.status.value}, result={task.result}")

if __name__ == "__main__":
    
    asyncio.run(test_execution_queue())
