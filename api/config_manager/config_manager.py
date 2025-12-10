import json
import os
import copy
from typing import Dict, Any, Optional, List
from pathlib import Path
import dotenv

class ConfigManager:
    def __init__(self, config_dir: str = "./config", env_file: str = ".env"):
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        
        self.env_file = Path(env_file)
        if self.env_file.exists():
            dotenv.load_dotenv(self.env_file)
        
        
        self.config: Dict[str, Any] = {}
        self.config_files: Dict[str, Path] = {}
        
        
        self._load_default_config()
        
        
        self._load_env_config()
    
    def _load_default_config(self):
        
        default_config = {
            "app": {
                "name": "Cognot Workflow Engine",
                "version": "1.0.0",
                "debug": True
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "reload": True
            },
            "database": {
                "url": "sqlite:///./cognot.db",
                "echo": False
            },
            "websocket": {
                "enabled": True,
                "path": "/ws"
            },
            "file_upload": {
                "enabled": True,
                "upload_dir": "./uploads",
                "max_file_size": 104857600  
            },
            "security": {
                "api_key_required": False,
                "allowed_origins": ["*"]
            }
        }
        
        self.config.update(default_config)
    
    def _load_env_config(self):
        
        env_config = {
            "app": {
                "debug": os.getenv("APP_DEBUG", "True").lower() == "true"
            },
            "server": {
                "host": os.getenv("SERVER_HOST", "0.0.0.0"),
                "port": int(os.getenv("SERVER_PORT", "8000")),
                "reload": os.getenv("SERVER_RELOAD", "True").lower() == "true"
            },
            "database": {
                "url": os.getenv("DATABASE_URL", "sqlite:///./cognot.db"),
                "echo": os.getenv("DATABASE_ECHO", "False").lower() == "true"
            },
            "file_upload": {
                "max_file_size": int(os.getenv("FILE_UPLOAD_MAX_SIZE", "104857600"))
            },
            "security": {
                "api_key_required": os.getenv("API_KEY_REQUIRED", "False").lower() == "true"
            }
        }
        
        
        self._merge_config(self.config, env_config)
    
    def load_config_file(self, file_name: str, config_type: str = "app") -> bool:
        
        config_path = self.config_dir / file_name
        
        if config_path.exists() and config_path.is_file():
            try:
                with open(config_path, "r") as f:
                    file_config = json.load(f)
                
                
                if config_type not in self.config:
                    self.config[config_type] = {}
                
                
                self._merge_config(self.config[config_type], file_config)
                
                
                self.config_files[config_type] = config_path
                
                return True
            except Exception:
                return False
        
        return False
    
    def save_config_file(self, config_type: str = "app") -> bool:
        
        if config_type in self.config_files:
            config_path = self.config_files[config_type]
        else:
            config_path = self.config_dir / f"{config_type}.json"
        
        try:
            with open(config_path, "w") as f:
                json.dump(self.config.get(config_type, {}), f, indent=2)
            
            
            self.config_files[config_type] = config_path
            
            return True
        except Exception:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        
        keys = key.split(".")
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        
        keys = key.split(".")
        config = self.config
        
        try:
            
            for k in keys[:-1]:
                if k not in config or not isinstance(config[k], dict):
                    config[k] = {}
                config = config[k]
            
            
            config[keys[-1]] = value
            return True
        except Exception:
            return False
    
    def update(self, config_dict: Dict[str, Any]) -> bool:
        
        try:
            self._merge_config(self.config, config_dict)
            return True
        except Exception:
            return False
    
    def get_section(self, section: str) -> Optional[Dict[str, Any]]:
        
        return copy.deepcopy(self.config.get(section))
    
    def set_section(self, section: str, config_dict: Dict[str, Any]) -> bool:
        
        try:
            self.config[section] = copy.deepcopy(config_dict)
            return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        
        keys = key.split(".")
        config = self.config
        
        try:
            
            for k in keys[:-1]:
                config = config[k]
            
            
            if keys[-1] in config:
                del config[keys[-1]]
                return True
            return False
        except Exception:
            return False
    
    def list_sections(self) -> List[str]:
        
        return list(self.config.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        
        return copy.deepcopy(self.config)
    
    def _merge_config(self, target: Dict[str, Any], source: Dict[str, Any]):
        
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                
                self._merge_config(target[key], value)
            else:
                
                target[key] = value

config_manager = ConfigManager()

config_manager.load_config_file("app.json", "app")
config_manager.load_config_file("server.json", "server")
config_manager.load_config_file("database.json", "database")
