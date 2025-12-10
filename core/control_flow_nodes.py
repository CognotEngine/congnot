

from .node_registry import register_node

@register_node(
    name="condition",
    description="Conditional Branch Node - Determines execution path based on condition",
    inputs={"condition": bool, "true_path": str, "false_path": str},
    outputs={"result": bool, "next_path": str},
    category="control",
    icon="🔀"
)
def condition_node(condition: bool = False, true_path: str = "", false_path: str = "") -> dict:
    
    next_path = true_path if condition else false_path
    return {"result": condition, "next_path": next_path}

@register_node(
    name="loop_start",
    description="Loop Start Node - Marks the beginning of a loop",
    inputs={"iterable": list, "index": int},
    outputs={"current_value": any, "index": int, "has_next": bool},
    category="control",
    icon="🔄"
)
def loop_start_node(iterable: list = [], index: int = 0) -> dict:
    
    if index < len(iterable):
        return {
            "current_value": iterable[index],
            "index": index,
            "has_next": True
        }
    else:
        return {
            "current_value": None,
            "index": index,
            "has_next": False
        }

@register_node(
    name="loop_end",
    description="Loop End Node - Marks the end of a loop",
    inputs={"has_next": bool, "index": int}, 
    outputs={"next_index": int, "continue_loop": bool},
    category="control",
    icon="🔚"
)
def loop_end_node(has_next: bool = False, index: int = 0) -> dict:
    
    if has_next:
        return {
            "next_index": index + 1,
            "continue_loop": True
        }
    else:
        return {
            "next_index": index,
            "continue_loop": False
        }
