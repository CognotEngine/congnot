

from typing import Dict, Any, Callable, Type, Optional, TypeVar, Union
from pydantic import BaseModel
from .base_node import BaseNode

NodeType = Union[Callable, Type[BaseNode]]

class NodeRegistry:
    
    
    def __init__(self):
        
        self._nodes: Dict[str, Dict[str, Any]] = {}
        
        self._node_functions: Dict[str, Callable] = {}
        
        self._node_rollback_functions: Dict[str, Callable] = {}
    
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
        
        return node_type not in self._nodes and node_type not in self._node_functions
    
    def clear_all_nodes(self) -> int:
        
        count = len(self._nodes)
        self._nodes.clear()
        self._node_functions.clear()
        self._node_rollback_functions.clear()
        return count

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
