

import asyncio
import logging
import time
from collections import deque
from typing import List, Dict, Any, Optional, Callable
from .graph_parser import Graph, Node
from .node_registry import get_node_function, get_node_rollback_function
from .execution_queue import ExecutionQueue, Task, TaskStatus, create_execution_queue

class TopologicalSorter:
    
    
    @staticmethod
    def kahn_sort(graph: Graph) -> List[str]:
        
        
        in_degree = {node_id: 0 for node_id in graph.nodes}
        for edge in graph.edges.values():
            in_degree[edge.target] += 1
        
        
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        
        
        topological_order = []
        while queue:
            node_id = queue.popleft()
            topological_order.append(node_id)
            
            
            outgoing_edges = graph.get_edges_from_node(node_id)
            for edge in outgoing_edges:
                in_degree[edge.target] -= 1
                if in_degree[edge.target] == 0:
                    queue.append(edge.target)
        
        
        if len(topological_order) != len(graph.nodes):
            raise ValueError("Graph contains a cycle, topological sort is not possible")
        
        return topological_order
    
    @staticmethod
    def dfs_sort(graph: Graph) -> List[str]:
        
        visited = {}
        topological_order = []
        cycle_detected = False
        
        
        for node_id in graph.nodes:
            visited[node_id] = 0
        
        def dfs(node_id: str) -> None:
            nonlocal cycle_detected
            
            if cycle_detected:
                return
            
            if visited[node_id] == 1:
                cycle_detected = True
                return
            
            if visited[node_id] == 2:
                return
            
            
            visited[node_id] = 1
            
            
            outgoing_edges = graph.get_edges_from_node(node_id)
            for edge in outgoing_edges:
                dfs(edge.target)
            
            
            visited[node_id] = 2
            
            topological_order.append(node_id)
        
        
        for node_id in graph.nodes:
            if visited[node_id] == 0:
                dfs(node_id)
        
        
        if cycle_detected:
            raise ValueError("Graph contains a cycle, topological sort is not possible")
        
        
        topological_order.reverse()
        return topological_order

