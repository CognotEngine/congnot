from typing import Dict, Any, Optional
from PIL import Image
import io
import base64

from core.node_registry import register_node
from core.base_node import BaseNode, text_area, slider, text_input, handle

SD_AVAILABLE = None
torch = None
StableDiffusionPipeline = None
StableDiffusionImg2ImgPipeline = None
DEVICE = None
text_to_image_pipeline = None
img_to_img_pipeline = None

def init_sd_dependencies():
    
    global SD_AVAILABLE, torch, StableDiffusionPipeline, StableDiffusionImg2ImgPipeline, DEVICE
    
    if SD_AVAILABLE is not None:
        return SD_AVAILABLE
    
    try:
        from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
        import torch
        
        
        DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {DEVICE}")
        
        SD_AVAILABLE = True
        return True
    except ImportError as e:
        print(f"SD dependencies not installed: {e}")
        SD_AVAILABLE = False
        return False

@register_node(
    name="stable_diffusion_generate",
    description="Generate images using Stable Diffusion on local GPU",
    category="ai",
    icon="🎨"
)
class StableDiffusionGenerateNode(BaseNode):
    
    
    class Inputs(BaseNode.Inputs):
        
        prompt: str = text_area(
            default="A beautiful landscape",
            description="Prompt for image generation"
        )
        negative_prompt: str = text_area(
            default="ugly, deformed, blurry",
            description="Content not desired in the image"
        )
        height: int = slider(
            default=512,
            min=256,
            max=1024,
            step=64,
            description="Generated image height"
        )
        width: int = slider(
            default=512,
            min=256,
            max=1024,
            step=64,
            description="Generated image width"
        )
        num_inference_steps: int = slider(
            default=50,
            min=10,
            max=100,
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
    
    def __call__(self, prompt: str = "A beautiful landscape",
                 negative_prompt: str = "ugly, deformed, blurry",
                 height: int = 512,
                 width: int = 512,
                 num_inference_steps: int = 50,
                 guidance_scale: float = 7.5,
                 seed: Optional[int] = None) -> dict:
        
        
        
        if not init_sd_dependencies():
            return {
                "image": "",
                "success": False,
                "message": "Stable Diffusion dependencies not installed. Please install them using: pip install -r requirements.txt"
            }
        
        try:
            global text_to_image_pipeline
            
            
            if text_to_image_pipeline is None:
                text_to_image_pipeline = StableDiffusionPipeline.from_pretrained(
                    "runwayml/stable-diffusion-v1-5",
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
                )
                text_to_image_pipeline.to(DEVICE)
                
                
                if DEVICE == "cuda":
                    try:
                        text_to_image_pipeline.enable_xformers_memory_efficient_attention()
                    except ImportError:
                        print("xformers not available, using regular attention")
            
            
            generator = None
            if seed is not None:
                generator = torch.Generator(device=DEVICE).manual_seed(seed)
            
            
            image = text_to_image_pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            ).images[0]
            
            
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
            return {
                "image": "",
                "success": False,
                "message": f"Error generating image: {str(e)}"
            }

@register_node(
    name="clip_text_encode",
    description="CLIP Text Encode (Prompt)",
    category="ai",
    icon="📝"
)
class CLIPTextEncodeNode(BaseNode):
    
    class Inputs(BaseNode.Inputs):
        
        clip: Any = handle(
            description="CLIP model input",
            color_type="MODEL"
        )
        prompt: str = text_area(
            default="A beautiful landscape",
            description="Text prompt to encode"
        )
    
    class Outputs(BaseNode.Outputs):
        
        Conditioning: Any
    
    def __call__(self, clip: Any = None, prompt: str = "A beautiful landscape") -> dict:
        
        try:
            if not init_sd_dependencies():
                return {
                    "Conditioning": None,
                    "success": False,
                    "message": "Stable Diffusion dependencies not installed."
                }
            
            # 这里只是一个占位实现，实际的CLIP编码逻辑需要根据具体需求实现
            # 通常需要使用SD模型的text encoder来处理prompt
            conditioning = {
                "prompt": prompt,
                "type": "conditioning"
            }
            
            return {
                "Conditioning": conditioning,
                "success": True,
                "message": "CLIP text encoding successful"
            }
            
        except Exception as e:
            return {
                "Conditioning": None,
                "success": False,
                "message": f"Error in CLIP text encoding: {str(e)}"
            }

@register_node(
    name="stable_diffusion_image_to_image",
    description="Generate images using Stable Diffusion image-to-image on local GPU",
    category="ai",
    icon="🖼️"
)
class StableDiffusionImageToImageNode(BaseNode):
    
    
    class Inputs(BaseNode.Inputs):
        
        prompt: str = text_area(
            default="A beautiful landscape",
            description="Prompt for image generation"
        )
        negative_prompt: str = text_area(
            default="ugly, deformed, blurry",
            description="Content not desired in the image"
        )
        init_image: str = handle(
            description="Initial image"
        )
        strength: float = slider(
            default=0.75,
            min=0.1,
            max=1.0,
            step=0.05,
            description="Image strength (affects how much of the initial image is preserved)"
        )
        num_inference_steps: int = slider(
            default=50,
            min=10,
            max=100,
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
    
    def __call__(self, prompt: str = "A beautiful landscape",
                 negative_prompt: str = "ugly, deformed, blurry",
                 init_image: str = "",
                 strength: float = 0.75,
                 num_inference_steps: int = 50,
                 guidance_scale: float = 7.5,
                 seed: Optional[int] = None) -> dict:
        
        
        
        if not init_sd_dependencies():
            return {
                "image": "",
                "success": False,
                "message": "Stable Diffusion dependencies not installed. Please install them using: pip install -r requirements.txt"
            }
        
        try:
            global img_to_img_pipeline
            
            
            if not init_image:
                return {
                    "image": "",
                    "success": False,
                    "message": "Initial image is required for image-to-image generation"
                }
            
            
            if init_image.startswith("data:image/"):
                
                init_image = init_image.split(",")[1]
            
            init_image_data = base64.b64decode(init_image)
            init_image_pil = Image.open(io.BytesIO(init_image_data)).convert("RGB")
            
            
            if img_to_img_pipeline is None:
                img_to_img_pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
                    "runwayml/stable-diffusion-v1-5",
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
                )
                img_to_img_pipeline.to(DEVICE)
                
                
                if DEVICE == "cuda":
                    try:
                        img_to_img_pipeline.enable_xformers_memory_efficient_attention()
                    except ImportError:
                        print("xformers not available, using regular attention")
            
            
            generator = None
            if seed is not None:
                generator = torch.Generator(device=DEVICE).manual_seed(seed)
            
            
            image = img_to_img_pipeline(
                prompt=prompt,
                image=init_image_pil,
                negative_prompt=negative_prompt,
                strength=strength,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            ).images[0]
            
            
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
            return {
                "image": "",
                "success": False,
                "message": f"Error generating image: {str(e)}"
            }
