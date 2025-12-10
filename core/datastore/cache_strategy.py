
from typing import Any, Optional, Dict, OrderedDict
from .interfaces import CacheStrategyInterface

class LRUCacheStrategy(CacheStrategyInterface):
    def __init__(self, capacity: int):
        self.capacity = capacity
        
        self.cache: OrderedDict[str, Any] = OrderedDict()
        
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get(self, key: str) -> Optional[Any]:
        
        if key in self.cache:
            
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        else:
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any) -> None:
        
        if key in self.cache:
            
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.capacity:
            
            self.cache.popitem(last=False)
            self.evictions += 1
        
        
        self.cache[key] = value
    
    def delete(self, key: str) -> None:
        
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get_stats(self) -> Dict[str, int]:
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "size": len(self.cache),
            "capacity": self.capacity
        }
    
    def size(self) -> int:
        
        return len(self.cache)
    
    def keys(self) -> list:
        
        return list(self.cache.keys())

class FIFOCacheStrategy(CacheStrategyInterface):
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict[str, Any] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        else:
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any) -> None:
        if key in self.cache:
            
            self.cache[key] = value
        elif len(self.cache) >= self.capacity:
            
            self.cache.popitem(last=False)
            self.evictions += 1
        
        
        self.cache[key] = value
    
    def delete(self, key: str) -> None:
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def get_stats(self) -> Dict[str, int]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "size": len(self.cache),
            "capacity": self.capacity
        }
