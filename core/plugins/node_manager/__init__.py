# 节点管理器插件

import logging
from typing import Any, Dict, Optional, List
from core.module.module_interface import Module, ModuleMetadata
from core.node_registry import NodeRegistry
from core.workflow_validator import WorkflowValidator
import asyncio

logger = logging.getLogger(__name__)

# 插件元数据
METADATA = ModuleMetadata(
    id="node_manager",
    name="Node Manager",
    version="1.0.0",
    description="节点管理、依赖安装和工作流校验插件",
    dependencies=None
)


class NodeManagerPlugin(Module):
    """
    节点管理器插件，集成节点管理、依赖安装和工作流校验功能
    """
    def __init__(self, metadata: ModuleMetadata):
        super().__init__(metadata)
        self._node_registry = NodeRegistry()
        self._workflow_validator = WorkflowValidator(self._node_registry)
        
    async def activate(self) -> None:
        """
        激活插件，初始化节点管理器
        """
        logger.info("激活节点管理器插件...")
        # 加载已注册的节点
        await asyncio.to_thread(self._node_registry.load_registered_nodes)
        logger.info("节点管理器插件激活成功")
        
    async def deactivate(self) -> None:
        """
        停用插件
        """
        logger.info("停用节点管理器插件...")
        # 清理资源
        logger.info("节点管理器插件停用成功")
        
    def get_api(self) -> Dict[str, Any]:
        """
        获取插件API，暴露节点管理、依赖安装和工作流校验功能
        """
        return {
            # 节点注册功能
            "register_node": self._node_registry.register_node,
            "get_node_metadata": self._node_registry.get_node_metadata,
            "get_all_nodes": self._node_registry.get_all_nodes,
            "get_node_by_id": self._node_registry.get_node_by_id,
            "remove_node": self._node_registry.remove_node,
            
            # 工作流校验功能
            "validate_workflow": self._workflow_validator.validate,
            "get_missing_nodes": self._workflow_validator.get_missing_nodes,
            
            # 第三方节点管理功能
            "add_third_party_repo": self._node_registry.add_third_party_repo,
            "remove_third_party_repo": self._node_registry.remove_third_party_repo,
            "get_third_party_repos": self._node_registry.get_third_party_repos,
            "install_third_party_nodes": self._node_registry.install_third_party_nodes,
            "uninstall_third_party_nodes": self._node_registry.uninstall_third_party_nodes,
            "load_custom_nodes_from_dir": self._node_registry.load_custom_nodes_from_dir,
        }


# 创建插件实例
node_manager_plugin = NodeManagerPlugin(METADATA)
