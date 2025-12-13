import json
import os
import copy
import yaml
import re
import logging
from typing import Dict, Any, Optional, List, TypeVar, Type
from pathlib import Path
import dotenv
from pydantic import BaseModel, ValidationError, Field
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio

# 设置日志
logging.basicConfig(level=logging.INFO, encoding='utf-8')
logger = logging.getLogger(__name__)

# 类型变量用于泛型支持
T = TypeVar('T', bound=BaseModel)

class ConfigModel(BaseModel):
    """
    基础配置模型类，用于验证和类型转换
    """
    class Config:
        extra = "allow"
        env_file_encoding = "utf-8"

class AppConfig(ConfigModel):
    """
    应用程序配置模型
    """
    name: str = Field(default="Cognot Workflow Engine", env="APP_NAME")
    version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=True, env="APP_DEBUG")

class ServerConfig(ConfigModel):
    """
    服务器配置模型
    """
    host: str = Field(default="0.0.0.0", env="SERVER_HOST")
    port: int = Field(default=8000, env="SERVER_PORT")
    reload: bool = Field(default=True, env="SERVER_RELOAD")

class DatabaseConfig(ConfigModel):
    """
    数据库配置模型
    """
    url: str = Field(default="sqlite:///./cognot.db", env="DATABASE_URL")
    echo: bool = Field(default=False, env="DATABASE_ECHO")

class WebSocketConfig(ConfigModel):
    """
    WebSocket配置模型
    """
    enabled: bool = Field(default=True, env="WEBSOCKET_ENABLED")
    path: str = Field(default="/ws", env="WEBSOCKET_PATH")

class FileUploadConfig(ConfigModel):
    """
    文件上传配置模型
    """
    enabled: bool = Field(default=True, env="FILE_UPLOAD_ENABLED")
    upload_dir: str = Field(default="./uploads", env="FILE_UPLOAD_DIR")
    max_file_size: int = Field(default=104857600, env="FILE_UPLOAD_MAX_SIZE")

class SecurityConfig(ConfigModel):
    """
    安全配置模型
    """
    api_key_required: bool = Field(default=False, env="API_KEY_REQUIRED")
    allowed_origins: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    api_key: Optional[str] = Field(default=None, env="API_KEY")

class ProxyConfig(ConfigModel):
    """
    代理配置模型
    """
    enabled: bool = Field(default=True, env="PROXY_ENABLED")
    auto_detect: bool = Field(default=True, env="PROXY_AUTO_DETECT")
    host: str = Field(default="", env="PROXY_HOST")
    port: int = Field(default=0, env="PROXY_PORT")
    username: Optional[str] = Field(default=None, env="PROXY_USERNAME")
    password: Optional[str] = Field(default=None, env="PROXY_PASSWORD")
    protocol: str = Field(default="http", env="PROXY_PROTOCOL")

class ModulesConfig(ConfigModel):
    """
    模块配置模型
    """
    enabled: List[str] = Field(default=["workflow"], env="ENABLED_MODULES")
    plugins_dir: str = Field(default="./plugins", env="PLUGINS_DIR")

class CognotConfig(ConfigModel):
    """
    完整的Cognot配置模型
    """
    app: AppConfig = AppConfig()
    server: ServerConfig = ServerConfig()
    database: DatabaseConfig = DatabaseConfig()
    websocket: WebSocketConfig = WebSocketConfig()
    file_upload: FileUploadConfig = FileUploadConfig()
    security: SecurityConfig = SecurityConfig()
    modules: ModulesConfig = ModulesConfig()
    proxy: ProxyConfig = ProxyConfig()

class ConfigChangeHandler(FileSystemEventHandler):
    """
    配置文件变化处理器
    """
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.debounce_timer = None

    def on_modified(self, event):
        """
        当配置文件被修改时触发
        """
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix in ['.json', '.yaml', '.yml']:
            # 使用防抖机制避免频繁触发
            if self.debounce_timer:
                self.debounce_timer.cancel()
            
            async def reload_config():
                await asyncio.sleep(0.5)  # 500ms防抖
                try:
                    await self.config_manager.reload_config()
                    logger.info(f"配置文件 {file_path} 已重载")
                except Exception as e:
                    logger.error(f"重载配置文件 {file_path} 失败: {e}")
            
            self.debounce_timer = asyncio.create_task(reload_config())

