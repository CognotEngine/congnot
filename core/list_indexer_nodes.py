from typing import Dict, Any, Optional, List
from core.node_registry import register_node
from core.base_node import BaseNode, text_input, slider


@register_node(
    name="list_indexer",
    description="Extract a specific element from a list by index",
    category="utility",
    icon="📋"
)
class ListIndexerNode(BaseNode):
    """Node to extract a specific element from a list by index."""

    class Inputs(BaseNode.Inputs):
        input_list: List[Any] = BaseNode.Inputs.List(description="Input list to extract from")
        index: int = slider(
            default=0,
            min=0,
            max=10,
            step=1,
            description="Index of the element to extract"
        )
        fallback_value: Any = BaseNode.Inputs.Any(
            default="",
            description="Fallback value if index is out of range"
        )

    class Outputs(BaseNode.Outputs):
        element: Any
        index: int
        success: bool
        message: str

    def __call__(self, input_list: List[Any] = None,
                 index: int = 0,
                 fallback_value: Any = "") -> dict:
        """Extract element from list by index."""
        try:
            if input_list is None:
                input_list = []

            if not isinstance(input_list, list):
                raise ValueError("Input must be a list")

            if index < 0 or index >= len(input_list):
                return {
                    "element": fallback_value,
                    "index": index,
                    "success": False,
                    "message": f"Index {index} out of range for list of length {len(input_list)}"
                }

            element = input_list[index]
            return {
                "element": element,
                "index": index,
                "success": True,
                "message": f"Successfully extracted element at index {index}"
            }

        except Exception as e:
            print(f"Error in ListIndexerNode: {e}")
            return {
                "element": fallback_value,
                "index": index,
                "success": False,
                "message": f"Error extracting element: {str(e)}"
            }


@register_node(
    name="list_splitter",
    description="Split a list into multiple individual outputs",
    category="utility",
    icon="✂️"
)
class ListSplitterNode(BaseNode):
    """Node to split a list into multiple individual outputs."""

    class Inputs(BaseNode.Inputs):
        input_list: List[Any] = BaseNode.Inputs.List(description="Input list to split")
        output_count: int = slider(
            default=6,
            min=1,
            max=12,
            step=1,
            description="Number of output elements to generate"
        )

    class Outputs(BaseNode.Outputs):
        # Dynamic outputs based on output_count
        pass

    def __init__(self, **kwargs):
        """Initialize the node with dynamic outputs."""
        super().__init__(**kwargs)
        # Set up dynamic outputs
        self.outputs = {}
        for i in range(12):  # Max 12 outputs
            self.outputs[f"element_{i+1}"] = (Any, f"Element {i+1} from list")
        self.outputs["success"] = (bool, "Operation success status")
        self.outputs["message"] = (str, "Operation message")

    def __call__(self, input_list: List[Any] = None,
                 output_count: int = 6) -> dict:
        """Split list into multiple outputs."""
        try:
            if input_list is None:
                input_list = []

            if not isinstance(input_list, list):
                raise ValueError("Input must be a list")

            result = {}
            
            # Generate outputs based on output_count
            for i in range(output_count):
                if i < len(input_list):
                    result[f"element_{i+1}"] = input_list[i]
                else:
                    result[f"element_{i+1}"] = None

            # Fill remaining outputs with None
            for i in range(output_count, 12):
                result[f"element_{i+1}"] = None

            result["success"] = True
            result["message"] = f"Successfully split list into {output_count} elements"

            return result

        except Exception as e:
            print(f"Error in ListSplitterNode: {e}")
            result = {}
            
            # Fill all outputs with None on error
            for i in range(12):
                result[f"element_{i+1}"] = None
                
            result["success"] = False
            result["message"] = f"Error splitting list: {str(e)}"
            
            return result


@register_node(
    name="list_combiner",
    description="Combine multiple elements into a single list",
    category="utility",
    icon="📦"
)
class ListCombinerNode(BaseNode):
    """Node to combine multiple elements into a single list."""

    class Inputs(BaseNode.Inputs):
        element_1: Any = BaseNode.Inputs.Any(default=None, description="Element 1")
        element_2: Any = BaseNode.Inputs.Any(default=None, description="Element 2")
        element_3: Any = BaseNode.Inputs.Any(default=None, description="Element 3")
        element_4: Any = BaseNode.Inputs.Any(default=None, description="Element 4")
        element_5: Any = BaseNode.Inputs.Any(default=None, description="Element 5")
        element_6: Any = BaseNode.Inputs.Any(default=None, description="Element 6")
        element_7: Any = BaseNode.Inputs.Any(default=None, description="Element 7")
        element_8: Any = BaseNode.Inputs.Any(default=None, description="Element 8")

    class Outputs(BaseNode.Outputs):
        output_list: List[Any]
        length: int
        success: bool
        message: str

    def __call__(self, **kwargs) -> dict:
        """Combine input elements into a list."""
        try:
            # Collect all elements from kwargs
            elements = []
            for i in range(1, 9):
                key = f"element_{i}"
                if key in kwargs:
                    element = kwargs[key]
                    if element is not None:
                        elements.append(element)

            return {
                "output_list": elements,
                "length": len(elements),
                "success": True,
                "message": f"Successfully combined {len(elements)} elements into a list"
            }

        except Exception as e:
            print(f"Error in ListCombinerNode: {e}")
            return {
                "output_list": [],
                "length": 0,
                "success": False,
                "message": f"Error combining elements: {str(e)}"
            }


@register_node(
    name="video_batch_processor",
    description="Process multiple video paths and combine them into a batch",
    category="video",
    icon="🎞️"
)
class VideoBatchProcessorNode(BaseNode):
    """Node to process multiple video paths and combine them into a batch."""

    class Inputs(BaseNode.Inputs):
        video_1: str = BaseNode.Inputs.Path(description="Path to video 1")
        video_2: str = BaseNode.Inputs.Path(description="Path to video 2")
        video_3: str = BaseNode.Inputs.Path(description="Path to video 3")
        video_4: str = BaseNode.Inputs.Path(description="Path to video 4")
        video_5: str = BaseNode.Inputs.Path(description="Path to video 5")
        video_6: str = BaseNode.Inputs.Path(description="Path to video 6")
        output_path: str = BaseNode.Inputs.Path(description="Output path for the combined video")
        batch_name: str = text_input(default="video_batch", description="Name for the video batch")

    class Outputs(BaseNode.Outputs):
        video_batch: List[str]
        batch_name: str
        output_path: str
        success: bool
        message: str

    def __call__(self, **kwargs) -> dict:
        """Process multiple video paths into a batch."""
        try:
            # Collect all video paths from kwargs
            video_paths = []
            for i in range(1, 7):
                key = f"video_{i}"
                if key in kwargs:
                    path = kwargs[key]
                    if path and path.strip():
                        video_paths.append(path)

            output_path = kwargs.get("output_path", "")
            batch_name = kwargs.get("batch_name", "video_batch")

            return {
                "video_batch": video_paths,
                "batch_name": batch_name,
                "output_path": output_path,
                "success": True,
                "message": f"Successfully processed {len(video_paths)} videos into batch '{batch_name}'"
            }

        except Exception as e:
            print(f"Error in VideoBatchProcessorNode: {e}")
            return {
                "video_batch": [],
                "batch_name": "",
                "output_path": "",
                "success": False,
                "message": f"Error processing video batch: {str(e)}"
            }
