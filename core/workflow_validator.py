# 工作流验证器

from typing import Dict, List, Optional
from core.node_registry import NodeRegistry


class WorkflowValidator:
    """
    工作流验证器，用于验证工作流中的节点是否都已安装
    """
    def __init__(self, node_registry: NodeRegistry):
        """
        初始化工作流验证器
        
        Args:
            node_registry: 节点注册表实例
        """
        self._node_registry = node_registry
    
    def validate(self, workflow: Dict[str, any]) -> List[str]:
        """
        验证工作流中使用的节点是否都已安装
        
        Args:
            workflow: 工作流数据
            
        Returns:
            缺失的节点类型列表
        """
        return self._node_registry.validate_workflow(workflow)
    
    def get_missing_nodes(self, workflow: Dict[str, any]) -> List[str]:
        """
        获取工作流中缺失的节点
        
        Args:
            workflow: 工作流数据
            
        Returns:
            缺失的节点类型列表
        """
        return self.validate(workflow)
    
    def is_valid(self, workflow: Dict[str, any]) -> bool:
        """
        检查工作流是否有效（所有节点都已安装）
        
        Args:
            workflow: 工作流数据
            
        Returns:
            如果所有节点都已安装则返回True，否则返回False
        """
        return len(self.validate(workflow)) == 0