
from typing import Any, Optional, Dict, List
from .interfaces import StorageInterface, CacheStrategyInterface
from .cache_strategy import LRUCacheStrategy

class DataStoreConfig:
    def __init__(self,
                 storage_type: str = "memory",
                 cache_size: int = 1000,
                 cache_strategy: str = "lru"):
        self.storage_type = storage_type
        self.cache_size = cache_size
        self.cache_strategy = cache_strategy

class DataStore:
    def __init__(self, config: Optional[DataStoreConfig] = None):
        self.config = config or DataStoreConfig()
        
        
        self._initialize_storage()
        
        
        self._initialize_cache()
    
    
    def _initialize_storage(self):
        if self.config.storage_type == "memory":
            from .memory_storage import MemoryStorage
            self.storage = MemoryStorage()
        else:
            raise ValueError(f"不支持的存储类型: {self.config.storage_type}")
    
    
    def _initialize_cache(self):
        if self.config.cache_strategy == "lru":
            self.cache = LRUCacheStrategy(self.config.cache_size)
        else:
            raise ValueError(f"不支持的缓存策略: {self.config.cache_strategy}")
    
    
    def get(self, key: str) -> Optional[Any]:
        
        cache_value = self.cache.get(key)
        if cache_value is not None:
            return cache_value
        
        
        value = self.storage.get(key)
        if value is not None:
            
            self.cache.set(key, value)
        
        return value
    
    
    def set(self, key: str, value: Any) -> bool:
        
        result = self.storage.set(key, value)
        if result:
            
            self.cache.set(key, value)
        return result
    
    
    def delete(self, key: str) -> bool:
        
        result = self.storage.delete(key)
        if result:
            
            self.cache.delete(key)
        return result
    
    
    def exists(self, key: str) -> bool:
        
        if self.cache.get(key) is not None:
            return True
        
        
        return self.storage.exists(key)
    
    
    def get_all(self) -> Dict[str, Any]:
        return self.storage.get_all()
    
    
    def clear(self) -> bool:
        
        self.storage.clear()
        
        self.cache.clear()
        return True
    
    
    def get_cache_stats(self) -> Dict[str, int]:
        if hasattr(self.cache, "get_stats"):
            return self.cache.get_stats()
        return {}