class GraphExecutor:
    
    
    def __init__(self, topology_sorter: str = "kahn"):
        
        if topology_sorter == "kahn":
            self._topology_sort_func = TopologicalSorter.kahn_sort
        elif topology_sorter == "dfs":
            self._topology_sort_func = TopologicalSorter.dfs_sort
        else:
            raise ValueError(f"Unknown topology sorter: {topology_sorter}")
    
    def execute_graph(self, graph: Graph, on_node_start: Optional[Callable] = None, on_node_complete: Optional[Callable] = None) -> Dict[str, Dict[str, Any]]:
        
        
        topological_order = self._topology_sort_func(graph)
        
        
        results = {}
        
        
        executed_nodes = []
        
        try:
            
            for node_id in topological_order:
                node = graph.get_node(node_id)
                if not node:
                    continue
                
                
                if on_node_start:
                    on_node_start(node_id)
                
                
                input_values = self._resolve_node_inputs(graph, node, results)
                
                
                if node.type == "condition":
                    
                    condition_value = input_values.get("condition", False)
                    
                    
                    
                    node_func = get_node_function(node.type)
                    if not node_func:
                        raise ValueError(f"Node function not found for type: {node.type}")
                    
                    try:
                        output_values = node_func(**input_values)
                    except Exception as e:
                        raise RuntimeError(f"Error executing node {node_id} ({node.type}): {e}")
                    
                    
                    graph.update_node_outputs(node_id, output_values)
                    results[node_id] = output_values
                    
                    
                    executed_nodes.append(node_id)
                    
                    
                    if on_node_complete:
                        on_node_complete(node_id, output_values)
                    continue
                
                
                elif node.type in ["loop_start", "loop_end"]:
                    # 循环节点的处理尚未实现
                    # 这些节点在工作流中用于创建循环结构
                    pass
                
                
                node_func = get_node_function(node.type)
                if not node_func:
                    raise ValueError(f"Node function not found for type: {node.type}")
                
                try:
                    output_values = node_func(**input_values)
                except Exception as e:
                    raise RuntimeError(f"Error executing node {node_id} ({node.type}): {e}")
                
                
                graph.update_node_outputs(node_id, output_values)
                results[node_id] = output_values
                
                
                executed_nodes.append(node_id)
                
                
                if on_node_complete:
                    on_node_complete(node_id, output_values)
        
        except Exception as e:
            
            self._rollback_nodes(graph, executed_nodes, results)
            raise
        
        return results
        
    def _execute_branch(self, graph: Graph, branch_node_ids: List[str], results: Dict[str, Dict[str, Any]], 
                       on_node_start: Optional[Callable] = None, on_node_complete: Optional[Callable] = None) -> None:
        
        for node_id in branch_node_ids:
            if node_id in graph.nodes and node_id not in results:
                node = graph.get_node(node_id)
                if not node:
                    continue
                
                # 处理分支中的节点
                if on_node_start:
                    on_node_start(node_id)
                
                # 解析节点输入
                input_values = self._resolve_node_inputs(graph, node, results)
                
                # 获取节点执行函数
                node_func = get_node_function(node.type)
                if not node_func:
                    raise ValueError(f"Node function not found for type: {node.type}")
                
                try:
                    # 执行节点
                    output_values = node_func(**input_values)
                except Exception as e:
                    raise RuntimeError(f"Error executing node {node_id} ({node.type}): {e}")
                
                # 更新节点输出
                graph.update_node_outputs(node_id, output_values)
                results[node_id] = output_values
                
                # 调用节点完成回调
                if on_node_complete:
                    on_node_complete(node_id, output_values)
                
                
                node_func = get_node_function(node.type)
                if not node_func:
                    raise ValueError(f"Node function not found for type: {node.type}")
                
                try:
                    output_values = node_func(**input_values)
                except Exception as e:
                    raise RuntimeError(f"Error executing node {node_id} ({node.type}): {e}")
                
                
                graph.update_node_outputs(node_id, output_values)
                results[node_id] = output_values
                
                
                if on_node_complete:
                    on_node_complete(node_id, output_values)
    
    async def execute_graph_async(self, graph: Graph, max_workers: int = 4,
                                on_node_start: Optional[Callable] = None,
                                on_node_complete: Optional[Callable] = None,
                                on_node_fail: Optional[Callable] = None,
                                on_rollback_start: Optional[Callable] = None,
                                on_rollback_complete: Optional[Callable] = None) -> Dict[str, Dict[str, Any]]:
        
        
        topological_order = self._topology_sort_func(graph)
        
        
        queue = create_execution_queue(max_workers=max_workers)
        
        
        results = {}
        
        
        results_lock = asyncio.Lock()
        
        
        executed_nodes = []
        executed_nodes_lock = asyncio.Lock()
        
        
        async def task_start_callback(task_id: str, node_id: str, node_type: str):
            if on_node_start:
                on_node_start(node_id)
        
        async def task_complete_callback(task_id: str, node_id: str, result: Dict[str, Any], execution_time: float):
            async with results_lock:
                node_outputs = result["outputs"]
                results[node_id] = node_outputs
                graph.update_node_outputs(node_id, node_outputs)
            
            
            async with executed_nodes_lock:
                executed_nodes.append(node_id)
            
            if on_node_complete:
                on_node_complete(node_id, node_outputs)
        
        async def task_fail_callback(task_id: str, node_id: str, error: str):
            if on_node_fail:
                on_node_fail(node_id, error)
        
        
        queue.on_task_start = task_start_callback
        queue.on_task_complete = task_complete_callback
        queue.on_task_fail = task_fail_callback
        
        
        task_dependencies = {}
        for node_id in topological_order:
            
            incoming_edges = graph.get_edges_to_node(node_id)
            
            dependencies = [edge.source for edge in incoming_edges]
            task_dependencies[node_id] = dependencies
        
        
        for node_id in topological_order:
            node = graph.get_node(node_id)
            if not node:
                continue
            
            task = Task(
                task_id=f"task_{node_id}",
                node_id=node_id,
                node_type=node.type,
                inputs=node.inputs,
                dependencies=[f"task_{dep_id}" for dep_id in task_dependencies[node_id]]
            )
            queue.add_task(task)
        
        
        async def custom_execute_task(task: Task) -> None:
            if task.status != TaskStatus.PENDING:
                return
            
            try:
                
                queue.running_tasks += 1
                task.status = TaskStatus.RUNNING
                
                
                if queue.on_task_start:
                    await queue.on_task_start(task.task_id, task.node_id, task.node_type)
                
                
                node = graph.get_node(task.node_id)
                if not node:
                    raise ValueError(f"Node {task.node_id} not found")
                
                
                async with results_lock:
                    input_values = self._resolve_node_inputs(graph, node, results)
                
                
                node_func = get_node_function(node.type)
                if not node_func:
                    raise ValueError(f"Node function not found for type: {node.type}")
                
                
                # 计算实际执行时间
                start_time = time.time()
                output_values = node_func(**input_values)
                end_time = time.time()
                execution_time = end_time - start_time
                
                task.status = TaskStatus.COMPLETED
                task.result = {"outputs": output_values}
                task.execution_time = execution_time
                
                
                if queue.on_task_complete:
                    await queue.on_task_complete(task.task_id, task.node_id, task.result, task.execution_time)
                
                
                queue.completed_tasks += 1
                
                
                await queue._check_dependencies(task.task_id)
                
            except Exception as e:
                
                task.status = TaskStatus.FAILED
                task.error = str(e)
                
                
                if queue.on_task_fail:
                    await queue.on_task_fail(task.task_id, task.node_id, str(e))
                
                
                queue.failed_tasks += 1
                
                
                async with executed_nodes_lock:
                    current_executed_nodes = list(executed_nodes)
                await self._rollback_nodes_async(graph, current_executed_nodes, results, results_lock)
            finally:
                queue.running_tasks -= 1
                
                
                if queue._all_tasks_processed():
                    queue.all_tasks_completed.set()
        
        
        queue.execute_task = custom_execute_task
        
        
        await queue.process_tasks()
        
        return results
    
    def _rollback_nodes(self, graph: Graph, executed_nodes: List[str], results: Dict[str, Dict[str, Any]]) -> None:
        
        
        for node_id in reversed(executed_nodes):
            node = graph.get_node(node_id)
            if not node:
                continue
            
            
            rollback_func = get_node_rollback_function(node.type)
            if not rollback_func:
                continue  
            
            
            input_values = self._resolve_node_inputs(graph, node, results)
            output_values = results.get(node_id, {})
            
            
            try:
                rollback_func(inputs=input_values, outputs=output_values)
            except Exception as e:
                logging.error(f"Error rolling back node {node_id} ({node.type}): {e}")
    
    async def _rollback_nodes_async(self, graph: Graph, executed_nodes: List[str], results: Dict[str, Dict[str, Any]], results_lock: asyncio.Lock) -> None:
        
        
        for node_id in reversed(executed_nodes):
            node = graph.get_node(node_id)
            if not node:
                continue
            
            
            rollback_func = get_node_rollback_function(node.type)
            if not rollback_func:
                continue  
            
            
            async with results_lock:
                input_values = self._resolve_node_inputs(graph, node, results)
                output_values = results.get(node_id, {})
            
            
            try:
                rollback_func(inputs=input_values, outputs=output_values)
            except Exception as e:
                logging.error(f"Error rolling back node {node_id} ({node.type}): {e}")
    
    def _resolve_node_inputs(self, graph: Graph, node: Node, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        
        resolved_inputs = {}
        
        for input_name, input_value in node.inputs.items():
            
            if isinstance(input_value, dict) and "$ref" in input_value:
                ref_str = input_value["$ref"]
                
                
                try:
                    source_node_id, source_output = ref_str.split(".outputs.")
                except ValueError:
                    raise ValueError(f"Invalid reference format: {ref_str}. Expected format: 'node_id.outputs.output_name'")
                
                
                if source_node_id not in results:
                    raise RuntimeError(f"Source node {source_node_id} not yet executed")
                
                
                if source_output not in results[source_node_id]:
                    raise ValueError(f"Output {source_output} not found in node {source_node_id}")
                
                
                resolved_inputs[input_name] = results[source_node_id][source_output]
            else:
                
                resolved_inputs[input_name] = input_value
        
        return resolved_inputs

def execute_graph(
    graph: Graph,
    topology_sorter: str = "kahn",
    on_node_start: Optional[Callable] = None,
    on_node_complete: Optional[Callable] = None
) -> Dict[str, Dict[str, Any]]:
    
    executor = GraphExecutor(topology_sorter=topology_sorter)
    return executor.execute_graph(graph, on_node_start, on_node_complete)

async def execute_graph_async(
    graph: Graph,
    topology_sorter: str = "kahn",
    max_workers: int = 4,
    on_node_start: Optional[Callable] = None,
    on_node_complete: Optional[Callable] = None,
    on_node_fail: Optional[Callable] = None
) -> Dict[str, Dict[str, Any]]:
    
    executor = GraphExecutor(topology_sorter=topology_sorter)
    return await executor.execute_graph_async(graph, max_workers, on_node_start, on_node_complete, on_node_fail)
