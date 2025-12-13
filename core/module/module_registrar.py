# 模块注册器，提供简化的模块注册API

from typing import Optional, Callable, Any
from .module_interface import Module, ModuleMetadata
from .module_manager import module_manager


class ModuleRegistrationOptions:
    """
    模块注册选项
    """
    def __init__(self,
                 id: str,
                 name: str,
                 version: str,
                 description: str,
                 dependencies: Optional[list[str]] = None,
                 activate: Optional[Callable[[], None]] = None,
                 deactivate: Optional[Callable[[], None]] = None,
                 async_activate: Optional[Callable[[], None]] = None,
                 async_deactivate: Optional[Callable[[], None]] = None,
                 get_api: Optional[Callable[[], Any]] = None):
        self.id = id
        self.name = name
        self.version = version
        self.description = description
        self.dependencies = dependencies
        self.activate = activate
        self.deactivate = deactivate
        self.async_activate = async_activate
        self.async_deactivate = async_deactivate
        self.get_api = get_api


class RegistrationModule(Module):
    """
    用于注册的模块实现
    """
    def __init__(self, options: ModuleRegistrationOptions):
        metadata = ModuleMetadata(
            id=options.id,
            name=options.name,
            version=options.version,
            description=options.description,
            dependencies=options.dependencies
        )
        super().__init__(metadata)
        self._options = options

    async def activate(self) -> None:
        """
        模块激活函数
        """
        if self._options.async_activate:
            await self._options.async_activate()
        elif self._options.activate:
            self._options.activate()

    async def deactivate(self) -> None:
        """
        模块停用函数
        """
        if self._options.async_deactivate:
            await self._options.async_deactivate()
        elif self._options.deactivate:
            self._options.deactivate()

    def get_api(self) -> Optional[Any]:
        """
        获取模块API
        """
        if self._options.get_api:
            return self._options.get_api()
        return None


def register_module(options: ModuleRegistrationOptions) -> None:
    """
    简化的模块注册函数
    
    Args:
        options: 模块注册选项
    """
    module = RegistrationModule(options)
    
    # 直接注册模块实例
    module_manager.register_module(module)


async def register_and_activate_module(options: ModuleRegistrationOptions) -> bool:
    """
    注册并激活模块
    
    Args:
        options: 模块注册选项
        
    Returns:
        如果模块激活成功则返回True，否则返回False
    """
    register_module(options)
    return await module_manager.activate_module(options.id)


def create_module_api(api_object: Any) -> Callable[[], Any]:
    """
    创建模块API获取函数
    
    Args:
        api_object: 模块API对象
        
    Returns:
        API获取函数
    """
    return lambda: api_object