class ConfigManager:
    """
    配置管理器，支持JSON/YAML格式，环境变量覆盖，配置验证和热重载
    """
    def __init__(self, config_dir: str = "./config", env_file: str = ".env", enable_watch: bool = True):
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载环境变量
        self.env_file = Path(env_file)
        if self.env_file.exists():
            dotenv.load_dotenv(self.env_file)
        
        # 配置存储
        self.config: Dict[str, Any] = {}
        self.config_files: Dict[str, Path] = {}
        self.config_model: CognotConfig = CognotConfig()
        
        # 配置热重载
        self.enable_watch = enable_watch
        self.observer = None
        
        # 初始化配置
        self._load_default_config()
        self._load_env_config()
        
        # 启动配置监控
        if self.enable_watch:
            self._start_watchdog()
    
    def _load_default_config(self):
        """
        从Pydantic模型加载默认配置
        """
        self.config = self.config_model.dict()
    
    def _load_env_config(self):
        """
        从环境变量加载配置（使用Pydantic自动处理）
        """
        # Pydantic已经在模型初始化时处理了环境变量
        # 这里只需要更新配置字典
        env_config = self.config_model.dict()
        self._merge_config(self.config, env_config)
    
    def load_config_file(self, file_name: str, config_type: Optional[str] = None) -> bool:
        """
        加载配置文件，支持JSON和YAML格式
        
        Args:
            file_name: 配置文件名
            config_type: 配置类型（可选）
            
        Returns:
            是否成功加载
        """
        config_path = self.config_dir / file_name
        
        if config_path.exists() and config_path.is_file():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    if file_name.endswith('.json'):
                        file_config = json.load(f)
                    elif file_name.endswith(('.yaml', '.yml')):
                        file_config = yaml.safe_load(f)
                    else:
                        logger.error(f"不支持的配置文件格式: {file_name}")
                        return False
                
                # 验证配置
                self._validate_config(file_config)
                
                # 合并配置
                if config_type:
                    if config_type not in self.config:
                        self.config[config_type] = {}
                    self._merge_config(self.config[config_type], file_config)
                    self.config_files[config_type] = config_path
                else:
                    self._merge_config(self.config, file_config)
                    self.config_files[file_name] = config_path
                
                # 更新Pydantic模型
                self._update_config_model()
                
                logger.info(f"成功加载配置文件: {file_name}")
                return True
            except ValidationError as e:
                logger.error(f"配置验证失败 {file_name}: {e}")
                return False
            except Exception as e:
                logger.error(f"加载配置文件失败 {file_name}: {e}")
                return False
        
        logger.warning(f"配置文件不存在: {file_name}")
        return False
    
    def save_config_file(self, config_type: str = "app", format: str = "json") -> bool:
        """
        保存配置到文件
        
        Args:
            config_type: 配置类型
            format: 文件格式（json或yaml）
            
        Returns:
            是否成功保存
        """
        if config_type in self.config_files:
            config_path = self.config_files[config_type]
        else:
            ext = ".yaml" if format == "yaml" else ".json"
            config_path = self.config_dir / f"{config_type}{ext}"
        
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                config_data = self.config.get(config_type, {})
                if format == "yaml":
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.config_files[config_type] = config_path
            logger.info(f"成功保存配置到文件: {config_path}")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败 {config_path}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键（支持点表示法，如 "app.debug"）
            default: 默认值
            
        Returns:
            配置值或默认值
        """
        keys = key.split(".")
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_model(self, model_type: Type[T]) -> T:
        """
        获取类型化的配置模型
        
        Args:
            model_type: 模型类型
            
        Returns:
            配置模型实例
        """
        try:
            if model_type == AppConfig:
                return self.config_model.app
            elif model_type == ServerConfig:
                return self.config_model.server
            elif model_type == DatabaseConfig:
                return self.config_model.database
            elif model_type == WebSocketConfig:
                return self.config_model.websocket
            elif model_type == FileUploadConfig:
                return self.config_model.file_upload
            elif model_type == SecurityConfig:
                return self.config_model.security
            elif model_type == ModulesConfig:
                return self.config_model.modules
            elif model_type == ProxyConfig:
                return self.config_model.proxy
            elif model_type == CognotConfig:
                return self.config_model
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")
        except Exception as e:
            logger.error(f"获取配置模型失败: {e}")
            raise
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键（支持点表示法，如 "app.debug"）
            value: 配置值
            
        Returns:
            是否成功设置
        """
        keys = key.split(".")
        config = self.config
        
        try:
            # 创建嵌套结构
            for k in keys[:-1]:
                if k not in config or not isinstance(config[k], dict):
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            
            # 更新Pydantic模型
            self._update_config_model()
            
            logger.debug(f"设置配置: {key} = {value}")
            return True
        except Exception as e:
            logger.error(f"设置配置失败 {key}: {e}")
            return False
    
    def update(self, config_dict: Dict[str, Any]) -> bool:
        """
        更新配置字典
        
        Args:
            config_dict: 配置字典
            
        Returns:
            是否成功更新
        """
        try:
            # 验证配置
            self._validate_config(config_dict)
            
            # 合并配置
            self._merge_config(self.config, config_dict)
            
            # 更新Pydantic模型
            self._update_config_model()
            
            logger.info("成功更新配置")
            return True
        except ValidationError as e:
            logger.error(f"配置验证失败: {e}")
            return False
        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            return False
    
    def get_section(self, section: str) -> Optional[Dict[str, Any]]:
        """
        获取配置节
        
        Args:
            section: 配置节名称
            
        Returns:
            配置节的深拷贝
        """
        return copy.deepcopy(self.config.get(section))
    
    def set_section(self, section: str, config_dict: Dict[str, Any]) -> bool:
        """
        设置配置节
        
        Args:
            section: 配置节名称
            config_dict: 配置字典
            
        Returns:
            是否成功设置
        """
        try:
            # 验证配置
            self._validate_config({section: config_dict})
            
            # 设置配置节
            self.config[section] = copy.deepcopy(config_dict)
            
            # 更新Pydantic模型
            self._update_config_model()
            
            logger.info(f"成功设置配置节: {section}")
            return True
        except ValidationError as e:
            logger.error(f"配置节验证失败 {section}: {e}")
            return False
        except Exception as e:
            logger.error(f"设置配置节失败 {section}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除配置项
        
        Args:
            key: 配置键（支持点表示法，如 "app.debug"）
            
        Returns:
            是否成功删除
        """
        keys = key.split(".")
        config = self.config
        
        try:
            # 导航到父节点
            for k in keys[:-1]:
                config = config[k]
            
            # 删除键
            if keys[-1] in config:
                del config[keys[-1]]
                
                # 更新Pydantic模型
                self._update_config_model()
                
                logger.debug(f"删除配置: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除配置失败 {key}: {e}")
            return False
    
    def list_sections(self) -> List[str]:
        """
        获取所有配置节名称
        
        Returns:
            配置节名称列表
        """
        return list(self.config.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        获取完整的配置字典
        
        Returns:
            配置字典的深拷贝
        """
        return copy.deepcopy(self.config)
    
    def reload_config(self):
        """
        重新加载所有配置文件
        """
        logger.info("重新加载所有配置...")
        
        # 重置配置到默认值
        self._load_default_config()
        self._load_env_config()
        
        # 重新加载所有配置文件
        for config_type, config_path in self.config_files.items():
            self.load_config_file(config_path.name, config_type)
        
        logger.info("配置重新加载完成")
    
    def _start_watchdog(self):
        """
        启动配置文件监控
        """
        try:
            self.observer = Observer()
            handler = ConfigChangeHandler(self)
            self.observer.schedule(handler, str(self.config_dir), recursive=False)
            self.observer.start()
            logger.info(f"启动配置监控: {self.config_dir}")
        except Exception as e:
            logger.error(f"启动配置监控失败: {e}")
            self.observer = None
    
    def _stop_watchdog(self):
        """
        停止配置文件监控
        """
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            logger.info("停止配置监控")
    
    def _validate_config(self, config_dict: Dict[str, Any]):
        """
        验证配置字典
        
        Args:
            config_dict: 要验证的配置字典
            
        Raises:
            ValidationError: 配置验证失败
        """
        try:
            # 尝试更新模型来验证配置
            updated_dict = self.config.copy()
            self._merge_config(updated_dict, config_dict)
            CognotConfig(**updated_dict)
        except Exception as e:
            logger.error(f"配置验证失败: {config_dict}")
            raise
    
    def _update_config_model(self):
        """
        更新Pydantic配置模型
        """
        try:
            self.config_model = CognotConfig(**self.config)
            logger.debug("更新配置模型成功")
        except ValidationError as e:
            logger.error(f"更新配置模型失败: {e}")
            # 保留旧模型
    
    def __del__(self):
        """
        清理资源
        """
        self._stop_watchdog()
    
    def _merge_config(self, target: Dict[str, Any], source: Dict[str, Any]):
        
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                
                self._merge_config(target[key], value)
            else:
                
                target[key] = value

config_manager = ConfigManager()

# 加载默认配置文件
config_manager.load_config_file("app.json")
config_manager.load_config_file("server.json")
config_manager.load_config_file("database.json")
config_manager.load_config_file("cognot.yaml")  # 支持YAML格式的完整配置文件
