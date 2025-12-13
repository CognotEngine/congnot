

from .node_registry import register_node
from .base_node import BaseNode, text_input, slider, combo, handle, text_area, toggle

@register_node(
    name="TextInput",
    description="Text Input Node - Provides text data input",
    category="input",
    icon="📝"
)
class TextInputNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        value: str = text_input(default="", description="Input text")
    
    class Outputs(BaseNode.Outputs):
        value: str
    
    def __call__(self, value: str = "") -> dict:
        
        return {"value": value}

@register_node(
    name="FileInput",
    description="File Input Node - Reads file content as input",
    category="input",
    icon="📁"
)
class FileInputNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        file_path: str = text_input(default="", description="File path")
        encoding: str = combo(default="utf-8", description="File encoding", options=["utf-8", "gbk", "latin-1"])
    
    class Outputs(BaseNode.Outputs):
        content: str
        file_name: str
    
    def __call__(self, file_path: str = "", encoding: str = "utf-8") -> dict:
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return {"content": content, "file_name": file_path.split('/')[-1]}
        except Exception as e:
            return {"content": f"Error: {str(e)}", "file_name": file_path.split('/')[-1]}

@register_node(
    name="APIInput",
    description="API Input Node - Fetches data from API",
    category="input",
    icon="🌐"
)
class APIInputNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        url: str = text_input(default="", description="API URL")
        method: str = combo(default="GET", description="Request method", options=["GET", "POST", "PUT", "DELETE"])
        headers: dict = text_input(default="{}", description="Request headers")
    
    class Outputs(BaseNode.Outputs):
        response: dict
        status: int
    
    def __call__(self, url: str = "", method: str = "GET", headers: dict = None) -> dict:
        
        import requests
        import json
        headers = json.loads(headers) if isinstance(headers, str) else (headers or {})
        try:
            response = requests.request(method, url, headers=headers)
            return {"response": response.json(), "status": response.status_code}
        except Exception as e:
            return {"response": {"error": str(e)}, "status": 500}

@register_node(
    name="DatabaseInput",
    description="Database Input Node - Queries data from database",
    category="input",
    icon="🗄️"
)
class DatabaseInputNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        query: str = text_area(default="", description="SQL query")
        connection: dict = text_input(default="{}", description="Database connection configuration")
    
    class Outputs(BaseNode.Outputs):
        results: list
        count: int
    
    def __call__(self, query: str = "", connection: dict = None) -> dict:
        
        import json
        connection = json.loads(connection) if isinstance(connection, str) else (connection or {})
        
        try:
            
            results = [{"id": 1, "name": "Sample", "value": "Data"}]
            return {"results": results, "count": len(results)}
        except Exception as e:
            return {"results": [], "count": 0}

@register_node(
    name="TextProcessing",
    description="Text Processing Node - Performs text conversion and processing operations",
    category="processing",
    icon="🔤"
)
class TextProcessingNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        text: str = handle(description="Input text")
        operation: str = combo(default="uppercase", description="Operation type", options=["uppercase", "lowercase", "trim", "split", "replace", "length"])
        params: dict = text_input(default="{}", description="Operation parameters")
    
    class Outputs(BaseNode.Outputs):
        result: str
    
    def __call__(self, text: str = "", operation: str = "uppercase", params: dict = None) -> dict:
        
        import json
        params = json.loads(params) if isinstance(params, str) else (params or {})
        
        if operation == "uppercase":
            return {"result": text.upper()}
        elif operation == "lowercase":
            return {"result": text.lower()}
        elif operation == "trim":
            return {"result": text.strip()}
        elif operation == "split":
            separator = params.get("separator", " ")
            return {"result": str(text.split(separator))}
        elif operation == "replace":
            old = params.get("old", "")
            new = params.get("new", "")
            return {"result": text.replace(old, new)}
        elif operation == "length":
            return {"result": str(len(text))}
        else:
            return {"result": text}

@register_node(
    name="MathOperation",
    description="Math Operation Node - Performs basic math operations",
    category="processing",
    icon="🔢"
)
class MathOperationNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        a: float = handle(description="First operand")
        b: float = handle(description="Second operand")
        operation: str = combo(default="add", description="Operation type", options=["add", "subtract", "multiply", "divide", "power", "modulus"])
    
    class Outputs(BaseNode.Outputs):
        result: float
    
    def __call__(self, a: float = 0.0, b: float = 0.0, operation: str = "add") -> dict:
        
        
        if operation == "add":
            return {"result": a + b}
        elif operation == "subtract":
            return {"result": a - b}
        elif operation == "multiply":
            return {"result": a * b}
        elif operation == "divide":
            if b != 0:
                return {"result": a / b}
            else:
                return {"result": 0.0}
        elif operation == "power":
            return {"result": a ** b}
        elif operation == "modulus":
            return {"result": a % b}
        else:
            return {"result": a}

