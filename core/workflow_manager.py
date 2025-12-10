import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WorkflowManager:
    """工作流管理器，用于验证工作流数据"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_workflow(self, workflow_data: Dict[str, Any]) -> bool:
        """验证工作流数据是否有效
        
        Args:
            workflow_data: 工作流数据字典
            
        Returns:
            bool: 工作流数据是否有效
        """
        try:
            # 检查工作流的基本结构
            if not isinstance(workflow_data, dict):
                self.logger.error("Workflow data must be a dictionary")
                return False
            
            # 检查是否包含nodes字段
            if 'nodes' not in workflow_data:
                self.logger.error("Workflow data must contain 'nodes' field")
                return False
            
            if not isinstance(workflow_data['nodes'], list):
                self.logger.error("'nodes' field must be a list")
                return False
            
            # 检查是否包含edges字段（如果有）
            if 'edges' in workflow_data and not isinstance(workflow_data['edges'], list):
                self.logger.error("'edges' field must be a list")
                return False
            
            # 验证每个节点
            for node in workflow_data['nodes']:
                if not self._validate_node(node):
                    return False
            
            # 验证每个边（如果有）
            if 'edges' in workflow_data:
                for edge in workflow_data['edges']:
                    if not self._validate_edge(edge):
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating workflow: {e}")
            return False
    
    def _validate_node(self, node: Dict[str, Any]) -> bool:
        """验证单个节点是否有效"""
        if not isinstance(node, dict):
            self.logger.error("Node must be a dictionary")
            return False
        
        # 节点必须包含id和type
        if 'id' not in node:
            self.logger.error("Node must contain 'id' field")
            return False
        
        if 'type' not in node:
            self.logger.error("Node must contain 'type' field")
            return False
        
        return True
    
    def _validate_edge(self, edge: Dict[str, Any]) -> bool:
        """验证单个边是否有效"""
        if not isinstance(edge, dict):
            self.logger.error("Edge must be a dictionary")
            return False
        
        # 边必须包含source和target
        if 'source' not in edge:
            self.logger.error("Edge must contain 'source' field")
            return False
        
        if 'target' not in edge:
            self.logger.error("Edge must contain 'target' field")
            return False
        
        return True