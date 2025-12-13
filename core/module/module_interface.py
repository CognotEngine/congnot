# 模块接口定义

from typing import Optional, Any, List
from dataclasses import dataclass


@dataclass
class ModuleMetadata:
    """
    模块元数据
    """
    id: str  # 模块唯一标识符
    name: str  # 模块名称
    version: str  # 模块版本
    description: str  # 模块描述
    dependencies: Optional[List[str]] = None  # 依赖的其他模块ID
    python_dependencies: Optional[List[str]] = None  # 依赖的 Python 包
    entry_point: Optional[str] = None  # 模块入口点


class Module:
    """
    模块基类，所有模块都应继承此类或实现相同的接口
    """
    def __init__(self, metadata: ModuleMetadata):
        self.metadata = metadata

    async def activate(self) -> None:
        """
        模块激活函数，在模块加载时调用
        """
        pass

    async def deactivate(self) -> None:
        """
        模块停用函数，在模块卸载时调用
        """
        pass

    def get_api(self) -> Optional[Any]:
        """
        获取模块API
        """
        return None