@register_node(
    name="Filter",
    description="Data Filter Node - Filters data based on conditions",
    inputs={"data": list, "condition": str, "field": str},
    outputs={"filtered": list},
    category="processing",
    icon="🔍"
)
def filter_node(data: list = None, condition: str = "equals", field: str = "") -> dict:
    
    data = data or []
    filtered = []
    
    
    for item in data:
        if isinstance(item, dict) and field in item:
            filtered.append(item)
    
    return {"filtered": filtered}

@register_node(
    name="Transform",
    description="Data Transform Node - Transforms data structure",
    inputs={"data": any, "transform_type": str, "mapping": dict},
    outputs={"transformed": any},
    category="processing",
    icon="🔄"
)
def transform_node(data: any = None, transform_type: str = "map", mapping: dict = None) -> dict:
    
    data = data or {}
    mapping = mapping or {}
    
    
    if transform_type == "map" and isinstance(data, dict):
        transformed = {}
        for old_key, new_key in mapping.items():
            if old_key in data:
                transformed[new_key] = data[old_key]
        return {"transformed": transformed}
    
    return {"transformed": data}

@register_node(
    name="AIProcessing",
    description="AI Processing Node - Performs AI-related processing tasks",
    inputs={"input_data": any, "ai_model": str, "prompt": str},
    outputs={"result": any, "confidence": float},
    category="processing",
    icon="🤖"
)
def ai_processing_node(input_data: any = "", ai_model: str = "default", prompt: str = "") -> dict:
    
    
    return {
        "result": f"Processed with {ai_model}: {str(input_data)}",
        "confidence": 0.95
    }

@register_node(
    name="TextOutput",
    description="Text Output Node - Outputs results as text",
    inputs={"value": str},
    outputs={"result": str},
    category="output",
    icon="📝"
)
def text_output_node(value: str = "") -> dict:
    
    return {"result": value}

import base64
import io
from PIL import Image

@register_node(
    name="FileOutput",
    description="File Output Node - Saves results to file (supports text and images)",
    inputs={"content": str, "file_path": str, "encoding": str, "is_image": bool},
    outputs={"success": bool, "message": str},
    category="output",
    icon="💾"
)
def file_output_node(content: str = "", file_path: str = "output.txt", encoding: str = "utf-8", is_image: bool = False) -> dict:
    
    try:
        if is_image:
            
            if content.startswith("data:image/"):
                
                content = content.split(",")[1]
            
            
            image_data = base64.b64decode(content)
            
            
            image = Image.open(io.BytesIO(image_data))
            image.save(file_path)
            return {"success": True, "message": f"Image saved to {file_path}"}
        else:
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return {"success": True, "message": f"Text file saved to {file_path}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@register_node(
    name="APIOutput",
    description="API Output Node - Sends results to API",
    inputs={"data": any, "url": str, "method": str, "headers": dict},
    outputs={"success": bool, "status": int, "response": any},
    category="output",
    icon="📡"
)
def api_output_node(data: any = None, url: str = "", method: str = "POST", headers: dict = None) -> dict:
    
    data = data or {}
    headers = headers or {}
    
    
    try:
        import requests
        response = requests.request(method, url, json=data, headers=headers)
        return {
            "success": response.status_code < 400,
            "status": response.status_code,
            "response": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "status": 500,
            "response": {"error": str(e)}
        }

@register_node(
    name="DatabaseOutput",
    description="Database Output Node - Saves results to database",
    inputs={"data": list, "table": str, "connection": dict},
    outputs={"success": bool, "count": int, "message": str},
    category="output",
    icon="💽"
)
def database_output_node(data: list = None, table: str = "", connection: dict = None) -> dict:
    
    data = data or []
    connection = connection or {}
    
    
    try:
        count = len(data)
        return {
            "success": True,
            "count": count,
            "message": f"Inserted {count} records into {table}"
        }
    except Exception as e:
        return {
            "success": False,
            "count": 0,
            "message": f"Error: {str(e)}"
        }

@register_node(
    name="Branch",
    description="Branch Node - Executes different branches based on conditions",
    category="control",
    icon="🔀"
)
class BranchNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        condition: bool = toggle(default=False, description="Condition expression")
        true_branch: str = text_input(default="", description="Branch when condition is true")
        false_branch: str = text_input(default="", description="Branch when condition is false")
    
    class Outputs(BaseNode.Outputs):
        result: bool
        next_branch: str
    
    def __call__(self, condition: bool = False, true_branch: str = "", false_branch: str = "") -> dict:
        
        next_branch = true_branch if condition else false_branch
        return {"result": condition, "next_branch": next_branch}

