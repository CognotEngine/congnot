import sys
import os
import json
import asyncio
from typing import Dict, Any, List

# 添加AI工作流系统路径
AI_WORKFLOW_PATH = "f:\\goting\\Cognot\\AI-Workflow-master\\AI-Workflow-master"
sys.path.insert(0, AI_WORKFLOW_PATH)

class AIWorkflowExecutor:
    """AI工作流执行引擎集成接口"""
    
    def __init__(self):
        self.init_ai_workflow()
    
    def init_ai_workflow(self):
        """初始化AI工作流执行环境"""
        try:
            # 加载AI工作流的必要模块
            import nodes as ai_nodes
            import execution as ai_execution
            import folder_paths as ai_folder_paths
            
            # 初始化模型路径
            ai_folder_paths.folder_names_and_paths["checkpoints"] = ([os.path.join(AI_WORKFLOW_PATH, "models", "checkpoints")], [".ckpt", ".safetensors"])
            ai_folder_paths.folder_names_and_paths["vae"] = ([os.path.join(AI_WORKFLOW_PATH, "models", "vae")], [".ckpt", ".safetensors"])
            ai_folder_paths.folder_names_and_paths["lora"] = ([os.path.join(AI_WORKFLOW_PATH, "models", "loras")], [".ckpt", ".safetensors"])
            
            self.ai_nodes = ai_nodes
            self.ai_execution = ai_execution
            self.ai_folder_paths = ai_folder_paths
            
            print("AI workflow execution environment initialized successfully")
        except Exception as e:
            print(f"Failed to initialize AI workflow execution environment: {e}")
            import traceback
            traceback.print_exc()
    
    def convert_cognot_workflow_to_ai_format(self, cognot_workflow: Dict[str, Any]) -> Dict[str, Any]:
        """将Cognot工作流转换为AI工作流格式"""
        try:
            # 提取Cognot工作流中的节点和边
            nodes = cognot_workflow.get("nodes", [])
            edges = cognot_workflow.get("edges", [])
            
            # 转换为AI工作流格式
            ai_workflow = {}
            ai_nodes = {}
            
            # 首先创建所有节点
            for i, node in enumerate(nodes):
                node_id = node.get("id", f"node_{i}")
                node_type = node.get("type", "")
                position = node.get("position", {"x": 0, "y": 0})
                
                # 获取节点的输入配置
                inputs = node.get("inputs", {})
                
                # 创建AI节点格式
                ai_node = {
                    "id": node_id,
                    "class_type": node_type,
                    "pos_x": position["x"],
                    "pos_y": position["y"],
                    "inputs": {}
                }
                
                # 处理节点输入
                for input_name, input_value in inputs.items():
                    if isinstance(input_value, dict) and "nodeId" in input_value and "output" in input_value:
                        # 处理连接类型输入
                        ai_node["inputs"][input_name] = [
                            input_value["nodeId"],  # 源节点ID
                            input_value["output"]   # 源节点输出索引
                        ]
                    else:
                        # 处理值类型输入
                        ai_node["inputs"][input_name] = input_value
                
                ai_nodes[node_id] = ai_node
            
            # 添加节点到工作流
            ai_workflow["nodes"] = ai_nodes
            
            print("Successfully converted Cognot workflow to AI workflow format")
            return ai_workflow
        except Exception as e:
            print(f"Failed to convert Cognot workflow to AI workflow format: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    async def execute_ai_workflow(self, ai_workflow: Dict[str, Any]) -> Dict[str, Any]:
        """执行AI工作流"""
        try:
            # 创建执行上下文
            from ai_execution.graph import GraphBuilder
            from ai_execution.execution import GraphExecutionContext
            
            # 构建执行图
            graph_builder = GraphBuilder(ai_workflow)
            execution_list = graph_builder.build_execution_list()
            
            # 创建执行上下文
            execution_context = GraphExecutionContext(execution_list)
            
            # 执行工作流
            await execution_context.execute()
            
            # 获取执行结果
            results = execution_context.get_results()
            
            print("AI workflow executed successfully")
            return {
                "status": "success",
                "results": results
            }
        except Exception as e:
            print(f"Failed to execute AI workflow: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def execute_cognot_workflow(self, cognot_workflow: Dict[str, Any]) -> Dict[str, Any]:
        """执行Cognot工作流（内部转换为AI工作流格式）"""
        # 转换工作流格式
        ai_workflow = self.convert_cognot_workflow_to_ai_format(cognot_workflow)
        
        if not ai_workflow:
            return {
                "status": "error",
                "error": "Failed to convert workflow to AI workflow format"
            }
        
        # 执行AI工作流
        return await self.execute_ai_workflow(ai_workflow)

# 创建全局执行器实例
ai_workflow_executor = AIWorkflowExecutor()
