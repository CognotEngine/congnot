# 模块管理器

import logging
import asyncio
import os
import sys
import importlib.util
import subprocess
import pkg_resources
from typing import Dict, Any, Optional, Callable, List, Type, Awaitable
from enum import Enum
from .module_interface import Module, ModuleMetadata

logger = logging.getLogger(__name__)


class ModuleState(Enum):
    """
    模块状态枚举
    """
    UNLOADED = "unloaded"  # 未加载
    LOADING = "loading"    # 加载中
    LOADED = "loaded"      # 已加载
    ACTIVATING = "activating"  # 激活中
    ACTIVATED = "activated"    # 已激活
    FAILED = "failed"      # 加载失败


class ModuleLoadException(Exception):
    """
    模块加载异常
    """
    def __init__(self, module_id: str, message: str):
        self.module_id = module_id
        self.message = message
        super().__init__(f"Module {module_id} load failed: {message}")


class ModuleInstance:
    """
    模块实例包装类，用于管理模块状态和错误隔离
    """
    def __init__(self, module_id: str):
        self.module_id = module_id
        self.module: Optional[Module] = None
        self.state = ModuleState.UNLOADED
        self.error: Optional[Exception] = None
        self.load_attempts = 0
        self.last_error_time: Optional[float] = None


def _install_python_dependencies(dependencies: List[str]) -> None:
    """
    安装Python依赖
    """
    if not dependencies:
        return
    
    # 检查已安装的包
    installed = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    to_install = []
    
    for dep in dependencies:
        try:
            # 解析依赖字符串（支持版本规范）
            req = pkg_resources.Requirement.parse(dep)
            if req.key not in installed or installed[req.key] not in req:
                to_install.append(dep)
        except Exception:
            # 无法解析的依赖直接安装
            to_install.append(dep)
    
    if to_install:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + to_install)


def _discover_external_modules(plugins_dir: str = "plugins") -> List[str]:
    """
    发现外部模块
    """
    module_paths = []
    
    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
        return module_paths
    
    # 遍历plugins目录下的所有子文件夹
    for item in os.listdir(plugins_dir):
        item_path = os.path.join(plugins_dir, item)
        if os.path.isdir(item_path):
            # 查找标准入口文件
            entry_files = [
                os.path.join(item_path, "__init__.py"),
                os.path.join(item_path, "plugin.py")
            ]
            
            for entry_file in entry_files:
                if os.path.exists(entry_file):
                    module_paths.append(entry_file)
                    break
    
    return module_paths


def _import_module_from_path(module_path: str) -> Any:
    """
    从路径导入模块
    """
    module_name = os.path.basename(os.path.dirname(module_path))
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    return None