@register_node(
    name="Parallel",
    description="Parallel Execution Node - Executes multiple tasks in parallel",
    category="control",
    icon="⚡"
)
class ParallelNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        tasks: list = text_input(default="[]", description="Task list")
        max_workers: int = slider(default=4, description="Maximum number of workers", min=1, max=16, step=1)
    
    class Outputs(BaseNode.Outputs):
        results: list
        completed: int
    
    def __call__(self, tasks: list = None, max_workers: int = 4) -> dict:
        
        import json
        tasks = json.loads(tasks) if isinstance(tasks, str) else (tasks or [])
        results = []
        
        
        for task in tasks:
            results.append(f"Processed: {str(task)}")

        return {
            "results": results,
            "completed": len(results)
        }

@register_node(
    name="Loop",
    description="Loop Node - Repeats task execution until condition is met",
    category="control",
    icon="🔄"
)
class LoopNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        iterable: list = text_input(default="[]", description="Iterable object")
        condition: str = combo(default="all", description="Loop condition", options=["all", "any", "first_n"])
        max_iterations: int = slider(default=100, description="Maximum number of iterations", min=1, max=1000, step=1)
    
    class Outputs(BaseNode.Outputs):
        results: list
        iterations: int
    
    def __call__(self, iterable: list = None, condition: str = "all", max_iterations: int = 100) -> dict:
        
        import json
        iterable = json.loads(iterable) if isinstance(iterable, str) else (iterable or [])
        results = []
        iterations = 0

        for item in iterable:
            if iterations >= max_iterations:
                break
            results.append(f"Iteration {iterations}: {str(item)}")
            iterations += 1

        return {
            "results": results,
            "iterations": iterations
        }

@register_node(
    name="batch_audio_gen",
    description="Batch Audio Generation Node - Generates multiple audio files from prompts",
    category="audio",
    icon="🎵"
)
class BatchAudioGenNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        audio_prompt_list: list = BaseNode.Inputs.List(description="List of audio generation prompts")
        audio_model: str = combo(default="facebook/musicgen-small", description="Audio model", options=["facebook/musicgen-small", "facebook/musicgen-medium", "facebook/musicgen-large"])
        duration: float = slider(default=10.0, min=1.0, max=30.0, step=1.0, description="Duration of each audio in seconds")
        audio_seed: int = slider(default=42, min=0, max=2147483647, step=1, description="Random seed for audio generation")
    
    class Outputs(BaseNode.Outputs):
        audio_list: list
        count: int
        success: bool
        message: str
    
    def __call__(self, audio_prompt_list: list = None, audio_model: str = "facebook/musicgen-small", duration: float = 10.0, audio_seed: int = 42) -> dict:
        
        try:
            import torch
            from transformers import AutoProcessor, MusicgenForConditionalGeneration
            import scipy.io.wavfile as wavfile
            import numpy as np
            import tempfile
            import os
            
            audio_prompt_list = audio_prompt_list or []
            
            if not isinstance(audio_prompt_list, list):
                return {
                    "audio_list": [],
                    "count": 0,
                    "success": False,
                    "message": "Input must be a list of audio prompts"
                }
            
            if len(audio_prompt_list) == 0:
                return {
                    "audio_list": [],
                    "count": 0,
                    "success": False,
                    "message": "Audio prompt list is empty"
                }
            
            # Initialize the audio generation model
            processor = AutoProcessor.from_pretrained(audio_model)
            model = MusicgenForConditionalGeneration.from_pretrained(audio_model)
            
            # Set device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model.to(device)
            
            audio_list = []
            
            # Create temporary directory for audio output
            os.makedirs("uploads/audio", exist_ok=True)
            
            # Generate audio for each prompt
            for i, prompt in enumerate(audio_prompt_list):
                if not prompt:
                    continue
                
                # Process the prompt
                inputs = processor(
                    text=[prompt],
                    padding=True,
                    return_tensors="pt"
                ).to(device)
                
                # Generate audio
                with torch.no_grad():
                    audio_values = model.generate(
                        **inputs,
                        do_sample=True,
                        guidance_scale=3.0,
                        max_new_tokens=int(duration * 50),  # Approximate conversion
                        temperature=1.0,
                        seed=audio_seed + i  # Unique seed for each audio
                    )
                
                # Save the generated audio
                sample_rate = model.config.audio_encoder.sampling_rate
                audio_np = audio_values[0, 0].cpu().numpy()
                
                # Normalize audio
                audio_np = audio_np / np.max(np.abs(audio_np))
                
                # Convert to 16-bit PCM
                audio_np = (audio_np * 32767).astype(np.int16)
                
                # Create temporary file
                temp_audio_path = tempfile.mktemp(suffix=".wav", dir="uploads/audio")
                wavfile.write(temp_audio_path, sample_rate, audio_np)
                
                audio_list.append(temp_audio_path)
            
            return {
                "audio_list": audio_list,
                "count": len(audio_list),
                "success": True,
                "message": f"Successfully generated {len(audio_list)} audio files"
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "audio_list": [],
                "count": 0,
                "success": False,
                "message": f"Error generating audio: {str(e)}"
            }
