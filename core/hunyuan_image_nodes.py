from typing import Dict, Any, Optional
from PIL import Image
import io
import base64

from core.node_registry import register_node
from core.base_node import BaseNode, text_area, slider, text_input, handle
import core.model_cache_manager as model_cache_manager

HUNYUAN_IMAGE_AVAILABLE = None
torch = None
HunyuanDiTPipeline = None
DEVICE = None
hunyuan_dit_pipeline = None


def init_hunyuan_image_dependencies():
    """Initialize Hunyuan DiT dependencies"""
    global HUNYUAN_IMAGE_AVAILABLE, torch, HunyuanDiTPipeline, DEVICE

    if HUNYUAN_IMAGE_AVAILABLE is not None:
        return HUNYUAN_IMAGE_AVAILABLE

    try:
        from diffusers import HunyuanDiTPipeline
        import torch

        DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"HunyuanDiT using device: {DEVICE}")

        HUNYUAN_IMAGE_AVAILABLE = True
        return True
    except ImportError as e:
        print(f"HunyuanDiT dependencies not installed: {e}")
        HUNYUAN_IMAGE_AVAILABLE = False
        return False


@register_node(
    name="hunyuan_dit_generate",
    description="Generate images using HunyuanDiT text-to-image model",
    category="ai",
    icon="🎨"
)
class HunyuanDiTGenerateNode(BaseNode):

    class Inputs(BaseNode.Inputs):
        prompt: str = text_area(
            default="一只猫对着镜头笑",
            description="Prompt for image generation"
        )
        negative_prompt: str = text_area(
            default="ugly, deformed, blurry, low quality, watermark",
            description="Content not desired in the image"
        )
        height: int = slider(
            default=1024,
            min=512,
            max=1536,
            step=64,
            description="Generated image height"
        )
        width: int = slider(
            default=1024,
            min=512,
            max=1536,
            step=64,
            description="Generated image width"
        )
        num_inference_steps: int = slider(
            default=20,
            min=5,
            max=50,
            step=1,
            description="Number of inference steps"
        )
        guidance_scale: float = slider(
            default=7.5,
            min=1.0,
            max=20.0,
            step=0.5,
            description="Guidance scale"
        )
        seed: str = text_input(
            default=None,
            description="Random seed (optional)"
        )

    class Outputs(BaseNode.Outputs):
        image: str
        success: bool
        message: str

    def __call__(self, prompt: str = "一只猫对着镜头笑",
                 negative_prompt: str = "ugly, deformed, blurry, low quality, watermark",
                 height: int = 1024,
                 width: int = 1024,
                 num_inference_steps: int = 20,
                 guidance_scale: float = 7.5,
                 seed: Optional[int] = None) -> dict:

        if not init_hunyuan_image_dependencies():
            return {
                "image": "",
                "success": False,
                "message": "HunyuanDiT dependencies not installed. Please install them using: pip install -r requirements.txt"
            }

        try:
            # 使用模型缓存管理器获取或加载模型
            model_key = "hunyuan_dit_text2img"
            pipeline = model_cache_manager.get_model(model_key)
            
            if pipeline is None:
                # 模型不在缓存中，加载它
                pipeline = HunyuanDiTPipeline.from_pretrained(
                    "Tencent-Hunyuan/HunyuanDiT-v1.2",
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
                    variant="fp16" if DEVICE == "cuda" else ""
                )
                pipeline.to(DEVICE)
                
                if DEVICE == "cuda":
                    try:
                        pipeline.enable_xformers_memory_efficient_attention()
                        print("Enabled xformers memory efficient attention")
                    except ImportError:
                        print("xformers not available, using regular attention")
                
                # 将模型添加到缓存
                model_cache_manager.add_model(model_key, pipeline)

            # Set seed if provided
            generator = None
            if seed is not None:
                generator = torch.Generator(device=DEVICE).manual_seed(seed)

            # Generate image
            print(f"Generating image with prompt: '{prompt}'")
            image = pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            ).images[0]

            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            img_data = f"data:image/png;base64,{img_str}"

            return {
                "image": img_data,
                "success": True,
                "message": "Image generated successfully"
            }

        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return {
                "image": "",
                "success": False,
                "message": f"Error generating image: {str(e)}"
            }
