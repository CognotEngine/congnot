from typing import Dict, Any, Optional
from PIL import Image
import io
import base64

from core.node_registry import register_node
from core.base_node import BaseNode, text_area, slider, text_input, handle
import core.model_cache_manager as model_cache_manager

QWEN_AVAILABLE = None
torch = None
AutoTokenizer = None
AutoModelForCausalLM = None
DEVICE = None
qwen_vl_model = None
qwen_vl_tokenizer = None
qwen_text_model = None
qwen_text_tokenizer = None


def init_qwen_dependencies():
    """Initialize Qwen dependencies"""
    global QWEN_AVAILABLE, torch, AutoTokenizer, AutoModelForCausalLM, Qwen2VLForConditionalGeneration, Qwen2TokenizerFast, DEVICE

    if QWEN_AVAILABLE is not None:
        return QWEN_AVAILABLE

    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM, Qwen2VLForConditionalGeneration, Qwen2TokenizerFast
        import torch

        DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Qwen using device: {DEVICE}")

        QWEN_AVAILABLE = True
        return True
    except ImportError as e:
        print(f"Qwen dependencies not installed: {e}")
        QWEN_AVAILABLE = False
        return False


@register_node(
    name="qwen_vl_chat",
    description="Chat with Qwen-VL (Vision-Language) model",
    category="ai",
    icon="💬"
)
class QwenVLChatNode(BaseNode):

    class Inputs(BaseNode.Inputs):
        prompt: str = text_area(
            default="Describe this image",
            description="Text prompt for the model"
        )
        image_data: str = text_input(
            default="",
            description="Base64 encoded image data (optional)"
        )
        max_new_tokens: int = slider(
            default=1024,
            min=128,
            max=4096,
            step=64,
            description="Maximum number of new tokens to generate"
        )
        temperature: float = slider(
            default=0.7,
            min=0.1,
            max=2.0,
            step=0.1,
            description="Generation temperature"
        )
        seed: str = text_input(
            default=None,
            description="Random seed (optional)"
        )

    class Outputs(BaseNode.Outputs):
        response: str
        success: bool
        message: str

    def __call__(self, prompt: str = "Describe this image",
                 image_data: str = "",
                 max_new_tokens: int = 1024,
                 temperature: float = 0.7,
                 seed: Optional[int] = None) -> dict:

        if not init_qwen_dependencies():
            return {
                "response": "",
                "success": False,
                "message": "Qwen dependencies not installed. Please install them using: pip install -r requirements.txt"
            }

        try:
            global qwen_vl_model, qwen_vl_tokenizer

            # Initialize model and tokenizer if not already done
            # 使用模型缓存管理器获取或加载模型和分词器
            vl_model_key = "qwen_vl_model"
            vl_tokenizer_key = "qwen_vl_tokenizer"
            
            qwen_vl_model = model_cache_manager.get_model(vl_model_key)
            qwen_vl_tokenizer = model_cache_manager.get_model(vl_tokenizer_key)
            
            if qwen_vl_model is None or qwen_vl_tokenizer is None:
                print("Loading Qwen-VL-Chat model and tokenizer...")
                qwen_vl_model = Qwen2VLForConditionalGeneration.from_pretrained(
                    "Qwen/Qwen-VL-Chat",
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
                    device_map="auto",
                    trust_remote_code=True
                )
                qwen_vl_tokenizer = Qwen2TokenizerFast.from_pretrained(
                    "Qwen/Qwen-VL-Chat",
                    trust_remote_code=True
                )
                
                # 将模型和分词器添加到缓存
                model_cache_manager.add_model(vl_model_key, qwen_vl_model)
                model_cache_manager.add_model(vl_tokenizer_key, qwen_vl_tokenizer)

            # Set seed if provided
            if seed is not None:
                torch.manual_seed(seed)
                if DEVICE == "cuda":
                    torch.cuda.manual_seed_all(seed)

            # Prepare inputs
            if image_data:
                # Remove data URL prefix if present
                if image_data.startswith("data:image/"):
                    image_data = image_data.split(",")[1]
                
                # Convert base64 to PIL image
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Format inputs for Qwen-VL
                inputs = qwen_vl_tokenizer.from_list_format([
                    {"image": image},
                    {"text": prompt},
                ])
            else:
                # Text only input
                inputs = qwen_vl_tokenizer.from_list_format([
                    {"text": prompt},
                ])

            # Generate response
            print(f"Generating response with Qwen-VL...")
            inputs = qwen_vl_tokenizer(
                inputs, 
                return_tensors="pt", 
                padding=True
            ).to(DEVICE)
            
            generated_ids = qwen_vl_model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True
            )
            
            response = qwen_vl_tokenizer.batch_decode(
                generated_ids, 
                skip_special_tokens=True
            )[0]

            return {
                "response": response,
                "success": True,
                "message": "Response generated successfully"
            }

        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {
                "response": "",
                "success": False,
                "message": f"Error generating response: {str(e)}"
            }


