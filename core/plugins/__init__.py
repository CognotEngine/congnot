# 插件系统入口

from core.module.plugin_manager import PluginManager, plugin_manager

# 初始化插件管理器
def initialize_plugins():
    """
    初始化插件系统，加载所有插件
    """
    # 添加插件目录
    plugin_manager.add_plugin_dir("core/plugins")
    
    return plugin_manager


__all__ = ["PluginManager", "plugin_manager", "initialize_plugins"]
