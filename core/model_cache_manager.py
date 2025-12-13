import os
import logging
import torch
from typing import Dict, Optional, Any, Callable
from threading import Lock

logger = logging.getLogger(__name__)

class ModelCacheManager:
    """
    模型缓存管理器，用于优化模型加载和内存使用
    - 支持模型预加载
    - 实现LRU缓存策略
    - 提供内存监控和自动释放机制
    - 支持多GPU环境
    """
    
    def __init__(self, max_cache_size: int = 5, max_memory_percent: float = 0.8):
        """
        初始化模型缓存管理器
        
        Args:
            max_cache_size: 最大缓存模型数量
            max_memory_percent: 最大内存使用率百分比(0-1)
        """
        self.max_cache_size = max_cache_size
        self.max_memory_percent = max_memory_percent
        
        # 模型缓存字典: {model_key: (model, last_used_time, memory_usage)}
        self._cache: Dict[str, tuple] = {}
        
        # 缓存访问顺序 (用于LRU策略)
        self._access_order: list = []
        
        # 线程锁，确保线程安全
        self._lock = Lock()
        
        # 设备信息
        self.devices = self._get_available_devices()
        self.current_device = self.devices[0] if self.devices else "cpu"
    
    def _get_available_devices(self) -> list:
        """获取可用的设备列表"""
        devices = ["cpu"]
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                devices.append(f"cuda:{i}")
        return devices
    
    def _get_memory_usage(self) -> Dict[str, float]:
        """获取当前内存使用情况"""
        usage = {}
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                total_mem = torch.cuda.get_device_properties(i).total_memory
                used_mem = torch.cuda.memory_allocated(i)
                usage[f"cuda:{i}"] = used_mem / total_mem
        return usage
    
    def _is_memory_full(self) -> bool:
        """检查内存是否已满"""
        memory_usage = self._get_memory_usage()
        for device, usage in memory_usage.items():
            if usage > self.max_memory_percent:
                return True
        return False
    
    def _evict_oldest_model(self) -> Optional[str]:
        """使用LRU策略驱逐最旧的模型"""
        with self._lock:
            if not self._access_order:
                return None
            
            oldest_key = self._access_order.pop(0)
            if oldest_key in self._cache:
                model, _, _ = self._cache.pop(oldest_key)
                
                # 释放模型占用的内存
                if hasattr(model, "to"):
                    try:
                        model.to("cpu")
                    except Exception as e:
                        logger.error(f"Failed to move model to CPU: {e}")
                
                if hasattr(model, "unload"):
                    try:
                        model.unload()
                    except Exception as e:
                        logger.error(f"Failed to unload model: {e}")
                
                torch.cuda.empty_cache()
                logger.info(f"Evicted model: {oldest_key}")
                return oldest_key
        return None
    
    def _update_access_time(self, model_key: str) -> None:
        """更新模型的访问时间(用于LRU策略)"""
        with self._lock:
            if model_key in self._access_order:
                self._access_order.remove(model_key)
            self._access_order.append(model_key)
    
    def get_model(self, model_key: str) -> Optional[Any]:
        """
        从缓存中获取模型
        
        Args:
            model_key: 模型的唯一标识符
            
        Returns:
            模型实例，如果不存在则返回None
        """
        with self._lock:
            if model_key in self._cache:
                model, _, _ = self._cache[model_key]
                self._update_access_time(model_key)
                return model
        return None
    
    def add_model(self, model_key: str, model: Any, memory_usage: float = 0.0) -> bool:
        """
        将模型添加到缓存中
        
        Args:
            model_key: 模型的唯一标识符
            model: 模型实例
            memory_usage: 模型占用的内存(MB)
            
        Returns:
            True如果添加成功，False否则
        """
        with self._lock:
            # 检查缓存是否已满
            while len(self._cache) >= self.max_cache_size or self._is_memory_full():
                if not self._evict_oldest_model():
                    logger.error("Failed to evict model, cache is full")
                    return False
            
            # 添加模型到缓存
            self._cache[model_key] = (model, 0, memory_usage)  # 0是占位符，实际可以用时间戳
            self._update_access_time(model_key)
            logger.info(f"Added model to cache: {model_key}")
            return True
    
    def remove_model(self, model_key: str) -> bool:
        """
        从缓存中移除模型
        
        Args:
            model_key: 模型的唯一标识符
            
        Returns:
            True如果移除成功，False否则
        """
        with self._lock:
            if model_key in self._cache:
                model, _, _ = self._cache.pop(model_key)
                
                # 释放模型占用的内存
                if hasattr(model, "to"):
                    try:
                        model.to("cpu")
                    except Exception as e:
                        logger.error(f"Failed to move model to CPU: {e}")
                
                if hasattr(model, "unload"):
                    try:
                        model.unload()
                    except Exception as e:
                        logger.error(f"Failed to unload model: {e}")
                
                torch.cuda.empty_cache()
                
                if model_key in self._access_order:
                    self._access_order.remove(model_key)
                
                logger.info(f"Removed model from cache: {model_key}")
                return True
        return False
    
    def clear_cache(self) -> int:
        """
        清空所有缓存的模型
        
        Returns:
            被清空的模型数量
        """
        with self._lock:
            cleared_count = 0
            for model_key in list(self._cache.keys()):
                if self.remove_model(model_key):
                    cleared_count += 1
            self._access_order.clear()
            return cleared_count
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        获取缓存信息
        
        Returns:
            缓存信息字典
        """
        with self._lock:
            return {
                "cache_size": len(self._cache),
                "max_cache_size": self.max_cache_size,
                "cached_models": list(self._cache.keys()),
                "memory_usage": self._get_memory_usage()
            }
    
    def preload_model(self, model_key: str, load_func: Callable, *args, **kwargs) -> bool:
        """
        预加载模型到缓存中
        
        Args:
            model_key: 模型的唯一标识符
            load_func: 加载模型的函数
            *args: 加载函数的位置参数
            **kwargs: 加载函数的关键字参数
            
        Returns:
            True如果预加载成功，False否则
        """
        try:
            logger.info(f"Preloading model: {model_key}")
            model = load_func(*args, **kwargs)
            
            # 估算模型内存使用
            memory_usage = 0.0
            if hasattr(model, "get_memory_usage"):
                memory_usage = model.get_memory_usage()
            elif hasattr(model, "to") and torch.cuda.is_available():
                # 简单估算：将模型移动到GPU并测量内存变化
                model.to(self.current_device)
                memory_usage = torch.cuda.memory_allocated(self.current_device) / (1024 * 1024)  # MB
                
            return self.add_model(model_key, model, memory_usage)
        except Exception as e:
            logger.error(f"Failed to preload model {model_key}: {e}")
            return False

# 创建全局模型缓存管理器实例
model_cache_manager = ModelCacheManager(max_cache_size=3, max_memory_percent=0.75)