@register_node(
    name="qwen_text_chat",
    description="Chat with Qwen text model",
    category="ai",
    icon="💬"
)
class QwenTextChatNode(BaseNode):

    class Inputs(BaseNode.Inputs):
        prompt: str = text_area(
            default="Explain quantum computing in simple terms",
            description="Text prompt for the model"
        )
        max_new_tokens: int = slider(
            default=1024,
            min=128,
            max=4096,
            step=64,
            description="Maximum number of new tokens to generate"
        )
        temperature: float = slider(
            default=0.7,
            min=0.1,
            max=2.0,
            step=0.1,
            description="Generation temperature"
        )
        seed: str = text_input(
            default=None,
            description="Random seed (optional)"
        )

    class Outputs(BaseNode.Outputs):
        response: str
        success: bool
        message: str

    def __call__(self, prompt: str = "Explain quantum computing in simple terms",
                 max_new_tokens: int = 1024,
                 temperature: float = 0.7,
                 seed: Optional[int] = None) -> dict:

        if not init_qwen_dependencies():
            return {
                "response": "",
                "success": False,
                "message": "Qwen dependencies not installed. Please install them using: pip install -r requirements.txt"
            }

        try:
            global qwen_text_model, qwen_text_tokenizer

            # Initialize model and tokenizer if not already done
            # 使用模型缓存管理器获取或加载模型和分词器
            text_model_key = "qwen_text_model"
            text_tokenizer_key = "qwen_text_tokenizer"
            
            qwen_text_model = model_cache_manager.get_model(text_model_key)
            qwen_text_tokenizer = model_cache_manager.get_model(text_tokenizer_key)
            
            if qwen_text_model is None or qwen_text_tokenizer is None:
                print("Loading Qwen-7B-Chat model and tokenizer...")
                from transformers import AutoTokenizer, AutoModelForCausalLM
                
                qwen_text_model = AutoModelForCausalLM.from_pretrained(
                    "Qwen/Qwen-7B-Chat",
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
                    device_map="auto",
                    trust_remote_code=True
                )
                qwen_text_tokenizer = AutoTokenizer.from_pretrained(
                    "Qwen/Qwen-7B-Chat",
                    trust_remote_code=True
                )
                
                # 将模型和分词器添加到缓存
                model_cache_manager.add_model(text_model_key, qwen_text_model)
                model_cache_manager.add_model(text_tokenizer_key, qwen_text_tokenizer)

            # Set seed if provided
            if seed is not None:
                torch.manual_seed(seed)
                if DEVICE == "cuda":
                    torch.cuda.manual_seed_all(seed)

            # Generate response
            print(f"Generating text response with Qwen...")
            inputs = qwen_text_tokenizer(
                prompt, 
                return_tensors="pt", 
                padding=True
            ).to(DEVICE)
            
            generated_ids = qwen_text_model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True
            )
            
            response = qwen_text_tokenizer.batch_decode(
                generated_ids, 
                skip_special_tokens=True
            )[0]

            return {
                "response": response,
                "success": True,
                "message": "Response generated successfully"
            }

        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {
                "response": "",
                "success": False,
                "message": f"Error generating response: {str(e)}"
            }
