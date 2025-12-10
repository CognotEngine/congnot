import os
import sys
import importlib.util
from typing import Dict, Any, Optional, Callable
from .base_node import BaseNode
from .node_registry import register_node

# Add AI node system to the path
AI_NODE_PATH = "f:\goting\Cognot\AI-Nodes-master\AI-Nodes-master"
sys.path.insert(0, AI_NODE_PATH)

class AINodeAdapter:
    """AI节点适配器，将AI节点转换为Cognot节点格式"""
    
    def __init__(self):
        self.ai_nodes = {}
        self.load_ai_nodes()
    
    def load_ai_nodes(self):
        """加载AI节点"""
        try:
            # 加载AI节点模块
            import sys
            ai_node_path = "f:\goting\Cognot\AI-Nodes-master\AI-Nodes-master"
            if ai_node_path not in sys.path:
                sys.path.insert(0, ai_node_path)
            
            import nodes as ai_nodes
            
            # 确保AI节点映射已初始化
            if not hasattr(ai_nodes, 'NODE_CLASS_MAPPINGS'):
                print("NODE_CLASS_MAPPINGS not found in nodes module")
                # 尝试手动初始化
                from nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
            else:
                NODE_CLASS_MAPPINGS = ai_nodes.NODE_CLASS_MAPPINGS
                NODE_DISPLAY_NAME_MAPPINGS = ai_nodes.NODE_DISPLAY_NAME_MAPPINGS
            
            # 获取所有AI节点
            for node_name, node_class in NODE_CLASS_MAPPINGS.items():
                self.ai_nodes[node_name] = {
                    "class": node_class,
                    "display_name": NODE_DISPLAY_NAME_MAPPINGS.get(node_name, node_name)
                }
            
            print(f"Successfully loaded {len(self.ai_nodes)} AI nodes")
        except Exception as e:
            print(f"Failed to load AI nodes: {e}")
            import traceback
            traceback.print_exc()
    
    def convert_ai_type(self, ai_type):
        """将AI类型转换为Cognot类型"""
        if isinstance(ai_type, tuple):
            # 处理AI的类型定义，如 ("STRING", {"multiline": True})
            # 递归处理第一个元素，因为它可能是列表
            base_type = self.convert_ai_type(ai_type[0])
            return base_type
        elif isinstance(ai_type, str):
            return ai_type.lower()
        elif isinstance(ai_type, list):
            # 处理列表类型，如 ["STRING", "INT"]
            if len(ai_type) > 0:
                # 如果列表非空，递归处理第一个元素
                return self.convert_ai_type(ai_type[0])
            else:
                return "any"
        else:
            return "any"
    
    def create_cognot_node_from_ai(self, node_name: str):
        """将AI节点转换为Cognot节点"""
        if node_name not in self.ai_nodes:
            print(f"AI node {node_name} not found")
            return None
        
        ai_node = self.ai_nodes[node_name]
        node_class = ai_node["class"]
        display_name = ai_node["display_name"]
        
        try:
            # 获取节点的输入类型
            input_types = node_class.INPUT_TYPES()
            
            # 处理必填输入
            required_inputs = input_types.get("required", {})
            
            # 获取节点的输出类型
            output_types = getattr(node_class, "RETURN_TYPES", ())
            output_tooltips = getattr(node_class, "OUTPUT_TOOLTIPS", [])
            
            # 获取节点的功能函数
            function_name = getattr(node_class, "FUNCTION", "__call__")
            node_function = getattr(node_class, function_name)
            
            # 创建Cognot节点输入定义
            cognot_inputs = {}
            for input_name, input_type in required_inputs.items():
                cognot_inputs[input_name] = self.convert_ai_type(input_type)
            
            # 创建Cognot节点输出定义
            cognot_outputs = {}
            for i, output_type in enumerate(output_types):
                output_name = f"output_{i+1}"
                tooltip = output_tooltips[i] if i < len(output_tooltips) else f"Output {i+1}"
                cognot_outputs[output_name] = {
                    "type": self.convert_ai_type(output_type),
                    "tooltip": tooltip
                }
            
            # 创建节点描述
            description = getattr(node_class, "DESCRIPTION", f"AI {display_name} node")
            
            # 创建节点类别
            category = getattr(node_class, "CATEGORY", "ai")
            
            # 创建适配器类，将AI节点包装为Cognot节点
            class AINodeAdapterWrapper(BaseNode):
                """AI节点适配器类"""
                
                def __init__(self):
                    super().__init__()
                    self.ai_node_instance = node_class()
                    
                def __call__(self, **kwargs):
                    """调用AI节点"""
                    try:
                        # 调用AI节点的函数
                        result = getattr(self.ai_node_instance, function_name)(**kwargs)
                        
                        # 转换结果格式
                        if isinstance(result, tuple):
                            return {f"output_{i+1}": value for i, value in enumerate(result)}
                        else:
                            return {"output_1": result}
                    except Exception as e:
                        print(f"Error calling AI node {node_name}: {e}")
                        import traceback
                        traceback.print_exc()
                        raise
            
            # 注册到Cognot节点注册表
            register_node(
                name=node_name,
                description=description,
                category=category,
                icon="ai"
            )(AINodeAdapterWrapper)
            
            print(f"Successfully converted AI node: {display_name} -> {node_name}")
            return True
            
        except Exception as e:
            print(f"Failed to convert AI node {node_name}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def convert_all_nodes(self):
        """转换所有AI节点"""
        success_count = 0
        total_count = len(self.ai_nodes)
        
        for node_name in self.ai_nodes:
            if self.create_cognot_node_from_ai(node_name):
                success_count += 1
        
        print(f"Conversion complete: {success_count}/{total_count} nodes converted successfully")
        return success_count

# 创建全局适配器实例
ai_node_adapter = AINodeAdapter()
