

from typing import Dict, Any, Callable, Type, Optional, TypeVar, Union, List
import json
import os
import shutil
import subprocess
from pydantic import BaseModel
from .base_node import BaseNode

NodeType = Union[Callable, Type[BaseNode]]

class NodeRegistry:
    
    def __init__(self, metadata_file: str = "node_metadata.json"):
        
        self._nodes: Dict[str, Dict[str, Any]] = {}
        
        self._node_functions: Dict[str, Callable] = {}
        
        self._node_rollback_functions: Dict[str, Callable] = {}
        
        self.metadata_file = os.path.join(os.getcwd(), metadata_file)
        
        self.third_party_repos: List[Dict[str, Any]] = []
        
        self.third_party_nodes_dir = os.path.join(os.getcwd(), "third_party_nodes")
        
        self._load_metadata()
        
        self._load_third_party_repos()
    
    def _load_metadata(self):
        """加载节点元数据"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    self._nodes = metadata.get("nodes", {})
            except Exception as e:
                print(f"Failed to load node metadata: {e}")
    
    def _save_metadata(self):
        """保存节点元数据"""
        try:
            metadata = {
                "nodes": self._nodes
            }
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save node metadata: {e}")
    
    def _load_third_party_repos(self):
        """加载第三方节点仓库配置"""
        repos_file = os.path.join(os.getcwd(), "third_party_repos.json")
        if os.path.exists(repos_file):
            try:
                with open(repos_file, 'r', encoding='utf-8') as f:
                    self.third_party_repos = json.load(f)
            except Exception as e:
                print(f"Failed to load third party repos: {e}")
        else:
            # 初始化默认仓库列表
            self.third_party_repos = [
                {
                    "name": "AI-Nodes",
                    "url": "https://github.com/AI-Nodes/AI-Nodes.git",
                    "description": "A collection of AI nodes for Cognot"
                }
            ]
            self._save_third_party_repos()
    
    def _save_third_party_repos(self):
        """保存第三方节点仓库配置"""
        repos_file = os.path.join(os.getcwd(), "third_party_repos.json")
        try:
            with open(repos_file, 'w', encoding='utf-8') as f:
                json.dump(self.third_party_repos, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save third party repos: {e}")
    def register_node(
        self,
        *args,
        **kwargs
    ) -> Union[Callable, NodeType]:
        
        
        if args and isinstance(args[0], (Callable, type)):
            
            obj = args[0]
            name = kwargs.get("name")
            description = kwargs.get("description")
            inputs = kwargs.get("inputs")
            outputs = kwargs.get("outputs")
            category = kwargs.get("category", "general")
            icon = kwargs.get("icon")
            
            
            if name is None:
                if hasattr(obj, "__name__"):
                    name = obj.__name__.lower()
                else:
                    raise ValueError("Must provide node name")
            
            if description is None:
                description = obj.__doc__ if obj.__doc__ else f"Node {name}"
        else:
            
            name = kwargs.get("name")
            description = kwargs.get("description")
            inputs = kwargs.get("inputs")
            outputs = kwargs.get("outputs")
            category = kwargs.get("category", "general")
            icon = kwargs.get("icon")
            
            def decorator(obj: NodeType) -> NodeType:
                
                if isinstance(obj, type) and issubclass(obj, BaseNode):
                    
                    node_class = obj
                    
                    
                    input_schema = node_class.get_input_schema()
                    output_schema = node_class.get_output_schema()
                    
                    
                    input_types = {}
                for prop_name, prop in input_schema["properties"].items():
                    if "type" in prop:
                        input_types[prop_name] = prop["type"]
                    else:
                        input_types[prop_name] = "any"
                
                    output_types = {}
                    for prop_name, prop in output_schema.get("properties", {}).items():
                        if "type" in prop:
                            output_types[prop_name] = prop["type"]
                        else:
                            output_types[prop_name] = "any"
                    
                    
                    self._nodes[name] = {
                        "name": name,
                        "description": description,
                        "inputs": input_types,
                        "outputs": output_types,
                        "input_schema": input_schema,
                        "output_schema": output_schema,
                        "category": category,
                        "icon": icon,
                        "is_class": True
                    }
                    
                    
                    def node_factory(**kwargs):
                        node_instance = node_class()
                        return node_instance(**kwargs)
                    
                    
                    self._node_functions[name] = node_factory
                    
                else:
                    
                    func = obj
                    
                    
                    self._nodes[name] = {
                        "name": name,
                        "description": description,
                        "inputs": inputs or {},
                        "outputs": outputs or {},
                        "category": category,
                        "icon": icon,
                        "function_name": func.__name__,
                        "is_class": False
                    }
                    
                    
                    self._node_functions[name] = func
                
                self._save_metadata()
                return obj
        
        if args and isinstance(args[0], (Callable, type)):
            
            
            if isinstance(obj, type) and issubclass(obj, BaseNode):
                
                node_class = obj
                
                
                input_schema = node_class.get_input_schema()
                output_schema = node_class.get_output_schema()
                
                
                input_types = {}
                for prop_name, prop in input_schema["properties"].items():
                    if "type" in prop:
                        input_types[prop_name] = prop["type"]
                    else:
                        input_types[prop_name] = "any"
                
                output_types = {}
                for prop_name, prop in output_schema.get("properties", {}).items():
                    if "type" in prop:
                        output_types[prop_name] = prop["type"]
                    else:
                        output_types[prop_name] = "any"
                    
                    
                    self._nodes[name] = {
                        "name": name,
                        "description": description,
                        "inputs": input_types,
                        "outputs": output_types,
                        "input_schema": input_schema,
                        "output_schema": output_schema,
                        "category": category,
                        "icon": icon,
                        "is_class": True
                    }
                    
                    
                    def node_factory(**kwargs):
                        node_instance = node_class()
                        return node_instance(**kwargs)
                    
                    
                    self._node_functions[name] = node_factory
                
            else:
                
                func = obj
                
                
                self._nodes[name] = {
                    "name": name,
                    "description": description,
                    "inputs": inputs or {},
                    "outputs": outputs or {},
                    "category": category,
                    "icon": icon,
                    "function_name": func.__name__,
                    "is_class": False
                }
                
                
                self._node_functions[name] = func
            
            self._save_metadata()
            return obj
        else:
            
            return decorator
        
    def register_rollback_function(self, node_type: str) -> Callable:
        
        def decorator(func: Callable) -> Callable:
            
            self._node_rollback_functions[node_type] = func
            return func
        
        return decorator
    
    def get_node_metadata(self, node_type: str) -> Optional[Dict[str, Any]]:
        
        return self._nodes.get(node_type)
    
    def get_node_function(self, node_type: str) -> Optional[Callable]:
        
        return self._node_functions.get(node_type)
        
    def get_node_rollback_function(self, node_type: str) -> Optional[Callable]:
        
        return self._node_rollback_functions.get(node_type)
    
    def get_all_nodes(self) -> Dict[str, Dict[str, Any]]:
        
        
        nodes_copy = self._nodes.copy()
        
        
        for node_name, node_data in nodes_copy.items():
            
            if not node_data.get("is_class", False):
                
                if "inputs" in node_data and node_data["inputs"]:
                    nodes_copy[node_name]["inputs"] = {
                        k: v.__name__ if hasattr(v, "__name__") else str(v)
                        for k, v in node_data["inputs"].items()
                    }
                
                
                if "outputs" in node_data and node_data["outputs"]:
                    nodes_copy[node_name]["outputs"] = {
                        k: v.__name__ if hasattr(v, "__name__") else str(v)
                        for k, v in node_data["outputs"].items()
                    }
            
        # 确保所有节点都有category字段
        for node_name, node_data in nodes_copy.items():
            if "category" not in node_data:
                nodes_copy[node_name]["category"] = "general"
        
        return nodes_copy
    
    def load_custom_nodes(self, module_path: str) -> None:
        
        import importlib
        try:
            
            module = importlib.import_module(module_path)
            
        except ImportError as e:
            raise RuntimeError(f"Failed to load custom nodes from {module_path}: {e}")
    
    def remove_node(self, node_type: str) -> bool:
        
        if node_type in self._nodes:
            del self._nodes[node_type]
        
        if node_type in self._node_functions:
            del self._node_functions[node_type]
        
        if node_type in self._node_rollback_functions:
            del self._node_rollback_functions[node_type]
        
        self._save_metadata()
        return node_type not in self._nodes and node_type not in self._node_functions
    
    def clear_all_nodes(self) -> int:
        
        count = len(self._nodes)
        self._nodes.clear()
        self._node_functions.clear()
        self._node_rollback_functions.clear()
        
        self._save_metadata()
        return count
    
    def validate_workflow(self, workflow: Dict[str, Any]) -> List[str]:
        """验证工作流中使用的节点是否都已安装"""
        missing_nodes = []
        
        if "nodes" in workflow:
            for node in workflow["nodes"]:
                node_type = node.get("type")
                if node_type and node_type not in self._nodes:
                    if node_type not in missing_nodes:
                        missing_nodes.append(node_type)
        
        return missing_nodes
    
    def add_third_party_repo(self, repo: Dict[str, Any]) -> None:
        """添加第三方节点仓库"""
        if repo not in self.third_party_repos:
            self.third_party_repos.append(repo)
            self._save_third_party_repos()
    
    def remove_third_party_repo(self, repo_url: str) -> None:
        """移除第三方节点仓库"""
        self.third_party_repos = [repo for repo in self.third_party_repos if repo["url"] != repo_url]
        self._save_third_party_repos()
    
    def get_third_party_repos(self) -> List[Dict[str, Any]]:
        """获取所有第三方节点仓库"""
        return self.third_party_repos
    
    def install_third_party_nodes(self, repo_url: str) -> Dict[str, Any]:
        """安装第三方节点"""
        result = {
            "success": False,
            "message": ""
        }
        
        try:
            # 创建第三方节点目录
            if not os.path.exists(self.third_party_nodes_dir):
                os.makedirs(self.third_party_nodes_dir)
            
            # 解析仓库名称
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            repo_dir = os.path.join(self.third_party_nodes_dir, repo_name)
            
            # 克隆仓库
            if os.path.exists(repo_dir):
                # 如果已经存在，更新仓库
                subprocess.run(["git", "pull"], cwd=repo_dir, check=True)
            else:
                # 克隆新仓库
                subprocess.run(["git", "clone", repo_url], cwd=self.third_party_nodes_dir, check=True)
            
            # 安装依赖
            requirements_file = os.path.join(repo_dir, "requirements.txt")
            if os.path.exists(requirements_file):
                subprocess.run(["pip", "install", "-r", requirements_file], check=True)
            
            # 加载节点
            self.load_custom_nodes_from_dir(repo_dir)
            
            result["success"] = True
            result["message"] = f"Successfully installed/updated nodes from {repo_url}"
            
        except Exception as e:
            result["message"] = f"Failed to install nodes from {repo_url}: {str(e)}"
        
        return result
    
    def uninstall_third_party_nodes(self, repo_name: str) -> Dict[str, Any]:
        """卸载第三方节点"""
        result = {
            "success": False,
            "message": ""
        }
        
        try:
            repo_dir = os.path.join(self.third_party_nodes_dir, repo_name)
            
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir)
                result["success"] = True
                result["message"] = f"Successfully uninstalled nodes from {repo_name}"
            else:
                result["message"] = f"Repo {repo_name} not found"
        except Exception as e:
            result["message"] = f"Failed to uninstall nodes: {str(e)}"
        
        return result
    
    def load_custom_nodes_from_dir(self, dir_path: str) -> None:
        """从目录加载自定义节点"""
        if not os.path.exists(dir_path):
            return
        
        # 添加目录到Python路径
        import sys
        sys.path.append(dir_path)
        
        # 扫描所有Python文件
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".py") and not file.startswith("_"):
                    # 导入模块
                    module_name = file[:-3]
                    try:
                        import importlib
                        importlib.import_module(module_name)
                    except Exception as e:
                        print(f"Failed to import module {module_name}: {e}")

_node_registry = NodeRegistry()

def register_node(*args, **kwargs) -> Callable:
    
    return _node_registry.register_node(*args, **kwargs)

def get_node_metadata(node_type: str) -> Optional[Dict[str, Any]]:
    
    return _node_registry.get_node_metadata(node_type)

def get_node_function(node_type: str) -> Optional[Callable]:
    
    return _node_registry.get_node_function(node_type)

def get_node_rollback_function(node_type: str) -> Optional[Callable]:
    
    return _node_registry.get_node_rollback_function(node_type)

def register_rollback_function(node_type: str) -> Callable:
    
    return _node_registry.register_rollback_function(node_type)

def get_all_nodes() -> Dict[str, Dict[str, Any]]:
    
    return _node_registry.get_all_nodes()

def load_custom_nodes(module_path: str) -> None:
    
    return _node_registry.load_custom_nodes(module_path)

def load_third_party_ai_nodes():
    """加载第三方AI节点"""
    try:
        from .ai_node_adapter import ai_node_adapter
        ai_node_adapter.convert_all_nodes()
    except Exception as e:
        print(f"Failed to load third-party AI nodes: {e}")
        import traceback
        traceback.print_exc()

def remove_node(node_type: str) -> bool:
    
    return _node_registry.remove_node(node_type)

def clear_all_nodes() -> int:
    
    return _node_registry.clear_all_nodes()
