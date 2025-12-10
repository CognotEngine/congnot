
from typing import Any, Optional, Dict
from .interfaces import StorageInterface

class MemoryStorage(StorageInterface):
    def __init__(self):
        
        self.storage: Dict[str, Any] = {}
    
    def get(self, key: str) -> Optional[Any]:
        
        return self.storage.get(key)
    
    def set(self, key: str, value: Any) -> bool:
        
        self.storage[key] = value
        return True
    
    def delete(self, key: str) -> bool:
        
        if key in self.storage:
            del self.storage[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        
        return key in self.storage
    
    def get_all(self) -> Dict[str, Any]:
        
        return self.storage.copy()
    
    def clear(self) -> bool:
        
        self.storage.clear()
        return True
    
    def size(self) -> int:
        
        return len(self.storage)
    
    def keys(self) -> list:
        
        return list(self.storage.keys())
    
    def values(self) -> list:
        
        return list(self.storage.values())