class ModuleManager:
    """
    模块管理器，负责加载和管理所有模块
    """
    def __init__(self):
        self._modules: Dict[str, ModuleInstance] = {}  # 模块实例字典
        self._module_loaders: Dict[str, Callable[[], Module]] = {}  # 模块加载器
        self._async_module_loaders: Dict[str, Callable[[], Awaitable[Module]]] = {}  # 异步模块加载器
        self._load_timeout: float = 30.0  # 默认加载超时时间（秒）
        self._max_retries: int = 3  # 默认最大重试次数
        self._retry_delay: float = 2.0  # 默认重试延迟（秒）

    def register_module_loader(self, module_id: str, loader: Callable[[], Module]) -> None:
        """
        注册模块加载器
        
        Args:
            module_id: 模块唯一标识符
            loader: 模块加载函数
        """
        self._module_loaders[module_id] = loader
        logger.info(f"Module loader registered: {module_id}")

    def register_async_module_loader(self, module_id: str, loader: Callable[[], Awaitable[Module]]) -> None:
        """
        注册异步模块加载器
        
        Args:
            module_id: 模块唯一标识符
            loader: 异步模块加载函数
        """
        self._async_module_loaders[module_id] = loader
        logger.info(f"Async module loader registered: {module_id}")

    def register_module(self, module: Module) -> None:
        """
        注册已实例化的模块
        
        Args:
            module: 模块实例
        """
        module_id = module.metadata.id
        module_instance = ModuleInstance(module_id)
        module_instance.module = module
        module_instance.state = ModuleState.LOADED
        self._modules[module_id] = module_instance
        logger.info(f"Module registered: {module_id}")

    async def load_module(self, module_id: str) -> Optional[Module]:
        """
        加载模块，支持超时控制和重试机制
        
        Args:
            module_id: 模块唯一标识符
            
        Returns:
            加载的模块实例，如果加载失败则返回None
        """
        # 获取或创建模块实例
        if module_id not in self._modules:
            self._modules[module_id] = ModuleInstance(module_id)
        
        module_instance = self._modules[module_id]
        
        # 检查模块是否已加载
        if module_instance.state in [ModuleState.LOADED, ModuleState.ACTIVATED, ModuleState.ACTIVATING]:
            return module_instance.module
        
        # 检查模块是否正在加载
        if module_instance.state == ModuleState.LOADING:
            # 等待加载完成
            await self._wait_for_module_state(module_id, [ModuleState.LOADED, ModuleState.FAILED])
            return module_instance.module if module_instance.state == ModuleState.LOADED else None
        
        # 检查是否达到最大重试次数
        if module_instance.load_attempts >= self._max_retries:
            logger.error(f"Max retries reached for module {module_id}, giving up")
            module_instance.state = ModuleState.FAILED
            return None
        
        # 开始加载模块
        module_instance.state = ModuleState.LOADING
        module_instance.load_attempts += 1
        
        try:
            # 尝试使用同步加载器
            if module_id in self._module_loaders:
                # 使用超时控制
                module = await asyncio.wait_for(
                    asyncio.to_thread(self._module_loaders[module_id]),
                    timeout=self._load_timeout
                )
                module_instance.module = module
                module_instance.state = ModuleState.LOADED
                logger.info(f"Module loaded synchronously: {module_id}")
                return module
            
            # 尝试使用异步加载器
            if module_id in self._async_module_loaders:
                # 使用超时控制
                module = await asyncio.wait_for(
                    self._async_module_loaders[module_id](),
                    timeout=self._load_timeout
                )
                module_instance.module = module
                module_instance.state = ModuleState.LOADED
                logger.info(f"Module loaded asynchronously: {module_id}")
                return module
            
            logger.error(f"Module loader not found for module: {module_id}")
            module_instance.state = ModuleState.FAILED
            module_instance.error = ModuleLoadException(module_id, "Module loader not found")
            return None
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout loading module {module_id}")
            module_instance.state = ModuleState.FAILED
            module_instance.error = ModuleLoadException(module_id, "Loading timed out")
            # 等待一段时间后允许重试
            await asyncio.sleep(self._retry_delay)
            return None
            
        except Exception as e:
            logger.error(f"Error loading module {module_id}: {e}")
            module_instance.state = ModuleState.FAILED
            module_instance.error = e
            # 等待一段时间后允许重试
            await asyncio.sleep(self._retry_delay)
            return None

    async def activate_module(self, module_id: str) -> bool:
        """
        激活模块，支持依赖检查增强和错误隔离
        
        Args:
            module_id: 模块唯一标识符
            
        Returns:
            如果模块激活成功则返回True，否则返回False
        """
        # 获取模块实例
        if module_id not in self._modules:
            logger.error(f"Module {module_id} not found")
            return False
        
        module_instance = self._modules[module_id]
        
        # 检查模块是否已激活
        if module_instance.state == ModuleState.ACTIVATED:
            return True
        
        # 检查模块是否正在激活
        if module_instance.state == ModuleState.ACTIVATING:
            # 等待激活完成
            await self._wait_for_module_state(module_id, [ModuleState.ACTIVATED, ModuleState.FAILED])
            return module_instance.state == ModuleState.ACTIVATED
        
        # 确保模块已加载
        if module_instance.state != ModuleState.LOADED:
            module = await self.load_module(module_id)
            if not module:
                logger.error(f"Failed to load module {module_id} before activation")
                return False
        
        # 开始激活模块
        module_instance.state = ModuleState.ACTIVATING
        
        try:
            module = module_instance.module
            if not module:
                raise ModuleLoadException(module_id, "Module instance is None")
            
            # 验证依赖模块
            if not await self._validate_dependencies(module):
                logger.error(f"Dependency validation failed for module {module_id}")
                module_instance.state = ModuleState.FAILED
                module_instance.error = ModuleLoadException(module_id, "Dependency validation failed")
                return False
            
            # 加载并激活依赖模块
            if module.metadata.dependencies:
                for dependency_id in module.metadata.dependencies:
                    if not await self.activate_module(dependency_id):
                        logger.error(f"Failed to activate dependency {dependency_id} for module {module_id}")
                        module_instance.state = ModuleState.FAILED
                        module_instance.error = ModuleLoadException(module_id, f"Dependency {dependency_id} activation failed")
                        return False
            
            # 安装Python依赖
            if module.metadata.python_dependencies:
                _install_python_dependencies(module.metadata.python_dependencies)
            
            # 调用模块激活函数（带超时控制）
            await asyncio.wait_for(module.activate(), timeout=self._load_timeout)
            
            # 标记模块为已激活
            module_instance.state = ModuleState.ACTIVATED
            logger.info(f"Module activated: {module_id}")
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout activating module {module_id}")
            module_instance.state = ModuleState.FAILED
            module_instance.error = ModuleLoadException(module_id, "Activation timed out")
            return False
            
        except Exception as e:
            logger.error(f"Error activating module {module_id}: {e}")
            module_instance.state = ModuleState.FAILED
            module_instance.error = e
            return False

    async def deactivate_module(self, module_id: str) -> bool:
        """
        停用模块
        
        Args:
            module_id: 模块唯一标识符
            
        Returns:
            如果模块停用成功则返回True，否则返回False
        """
        # 获取模块实例
        if module_id not in self._modules:
            return True
        
        module_instance = self._modules[module_id]
        
        # 检查模块是否已激活
        if module_instance.state != ModuleState.ACTIVATED:
            return True
        
        try:
            # 获取模块
            module = module_instance.module
            if not module:
                return False
            
            # 调用模块停用函数
            await module.deactivate()
            
            # 标记模块为已加载
            module_instance.state = ModuleState.LOADED
            logger.info(f"Module deactivated: {module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating module {module_id}: {e}")
            return False
    
    async def _wait_for_module_state(self, module_id: str, target_states: List[ModuleState], timeout: float = 30.0) -> bool:
        """
        等待模块达到指定状态
        
        Args:
            module_id: 模块唯一标识符
            target_states: 目标状态列表
            timeout: 超时时间
            
        Returns:
            如果在超时前达到目标状态则返回True，否则返回False
        """
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout:
            if module_id not in self._modules:
                return False
            
            if self._modules[module_id].state in target_states:
                return True
            
            await asyncio.sleep(0.1)
        
        return False
    
    async def _validate_dependencies(self, module: Module) -> bool:
        """
        验证模块依赖
        
        Args:
            module: 模块实例
            
        Returns:
            如果依赖验证通过则返回True，否则返回False
        """
        if not module.metadata.dependencies:
            return True
        
        for dependency_id in module.metadata.dependencies:
            if dependency_id not in self._modules:
                logger.error(f"Dependency {dependency_id} not found for module {module.metadata.id}")
                return False
            
            dep_instance = self._modules[dependency_id]
            if dep_instance.state in [ModuleState.FAILED, ModuleState.LOADING, ModuleState.ACTIVATING]:
                logger.error(f"Dependency {dependency_id} is in invalid state: {dep_instance.state.value}")
                return False
        
        return True

    def get_module_api(self, module_id: str) -> Optional[Any]:
        """
        获取模块API
        
        Args:
            module_id: 模块唯一标识符
            
        Returns:
            模块API，如果模块不存在、未激活或没有API则返回None
        """
        module_instance = self._modules.get(module_id)
        if not module_instance or not module_instance.module:
            return None
        
        # 只有已激活的模块才能提供API
        if module_instance.state != ModuleState.ACTIVATED:
            logger.warning(f"Trying to access API of module {module_id} which is not activated")
            return None
        
        try:
            return module_instance.module.get_api()
        except Exception as e:
            logger.error(f"Error getting API for module {module_id}: {e}")
            return None

    def get_registered_modules(self) -> list[ModuleMetadata]:
        """
        获取所有已注册的模块
        
        Returns:
            已注册模块的元数据列表
        """
        return [module_instance.module.metadata 
                for module_instance in self._modules.values() 
                if module_instance.module]
    
    def get_module_state(self, module_id: str) -> Optional[str]:
        """
        获取模块状态
        
        Args:
            module_id: 模块唯一标识符
            
        Returns:
            模块状态字符串，如果模块不存在则返回None
        """
        module_instance = self._modules.get(module_id)
        if not module_instance:
            return None
        
        return module_instance.state.value
    
    def get_module_error(self, module_id: str) -> Optional[str]:
        """
        获取模块错误信息
        
        Args:
            module_id: 模块唯一标识符
            
        Returns:
            模块错误信息，如果模块不存在或没有错误则返回None
        """
        module_instance = self._modules.get(module_id)
        if not module_instance or not module_instance.error:
            return None
        
        return str(module_instance.error)

    def get_activated_modules(self) -> list[str]:
        """
        获取所有已激活的模块
        
        Returns:
            已激活模块的ID列表
        """
        return [module_id for module_id, module_instance in self._modules.items() 
                if module_instance.state == ModuleState.ACTIVATED]

    def discover_and_register_external_modules(self, plugins_dir: str = "plugins") -> None:
        """
        发现并注册外部模块
        
        Args:
            plugins_dir: 外部模块所在目录
        """
        module_paths = _discover_external_modules(plugins_dir)
        
        for module_path in module_paths:
            try:
                module = _import_module_from_path(module_path)
                if module:
                    # 查找模块类
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, Module) and attr != Module:
                            # 创建模块实例
                            module_instance = attr()
                            self.register_module(module_instance)
            except Exception as e:
                logger.error(f"Error loading external module {module_path}: {e}")


# 创建全局模块管理器实例
module_manager = ModuleManager()
