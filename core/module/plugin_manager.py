# 插件管理器

import os
import sys
import importlib.util
import logging
import asyncio
import subprocess
import shutil
import requests
import json
import time
import tempfile
import uuid
from typing import Dict, Optional, List, Type, Tuple
from .module_manager import ModuleManager, ModuleState
from .module_interface import Module, ModuleMetadata
from api.config_manager.config_manager import config_manager

logger = logging.getLogger(__name__)


class PluginManager(ModuleManager):
    """
    插件管理器，负责动态加载和管理插件模块
    """
    def __init__(self):
        super().__init__()
        self._plugin_dirs: List[str] = []  # 插件目录列表
        self._loaded_plugins: Dict[str, str] = {}  # 已加载插件的路径映射
        self._community_plugins = {
            # 示例社区插件，后续可从配置文件加载
            "WAS_Suite": {
                "name": "WAS Suite",
                "description": "A collection of advanced sampling nodes",
                "git_url": "https://github.com/Example/WAS-Suite.git",
                "nodes": ["WAS_Suite_Sampler", "WAS_Suite_NoiseGenerator"]
            },
            "MyCustomLoader": {
                "name": "My Custom Loader",
                "description": "Custom data loader for various formats",
                "git_url": "https://github.com/Example/MyCustomLoader.git",
                "nodes": ["MyCustomLoader"]
            }
        }
        # 插件索引相关配置
        self._index_url = "https://raw.githubusercontent.com/ltdrdata/ComfyUI-Manager/main/extension-node-map.json"
        self._custom_repositories: List[str] = []  # 用户自定义的仓库地址列表
        self._disabled_repositories: List[str] = []  # 用户禁用的仓库地址列表
        self._index_cache: Dict[str, List[str]] = {}  # 缓存的索引，键为git_url，值为节点列表
        self._index_last_updated: float = 0  # 最后更新时间
        self._index_cache_duration = 3600  # 缓存有效期（秒）
        # 反向索引，用于快速查找节点对应的插件
        self._reverse_index: Dict[str, str] = {}  # 键为节点名，值为git_url
        
        # 加载用户自定义仓库配置
        self._load_custom_repositories()

    def add_plugin_dir(self, plugin_dir: str) -> None:
        """
        添加插件目录
        
        Args:
            plugin_dir: 插件目录路径
        """
        if not os.path.isdir(plugin_dir):
            logger.error(f"Plugin directory {plugin_dir} does not exist")
            return
        
        if plugin_dir not in self._plugin_dirs:
            self._plugin_dirs.append(plugin_dir)
            logger.info(f"Added plugin directory: {plugin_dir}")

    async def discover_plugins(self) -> List[str]:
        """
        发现插件目录中的所有插件
        
        Returns:
            发现的插件ID列表
        """
        discovered_plugins = []
        
        for plugin_dir in self._plugin_dirs:
            # 遍历插件目录
            for item in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item)
                
                # 检查是否是目录
                if os.path.isdir(item_path):
                    # 检查目录中是否有__init__.py文件
                    if os.path.isfile(os.path.join(item_path, "__init__.py")):
                        try:
                            # 尝试加载插件元数据
                            plugin_id = await self._load_plugin_metadata(item_path)
                            if plugin_id:
                                discovered_plugins.append(plugin_id)
                        except Exception as e:
                            logger.error(f"Error discovering plugin {item}: {e}")
                
                # 检查是否是.py文件（单文件插件）
                elif item.endswith(".py") and not item.startswith("_"):
                    try:
                        plugin_id = await self._load_plugin_metadata(item_path)
                        if plugin_id:
                            discovered_plugins.append(plugin_id)
                    except Exception as e:
                        logger.error(f"Error discovering plugin {item}: {e}")
        
        return discovered_plugins

    async def load_plugin(self, plugin_path: str) -> Optional[str]:
        """
        加载单个插件
        
        Args:
            plugin_path: 插件路径（目录或文件）
            
        Returns:
            加载的插件ID，如果加载失败则返回None
        """
        try:
            # 加载插件元数据
            plugin_id = await self._load_plugin_metadata(plugin_path)
            if not plugin_id:
                return None
            
            # 激活插件
            if await self.activate_module(plugin_id):
                logger.info(f"Plugin loaded successfully: {plugin_id}")
                self._loaded_plugins[plugin_id] = plugin_path
                return plugin_id
            else:
                logger.error(f"Failed to activate plugin: {plugin_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_path}: {e}")
            return None

    async def unload_plugin(self, plugin_id: str) -> bool:
        """
        卸载插件
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            如果卸载成功则返回True，否则返回False
        """
        try:
            # 停用插件
            if not await self.deactivate_module(plugin_id):
                logger.warning(f"Plugin {plugin_id} was not activated")
            
            # 从已加载插件列表中移除
            if plugin_id in self._loaded_plugins:
                del self._loaded_plugins[plugin_id]
            
            # 从模块管理器中移除模块
            if plugin_id in self._modules:
                del self._modules[plugin_id]
            
            logger.info(f"Plugin unloaded successfully: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_id}: {e}")
            return False

    async def reload_plugin(self, plugin_id: str) -> Optional[str]:
        """
        重新加载插件
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            重新加载的插件ID，如果加载失败则返回None
        """
        try:
            # 检查插件是否已加载
            if plugin_id not in self._loaded_plugins:
                logger.error(f"Plugin {plugin_id} is not loaded")
                return None
            
            plugin_path = self._loaded_plugins[plugin_id]
            
            # 卸载插件
            await self.unload_plugin(plugin_id)
            
            # 重新加载插件
            return await self.load_plugin(plugin_path)
            
        except Exception as e:
            logger.error(f"Error reloading plugin {plugin_id}: {e}")
            return None

    def get_loaded_plugins(self) -> Dict[str, str]:
        """
        获取已加载的插件
        
        Returns:
            已加载插件的ID到路径的映射
        """
        return self._loaded_plugins.copy()

    def get_community_plugins(self) -> Dict[str, Dict]:
        """
        获取社区插件列表
        
        Returns:
            社区插件列表，键为插件ID，值为插件信息
        """
        return self._community_plugins
        
    def get_available_plugins(self) -> Dict[str, Dict]:
        """
        获取所有可用插件列表，包括社区插件和从索引中获取的插件
        
        Returns:
            可用插件列表，键为插件ID，值为插件信息
        """
        available_plugins = {}
        
        # 添加预设的社区插件
        for plugin_id, plugin_info in self._community_plugins.items():
            available_plugins[plugin_id] = plugin_info
        
        # 添加从索引中获取的插件
        for git_url, nodes in self._index_cache.items():
            # 提取仓库名称作为插件ID
            plugin_id = git_url.split('/')[-1].replace('.git', '')
            
            # 如果插件ID已经存在，跳过
            if plugin_id in available_plugins:
                continue
                
            # 创建插件信息
            plugin_info = {
                "name": plugin_id,
                "description": f"Plugin with {len(nodes)} nodes",
                "git_url": git_url,
                "nodes": nodes
            }
            
            available_plugins[plugin_id] = plugin_info
        
        return available_plugins
        
    def _load_custom_repositories(self):
        """
        从配置文件加载用户自定义的仓库地址
        """
        try:
            config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "repositories.json")
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self._custom_repositories = config.get("custom", [])
                    self._disabled_repositories = config.get("disabled", [])
                logger.info(f"Loaded custom repositories: {len(self._custom_repositories)}, disabled: {len(self._disabled_repositories)}")
        except Exception as e:
            logger.error(f"Failed to load custom repositories: {e}")
    
    def _save_custom_repositories(self):
        """
        将用户自定义的仓库地址保存到配置文件
        """
        try:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
            os.makedirs(config_dir, exist_ok=True)
            config_file = os.path.join(config_dir, "repositories.json")
            
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump({
                    "custom": self._custom_repositories,
                    "disabled": self._disabled_repositories
                }, f, indent=2)
            logger.info("Saved custom repositories to configuration file")
        except Exception as e:
            logger.error(f"Failed to save custom repositories: {e}")
    
    async def fetch_and_cache_index(self, force_refresh: bool = False) -> bool:
        """
        获取并缓存插件索引
        
        Args:
            force_refresh: 是否强制刷新缓存
            
        Returns:
            是否成功获取索引
        """
        try:
            # 检查缓存是否有效
            current_time = time.time()
            if not force_refresh and current_time - self._index_last_updated < self._index_cache_duration:
                logger.info("Using cached plugin index")
                return True
            
            # 获取代理配置
            proxies = self._get_proxies()
            
            # 获取主索引
            logger.info(f"Fetching plugin index from {self._index_url}")
            try:
                response = requests.get(self._index_url, timeout=60, proxies=proxies)
                response.raise_for_status()
            except requests.Timeout:
                logger.error("网络环境差，加载插件索引超时")
                return False
            except requests.ConnectionError:
                logger.error("网络环境差，无法连接到插件索引服务器")
                return False
            except requests.RequestException as e:
                logger.error(f"网络环境差，加载插件索引失败: {e}")
                return False
            
            # 解析JSON数据
            main_data = response.json()
            
            # 构建索引
            self._index_cache = {}
            self._reverse_index = {}
            
            # 处理主索引
            for git_url, plugin_info in main_data.items():
                if git_url in self._disabled_repositories:
                    continue
                    
                if isinstance(plugin_info, list) and len(plugin_info) > 0:
                    nodes_list = plugin_info[0]
                    if isinstance(nodes_list, list):
                        self._index_cache[git_url] = nodes_list
                        
                        # 构建反向索引
                        for node in nodes_list:
                            self._reverse_index[node] = git_url
            
            # 处理用户自定义仓库
            for repo_url in self._custom_repositories:
                if repo_url in self._disabled_repositories:
                    continue
                    
                try:
                    logger.info(f"Fetching index from custom repository: {repo_url}")
                    repo_response = requests.get(repo_url, timeout=60, proxies=proxies)
                    repo_response.raise_for_status()
                    repo_data = repo_response.json()
                    
                    # 合并自定义仓库的索引
                    for git_url, plugin_info in repo_data.items():
                        if git_url in self._disabled_repositories:
                            continue
                            
                        if isinstance(plugin_info, list) and len(plugin_info) > 0:
                            nodes_list = plugin_info[0]
                            if isinstance(nodes_list, list):
                                # 如果该仓库已存在于主索引中，合并节点列表
                                if git_url in self._index_cache:
                                    self._index_cache[git_url] = list(set(self._index_cache[git_url] + nodes_list))
                                else:
                                    self._index_cache[git_url] = nodes_list
                                
                                # 更新反向索引
                                for node in nodes_list:
                                    self._reverse_index[node] = git_url
                except requests.Timeout:
                    logger.error(f"网络环境差，加载自定义仓库 {repo_url} 超时")
                    continue
                except requests.ConnectionError:
                    logger.error(f"网络环境差，无法连接到自定义仓库 {repo_url}")
                    continue
                except Exception as e:
                    logger.error(f"Failed to fetch custom repository {repo_url}: {e}")
                    continue
            
            # 添加预设的社区插件到索引和反向索引
            for plugin_id, plugin_info in self._community_plugins.items():
                git_url = plugin_info.get("git_url")
                nodes = plugin_info.get("nodes", [])
                
                # 只有当插件有Git URL和节点列表时，才添加到索引和反向索引
                if git_url and nodes:
                    # 如果该仓库已存在于索引中，合并节点列表
                    if git_url in self._index_cache:
                        self._index_cache[git_url] = list(set(self._index_cache[git_url] + nodes))
                    else:
                        self._index_cache[git_url] = nodes
                    
                    # 更新反向索引
                    for node in nodes:
                        self._reverse_index[node] = git_url
            
            self._index_last_updated = current_time
            logger.info(f"Successfully fetched and cached plugin index with {len(self._index_cache)} plugins")
            return True
        except Exception as e:
            logger.error(f"网络环境差，加载插件索引失败: {e}")
            return False
    
    def check_environment(self) -> Dict[str, Dict[str, Any]]:
        """
        检查系统环境，列出项目所需的所有工具及其状态
        
        Returns:
            环境检查结果，包含每个工具的名称、状态、版本等信息
        """
        environment_status = {
            "git": {
                "name": "Git",
                "description": "版本控制系统，用于安装插件",
                "required": True,
                "installed": False,
                "version": None,
                "installable": True,
                "error_message": None
            },
            "ffmpeg": {
                "name": "FFmpeg",
                "description": "多媒体处理工具，用于视频处理",
                "required": True,
                "installed": False,
                "version": None,
                "installable": False,
                "error_message": None
            },
            "python": {
                "name": "Python",
                "description": "编程语言，项目的运行环境",
                "required": True,
                "installed": True,
                "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "installable": False,
                "error_message": None
            },
            "python_packages": {
                "name": "Python依赖包",
                "description": "项目所需的Python第三方库",
                "required": True,
                "installed": False,
                "version": None,
                "installable": True,
                "error_message": None,
                "packages": []
            }
        }
        
        # 检查Git是否安装
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                environment_status["git"]["installed"] = True
                # 解析Git版本
                version_line = result.stdout.strip()
                if version_line.startswith("git version"):
                    environment_status["git"]["version"] = version_line[12:]
        except Exception as e:
            environment_status["git"]["error_message"] = str(e)
        
        # 检查FFmpeg是否安装
        try:
            # 优先从imageio_ffmpeg获取FFmpeg路径（与ffmpeg_manager.py保持一致）
            ffmpeg_path = None
            try:
                from imageio_ffmpeg import get_ffmpeg_exe
                ffmpeg_path = get_ffmpeg_exe()
                if ffmpeg_path and os.path.exists(ffmpeg_path):
                    # 验证FFmpeg是否可用
                    result = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        environment_status["ffmpeg"]["installed"] = True
                        # 解析FFmpeg版本
                        version_line = result.stdout.split("\n")[0]
                        if version_line.startswith("ffmpeg version"):
                            environment_status["ffmpeg"]["version"] = version_line[15:]
            except ImportError:
                # 如果imageio_ffmpeg不可用，尝试从系统PATH中查找
                result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    environment_status["ffmpeg"]["installed"] = True
                    # 解析FFmpeg版本
                    version_line = result.stdout.split("\n")[0]
                    if version_line.startswith("ffmpeg version"):
                        environment_status["ffmpeg"]["version"] = version_line[15:]
        except Exception as e:
            environment_status["ffmpeg"]["error_message"] = str(e)
        
        # 检查Python依赖包是否安装
        try:
            import pkg_resources
            
            # 读取requirements.txt文件
            requirements_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "requirements.txt")
            
            if os.path.exists(requirements_path):
                with open(requirements_path, "r") as f:
                    requirements = f.readlines()
                
                installed_packages = 0
                total_packages = 0
                
                for req_line in requirements:
                    req_line = req_line.strip()
                    if not req_line or req_line.startswith("#"):
                        continue
                    
                    total_packages += 1
                    
                    # 解析依赖包名称（忽略版本号和注释）
                    pkg_name = req_line.split("=")[0].split(">=")[0].split("<=")[0].strip()
                    
                    # 检查依赖包是否已安装
                    try:
                        pkg_resources.get_distribution(pkg_name)
                        installed = True
                        installed_packages += 1
                    except pkg_resources.DistributionNotFound:
                        installed = False
                    except Exception:
                        installed = False
                    
                    # 添加到packages列表
                    environment_status["python_packages"]["packages"].append({
                        "name": pkg_name,
                        "required": True,
                        "installed": installed
                    })
                
                # 更新python_packages的整体状态
                if total_packages > 0:
                    environment_status["python_packages"]["installed"] = (installed_packages == total_packages)
                    environment_status["python_packages"]["version"] = f"{installed_packages}/{total_packages} 已安装"
                else:
                    environment_status["python_packages"]["installed"] = True
            else:
                environment_status["python_packages"]["error_message"] = "requirements.txt文件未找到"
        except Exception as e:
            environment_status["python_packages"]["error_message"] = str(e)
        
        return environment_status
    
    def install_git(self) -> Tuple[bool, str]:
        """
        安装Git工具
        
        Returns:
            (是否成功, 错误信息)
        """
        try:
            logger.info("Attempting to install Git...")
            
            # 根据操作系统选择安装方式
            if sys.platform == "win32":
                # Windows系统：提示用户下载安装Git
                return False, "请从 https://git-scm.com/download/win 下载并安装Git"
            elif sys.platform.startswith("linux"):
                # Linux系统：使用包管理器安装
                if shutil.which("apt-get"):
                    subprocess.run(["apt-get", "update"], check=True, shell=True)
                    subprocess.run(["apt-get", "install", "-y", "git"], check=True, shell=True)
                elif shutil.which("yum"):
                    subprocess.run(["yum", "install", "-y", "git"], check=True, shell=True)
                elif shutil.which("dnf"):
                    subprocess.run(["dnf", "install", "-y", "git"], check=True, shell=True)
                else:
                    return False, "未知的Linux包管理器"
            elif sys.platform == "darwin":
                # macOS系统：使用Homebrew安装
                if shutil.which("brew"):
                    subprocess.run(["brew", "install", "git"], check=True, shell=True)
                else:
                    return False, "请先安装Homebrew"
            else:
                return False, f"不支持的操作系统：{sys.platform}"
            
            logger.info("Git installed successfully")
            return True, ""
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Git: {e}")
            return False, f"安装失败：{e}"
        except Exception as e:
            logger.error(f"Error installing Git: {e}")
            return False, f"安装过程中发生错误：{e}"
    
    async def install_python_packages(self) -> Dict[str, Any]:
        """
        安装Python依赖包，从requirements.txt文件读取依赖列表
        
        Returns:
            安装结果，包含状态和进度信息
        """
        import subprocess
        import re
        
        try:
            # 获取requirements.txt文件路径
            requirements_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "requirements.txt")
            
            if not os.path.exists(requirements_path):
                return {
                    "status": "error",
                    "message": "requirements.txt文件未找到"
                }
            
            # 运行pip install命令
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", "-r", requirements_path, "--no-cache-dir"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # 解析输出
            total_packages = 0
            processed_packages = 0
            current_package = None
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                if line:
                    # 查找总包数
                    if re.search(r"Collecting .*", line):
                        total_packages += 1
                    
                    # 查找当前处理的包
                    package_match = re.search(r"Collecting (.*?)(?:\s|$)", line)
                    if package_match:
                        current_package = package_match.group(1)
                        processed_packages += 1
                    
                    # 计算进度百分比
                    if total_packages and total_packages > 0:
                        progress = min(int((processed_packages / total_packages) * 100), 100)
                    else:
                        progress = 0
                    
                    # 生成进度数据
                    progress_data = {
                        "status": "installing",
                        "progress": progress,
                        "current_package": current_package,
                        "message": line.strip()
                    }
                    
                    # 通过WebSocket发送进度信息
                    from api.realtime.websocket_manager import manager
                    await manager.broadcast(json.dumps({
                        "type": "package_install_progress",
                        "data": progress_data
                    }))
            
            # 检查安装结果
            if process.returncode == 0:
                return {
                    "status": "success",
                    "message": "Python依赖包安装成功",
                    "progress": 100
                }
            else:
                return {
                    "status": "error",
                    "message": "Python依赖包安装失败",
                    "progress": 100
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "progress": 0
            }
            
    def add_custom_repository(self, repo_url: str) -> bool:
        """
        添加自定义仓库地址
        
        Args:
            repo_url: 自定义仓库的URL
            
        Returns:
            添加成功返回True，失败返回False
        """
        if repo_url in self._custom_repositories:
            logger.warning(f"Repository {repo_url} is already in custom repositories")
            return False
            
        self._custom_repositories.append(repo_url)
        self._save_custom_repositories()
        logger.info(f"Added custom repository: {repo_url}")
        return True
    
    def remove_custom_repository(self, repo_url: str) -> bool:
        """
        删除自定义仓库地址
        
        Args:
            repo_url: 要删除的自定义仓库URL
            
        Returns:
            删除成功返回True，失败返回False
        """
        if repo_url not in self._custom_repositories:
            logger.warning(f"Repository {repo_url} is not in custom repositories")
            return False
            
        self._custom_repositories.remove(repo_url)
        self._save_custom_repositories()
        logger.info(f"Removed custom repository: {repo_url}")
        return True
    
    def disable_repository(self, repo_url: str) -> bool:
        """
        禁用指定的仓库地址
        
        Args:
            repo_url: 要禁用的仓库URL
            
        Returns:
            禁用成功返回True，失败返回False
        """
        if repo_url in self._disabled_repositories:
            logger.warning(f"Repository {repo_url} is already disabled")
            return False
            
        # 如果仓库在自定义仓库列表中，从那里移除
        if repo_url in self._custom_repositories:
            self._custom_repositories.remove(repo_url)
        
        self._disabled_repositories.append(repo_url)
        self._save_custom_repositories()
        # 清除缓存，以便下次获取索引时应用禁用设置
        self._index_cache = {}
        self._reverse_index = {}
        self._index_last_updated = 0
        logger.info(f"Disabled repository: {repo_url}")
        return True
    
    def enable_repository(self, repo_url: str) -> bool:
        """
        启用指定的仓库地址
        
        Args:
            repo_url: 要启用的仓库URL
            
        Returns:
            启用成功返回True，失败返回False
        """
        if repo_url not in self._disabled_repositories:
            logger.warning(f"Repository {repo_url} is not disabled")
            return False
            
        self._disabled_repositories.remove(repo_url)
        
        # 将仓库添加回自定义仓库列表
        if repo_url not in self._custom_repositories:
            self._custom_repositories.append(repo_url)
            
        self._save_custom_repositories()
        # 清除缓存，以便下次获取索引时应用启用设置
        self._index_cache = {}
        self._reverse_index = {}
        self._index_last_updated = 0
        logger.info(f"Enabled repository: {repo_url}")
        return True
    
    def get_custom_repositories(self) -> List[str]:
        """
        获取用户自定义的活跃仓库地址列表（不包含已禁用的仓库）
        
        Returns:
            活跃的自定义仓库地址列表
        """
        # 返回不在禁用列表中的自定义仓库
        return [repo for repo in self._custom_repositories if repo not in self._disabled_repositories]
    
    def get_disabled_repositories(self) -> List[str]:
        """
        获取用户禁用的仓库地址列表
        
        Returns:
            禁用的仓库地址列表
        """
        return self._disabled_repositories.copy()
    
    def _get_proxies(self) -> Optional[Dict[str, str]]:
        """
        获取当前的代理配置
        
        Returns:
            代理配置字典，如果未启用代理则返回None
        """
        proxy_config = config_manager.get("proxy")
        if not proxy_config.get("enabled", False):
            return None
            
        if proxy_config.get("auto_detect", False):
            # 自动检测系统代理
            from urllib.request import getproxies
            proxies = getproxies()
            if proxies:
                logger.info(f"Using auto-detected system proxy: {proxies}")
            else:
                logger.info("No system proxy detected")
            return proxies if proxies else None
        else:
            # 使用手动配置的代理
            protocol = proxy_config.get("protocol", "http")
            host = proxy_config.get("host", "127.0.0.1")
            port = proxy_config.get("port", 7890)
            username = proxy_config.get("username")
            password = proxy_config.get("password")
            
            if username and password:
                proxy_url = f"{protocol}://{username}:{password}@{host}:{port}"
            else:
                proxy_url = f"{protocol}://{host}:{port}"
            
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            logger.info(f"Using manual proxy: {proxy_url}")
            return proxies
    
    def find_plugin_for_node(self, node_type: str) -> Optional[str]:
        """
        查找提供指定节点的插件
        
        Args:
            node_type: 节点类型名称
            
        Returns:
            插件的Git URL，如果未找到则返回None
        """
        # 确保索引已加载
        if not self._reverse_index and not self._index_cache:
            # 如果索引为空，尝试同步加载
            try:
                proxies = self._get_proxies()
                response = requests.get(self._index_url, timeout=30, proxies=proxies)
                response.raise_for_status()
                index_data = response.json()
                
                # 构建反向索引
                for git_url, nodes in index_data.items():
                    if git_url in self._disabled_repositories:
                        continue
                    
                    for node in nodes:
                        self._reverse_index[node] = git_url
                        
                # 加载用户自定义仓库
                for repo_url in self._custom_repositories:
                    if repo_url in self._disabled_repositories:
                        continue
                        
                    try:
                        proxies = self._get_proxies()
                        repo_response = requests.get(repo_url, timeout=30, proxies=proxies)
                        repo_response.raise_for_status()
                        repo_data = repo_response.json()
                        
                        for git_url, nodes in repo_data.items():
                            if git_url in self._disabled_repositories:
                                continue
                            
                            for node in nodes:
                                self._reverse_index[node] = git_url
                    except Exception as e:
                        logger.error(f"Failed to fetch custom repository {repo_url}: {e}")
                        continue
                        
                logger.info("Fetched plugin index synchronously for lookup")
            except Exception as e:
                logger.error(f"Error fetching plugin index for lookup: {e}")
                return None
        
        return self._reverse_index.get(node_type)
        
    def get_missing_nodes_plugins(self, missing_nodes: List[str]) -> Dict[str, str]:
        """
        获取缺失节点对应的插件
        
        Args:
            missing_nodes: 缺失的节点列表
            
        Returns:
            节点类型到插件Git URL的映射
        """
        result = {}
        for node in missing_nodes:
            git_url = self.find_plugin_for_node(node)
            if git_url:
                result[node] = git_url
        return result

    async def install_plugin(self, git_url: str) -> tuple[bool, str]:
        """
        安装插件或ComfyUI扩展
        
        Args:
            git_url: 插件的Git仓库URL
            
        Returns:
            安装成功返回(True, ""), 失败返回(False, 错误信息)
        """
        try:
            # 从Git URL获取插件名称
            plugin_name = git_url.split("/")[-1].replace(".git", "")
            
            logger.info(f"Attempting to install plugin/extension from {git_url}")
            
            # 检查git命令是否可用
            try:
                subprocess.check_output(["git", "--version"], stderr=subprocess.STDOUT)
                logger.info("Git command found")
            except (subprocess.CalledProcessError, FileNotFoundError) as git_err:
                error_msg = f"Git command not found or not working: {git_err}"
                logger.error(error_msg)
                return False, error_msg
            
            # 检查是否为ComfyUI扩展
            is_comfyui_extension = False
            try:
                # 查看仓库的根目录结构，判断是否为ComfyUI扩展
                # 使用git ls-remote查看仓库文件
                subprocess.check_output(["git", "ls-remote", "--quiet", git_url], shell=True)
                
                # 克隆到临时目录进行分析
                temp_dir = os.path.join(tempfile.gettempdir(), f"comfyui_ext_check_{uuid.uuid4()}")
                os.makedirs(temp_dir, exist_ok=True)
                
                subprocess.check_call(["git", "clone", "--depth", "1", git_url, temp_dir], shell=True)
                
                # 检查是否包含ComfyUI扩展的特征文件
                if os.path.exists(os.path.join(temp_dir, "__init__.py")):
                    with open(os.path.join(temp_dir, "__init__.py"), "r", encoding="utf-8") as f:
                        content = f.read()
                        # 检查是否包含ComfyUI扩展的典型代码
                        if "NODE_CLASS_MAPPINGS" in content or "NODE_DISPLAY_NAME_MAPPINGS" in content:
                            is_comfyui_extension = True
                
                # 清理临时目录
                shutil.rmtree(temp_dir)
            except Exception as check_err:
                logger.warning(f"Error checking if repository is ComfyUI extension: {check_err}")
            
            if is_comfyui_extension:
                logger.info(f"Repository {git_url} identified as ComfyUI extension")
                
                # 安装ComfyUI扩展
                # 默认安装到custom_nodes目录
                custom_nodes_dir = os.path.abspath("custom_nodes")
                os.makedirs(custom_nodes_dir, exist_ok=True)
                extension_path = os.path.join(custom_nodes_dir, plugin_name)
                
                # 克隆仓库
                try:
                    subprocess.check_call(["git", "clone", git_url, extension_path], shell=True)
                    logger.info(f"Successfully cloned ComfyUI extension to {extension_path}")
                except subprocess.CalledProcessError as clone_err:
                    error_msg = f"Error cloning ComfyUI extension {git_url}: {clone_err}"
                    logger.error(error_msg)
                    return False, error_msg
                
                # 安装依赖
                requirements_file = os.path.join(extension_path, "requirements.txt")
                if os.path.exists(requirements_file):
                    logger.info(f"Installing dependencies for ComfyUI extension from {requirements_file}")
                    try:
                        subprocess.check_call([
                            sys.executable, "-m", "pip", "install", "-r", requirements_file
                        ])
                        logger.info(f"Successfully installed dependencies for ComfyUI extension {plugin_name}")
                    except subprocess.CalledProcessError as pip_err:
                        logger.error(f"Error installing dependencies for ComfyUI extension {plugin_name}: {pip_err}")
                        # 依赖安装失败不影响插件安装，继续执行
                
                logger.info(f"Installed ComfyUI extension: {plugin_name}")
                return True, ""
            else:
                # 安装普通插件
                logger.info(f"Repository {git_url} identified as regular plugin")
                
                # 确保有插件目录
                if not self._plugin_dirs:
                    default_plugin_dir = os.path.abspath("plugins")
                    self.add_plugin_dir(default_plugin_dir)
                    plugin_path = os.path.join(default_plugin_dir, plugin_name)
                else:
                    plugin_path = os.path.join(self._plugin_dirs[0], plugin_name)
                
                # 确保插件目录存在
                os.makedirs(self._plugin_dirs[0], exist_ok=True)
                
                # 克隆仓库
                try:
                    subprocess.check_call(["git", "clone", git_url, plugin_path], shell=True)
                    logger.info(f"Successfully cloned repository to {plugin_path}")
                except subprocess.CalledProcessError as clone_err:
                    error_msg = f"Error cloning repository {git_url}: {clone_err}"
                    logger.error(error_msg)
                    return False, error_msg
                
                # 安装依赖
                requirements_file = os.path.join(plugin_path, "requirements.txt")
                if os.path.exists(requirements_file):
                    logger.info(f"Installing dependencies from {requirements_file}")
                    try:
                        subprocess.check_call([
                            sys.executable, "-m", "pip", "install", "-r", requirements_file
                        ])
                        logger.info(f"Successfully installed dependencies for plugin {plugin_name}")
                    except subprocess.CalledProcessError as pip_err:
                        logger.error(f"Error installing dependencies for plugin {plugin_name}: {pip_err}")
                        # 依赖安装失败不影响插件安装，继续执行
                
                # 发现并加载新插件
                await self.discover_plugins()
                logger.info(f"Installed plugin: {plugin_name}")
                return True, ""
        except Exception as e:
            error_msg = f"Error installing plugin/extension {git_url}: {e}"
            logger.error(error_msg)
            return False, error_msg

    async def uninstall_plugin(self, plugin_id: str) -> bool:
        """
        卸载插件
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            卸载成功返回True，失败返回False
        """
        try:
            # 检查插件是否已加载
            if plugin_id not in self._loaded_plugins:
                logger.warning(f"Plugin {plugin_id} is not loaded")
                return False
            
            plugin_path = self._loaded_plugins[plugin_id]
            
            # 卸载插件
            await self.unload_plugin(plugin_id)
            
            # 删除插件目录
            if os.path.exists(plugin_path):
                shutil.rmtree(plugin_path)
            
            logger.info(f"Uninstalled plugin: {plugin_id}")
            return True
        except Exception as e:
            logger.error(f"Error uninstalling plugin {plugin_id}: {e}")
            return False

    def restart_required(self) -> bool:
        """
        检查是否需要重启服务
        
        Returns:
            需要重启返回True，否则返回False
        """
        # 简单实现：如果有新的Python依赖或新模块，返回True
        # 实际实现可以更复杂，比如检查是否有模块需要重新加载
        return False
        
    def find_plugin_by_node_id(self, node_id: str) -> Optional[str]:
        """
        根据节点ID查找对应的插件Git URL
        
        Args:
            node_id: 节点ID
            
        Returns:
            插件的Git URL，如果找不到返回None
        """
        # 首先检查反向索引
        if node_id in self._reverse_index:
            return self._reverse_index[node_id]
        
        logger.info(f"Node {node_id} not found in reverse index")
        return None
        
    async def ensure_index_loaded(self) -> bool:
        """
        确保插件索引已加载
        
        Returns:
            索引加载成功返回True，失败返回False
        """
        if not self._index_cache or time.time() - self._index_last_updated > self._index_cache_duration:
            return await self.fetch_and_cache_index()
        return True

    async def _load_plugin_metadata(self, plugin_path: str) -> Optional[str]:
        """
        加载插件元数据
        
        Args:
            plugin_path: 插件路径
            
        Returns:
            插件ID，如果加载失败则返回None
        """
        try:
            # 确定插件类型（目录或文件）
            if os.path.isdir(plugin_path):
                module_name = os.path.basename(plugin_path)
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    os.path.join(plugin_path, "__init__.py")
                )
            else:
                module_name = os.path.splitext(os.path.basename(plugin_path))[0]
                spec = importlib.util.spec_from_file_location(
                    module_name,
                    plugin_path
                )
            
            if not spec or not spec.loader:
                logger.error(f"Could not create module spec for {plugin_path}")
                return None
            
            # 加载模块
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # 查找Module子类
            module_class: Optional[Type[Module]] = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Module) and attr is not Module:
                    module_class = attr
                    break
            
            if not module_class:
                logger.error(f"No Module subclass found in {plugin_path}")
                return None
            
            # 检查模块是否有METADATA属性
            if hasattr(module, "METADATA") and isinstance(module.METADATA, ModuleMetadata):
                metadata = module.METADATA
                
                # 创建模块加载器
                def loader() -> Module:
                    return module_class(metadata)
                
                # 注册模块加载器
                self.register_module_loader(metadata.id, loader)
                
                logger.info(f"Discovered plugin: {metadata.id} ({metadata.name} v{metadata.version})")
                return metadata.id
            else:
                logger.error(f"No METADATA found in {plugin_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading plugin metadata from {plugin_path}: {e}")
            return None


# 创建全局插件管理器实例
plugin_manager = PluginManager()
