# 核心模块系统

from .module_manager import ModuleManager, module_manager
from .module_registrar import register_module, register_and_activate_module
from .module_interface import Module, ModuleMetadata
from .plugin_manager import PluginManager, plugin_manager

# 导入模块
import core.modules.workflow
import core.modules.task_queue

__all__ = [
    'ModuleManager',
    'module_manager',
    'register_module',
    'register_and_activate_module',
    'Module',
    'ModuleMetadata',
    'PluginManager',
    'plugin_manager'
]
