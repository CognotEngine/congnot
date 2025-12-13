from typing import Dict, Any, Optional
from PIL import Image
import io
import base64

from core.node_registry import register_node
from core.base_node import BaseNode, text_area, slider, text_input, handle
from core.model_cache_manager import model_cache_manager

SD_AVAILABLE = None
torch = None
StableDiffusionPipeline = None
StableDiffusionImg2ImgPipeline = None
StableDiffusion3Pipeline = None
StableDiffusion35Pipeline = None
StableDiffusionXLPipeline = None
StableCascadePipeline = None
FluxPipeline = None
DEVICE = None
text_to_image_pipeline = None
img_to_img_pipeline = None
sd3_pipeline = None
sd35_pipeline = None
sdxl_pipeline = None
stable_cascade_pipeline = None
flux_pipeline = None

def init_sd_dependencies():
    
    global SD_AVAILABLE, torch, StableDiffusionPipeline, StableDiffusionImg2ImgPipeline, StableDiffusion3Pipeline, StableDiffusion35Pipeline, StableDiffusionXLPipeline, StableCascadePipeline, FluxPipeline, DEVICE
    
    if SD_AVAILABLE is not None:
        return SD_AVAILABLE
    
    try:
        from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
        # 尝试导入SDXL相关的类
        try:
            from diffusers import StableDiffusionXLPipeline
        except ImportError:
            print("StableDiffusionXLPipeline not available")
        # 尝试导入SD3相关的类
        try:
            from diffusers import StableDiffusion3Pipeline
        except ImportError:
            print("StableDiffusion3Pipeline not available")
        # 尝试导入SD3.5相关的类
        try:
            from diffusers import StableDiffusion35Pipeline
        except ImportError:
            print("StableDiffusion35Pipeline not available")
        # 尝试导入Stable Cascade相关的类
        try:
            from diffusers import StableCascadePipeline
        except ImportError:
            print("StableCascadePipeline not available")
        # 尝试导入Flux相关的类
        try:
            from diffusers import FluxPipeline
        except ImportError:
            print("FluxPipeline not available")
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
            # 使用模型缓存管理器获取或加载模型
            model_key = "sd_v1-5_text2img"
            pipeline = model_cache_manager.get_model(model_key)
            
            if pipeline is None:
                # 模型不在缓存中，加载它
                pipeline = StableDiffusionPipeline.from_pretrained(
                    "runwayml/stable-diffusion-v1-5",
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
                )
                pipeline.to(DEVICE)
                
                if DEVICE == "cuda":
                    try:
                        pipeline.enable_xformers_memory_efficient_attention()
                    except ImportError:
                        print("xformers not available, using regular attention")
                
                # 将模型添加到缓存
                model_cache_manager.add_model(model_key, pipeline)
            
            
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
    name="stable_diffusion_xl_generate",
    description="Generate images using Stable Diffusion XL",
    category="ai",
    icon="🎨"
)
class StableDiffusionXLGenerateNode(BaseNode):
    
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
            default=1024,
            min=512,
            max=2048,
            step=64,
            description="Generated image height"
        )
        width: int = slider(
            default=1024,
            min=512,
            max=2048,
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
                 height: int = 1024,
                 width: int = 1024,
                 num_inference_steps: int = 50,
                 guidance_scale: float = 7.5,
                 seed: Optional[int] = None) -> dict:
        
        try:
            if not init_sd_dependencies():
                return {
                    "image": "",
                    "success": False,
                    "message": "Stable Diffusion dependencies not installed. Please install them using: pip install -r requirements.txt"
                }
            
            if StableDiffusionXLPipeline is None:
                return {
                    "image": "",
                    "success": False,
                    "message": "StableDiffusionXLPipeline not available. Please update diffusers library."
                }
            
            global sdxl_pipeline
            
            # 使用Stable Diffusion XL模型
            if sdxl_pipeline is None:
                sdxl_pipeline = StableDiffusionXLPipeline.from_pretrained(
                    "stabilityai/stable-diffusion-xl-base-1.0",
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
                )
                sdxl_pipeline.to(DEVICE)
                
                if DEVICE == "cuda":
                    try:
                        sdxl_pipeline.enable_xformers_memory_efficient_attention()
                    except ImportError:
                        print("xformers not available, using regular attention")
            
            generator = None
            if seed is not None:
                generator = torch.Generator(device=DEVICE).manual_seed(seed)
            
            image = sdxl_pipeline(
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
    name="stable_cascade_generate",
    description="Generate images using Stable Cascade",
    category="ai",
    icon="🎨"
)
class StableCascadeGenerateNode(BaseNode):
    
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
            default=1024,
            min=512,
            max=2048,
            step=64,
            description="Generated image height"
        )
        width: int = slider(
            default=1024,
            min=512,
            max=2048,
            step=64,
            description="Generated image width"
        )
        num_inference_steps: int = slider(
            default=30,
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
                 height: int = 1024,
                 width: int = 1024,
                 num_inference_steps: int = 30,
                 guidance_scale: float = 7.5,
                 seed: Optional[int] = None) -> dict:
        
        try:
            if not init_sd_dependencies():
                return {
                    "image": "",
                    "success": False,
                    "message": "Stable Diffusion dependencies not installed. Please install them using: pip install -r requirements.txt"
                }
            
            if StableCascadePipeline is None:
                return {
                    "image": "",
                    "success": False,
                    "message": "StableCascadePipeline not available. Please update diffusers library."
                }
            
            global stable_cascade_pipeline
            
            # 使用Stable Cascade模型
            if stable_cascade_pipeline is None:
                stable_cascade_pipeline = StableCascadePipeline.from_pretrained(
                    "stabilityai/stable-cascade-prior",
                    "stabilityai/stable-cascade",
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
                )
                stable_cascade_pipeline.to(DEVICE)
                
                if DEVICE == "cuda":
                    try:
                        stable_cascade_pipeline.enable_xformers_memory_efficient_attention()
                    except ImportError:
                        print("xformers not available, using regular attention")
            
            generator = None
            if seed is not None:
                generator = torch.Generator(device=DEVICE).manual_seed(seed)
            
            image = stable_cascade_pipeline(
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
    name="flux_generate",
    description="Generate images using Flux",
    category="ai",
    icon="🎨"
)
class FluxGenerateNode(BaseNode):
    
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
            default=1024,
            min=512,
            max=2048,
            step=64,
            description="Generated image height"
        )
        width: int = slider(
            default=1024,
            min=512,
            max=2048,
            step=64,
            description="Generated image width"
        )
        num_inference_steps: int = slider(
            default=4,
            min=1,
            max=20,
            step=1,
            description="Number of inference steps"
        )
        guidance_scale: float = slider(
            default=3.5,
            min=1.0,
            max=10.0,
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
                 height: int = 1024,
                 width: int = 1024,
                 num_inference_steps: int = 4,
                 guidance_scale: float = 3.5,
                 seed: Optional[int] = None) -> dict:
        
        try:
            if not init_sd_dependencies():
                return {
                    "image": "",
                    "success": False,
                    "message": "Stable Diffusion dependencies not installed. Please install them using: pip install -r requirements.txt"
                }
            
            if FluxPipeline is None:
                return {
                    "image": "",
                    "success": False,
                    "message": "FluxPipeline not available. Please update diffusers library."
                }
            
            global flux_pipeline
            
            # 使用Flux模型
            if flux_pipeline is None:
                flux_pipeline = FluxPipeline.from_pretrained(
                    "black-forest-labs/FLUX.1-dev",
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
                )
                flux_pipeline.to(DEVICE)
                
                if DEVICE == "cuda":
                    try:
                        flux_pipeline.enable_xformers_memory_efficient_attention()
                    except ImportError:
                        print("xformers not available, using regular attention")
            
            generator = None
            if seed is not None:
                generator = torch.Generator(device=DEVICE).manual_seed(seed)
            
            image = flux_pipeline(
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
    name="stable_diffusion_35_generate",
    description="Generate images using Stable Diffusion 3.5",
    category="ai",
    icon="🎨"
)
class StableDiffusion35GenerateNode(BaseNode):
    
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
            default=1024,
            min=256,
            max=2048,
            step=64,
            description="Generated image height"
        )
        width: int = slider(
            default=1024,
            min=256,
            max=2048,
            step=64,
            description="Generated image width"
        )
        num_inference_steps: int = slider(
            default=28,
            min=10,
            max=100,
            step=1,
            description="Number of inference steps"
        )
        guidance_scale: float = slider(
            default=7.0,
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
                 height: int = 1024,
                 width: int = 1024,
                 num_inference_steps: int = 28,
                 guidance_scale: float = 7.0,
                 seed: Optional[int] = None) -> dict:
        
        try:
            if not init_sd_dependencies():
                return {
                    "image": "",
                    "success": False,
                    "message": "Stable Diffusion dependencies not installed. Please install them using: pip install -r requirements.txt"
                }
            
            if StableDiffusion35Pipeline is None:
                return {
                    "image": "",
                    "success": False,
                    "message": "StableDiffusion35Pipeline not available. Please update diffusers library."
                }
            
            global sd35_pipeline
            
            # 使用Stable Diffusion 3.5模型
            if sd35_pipeline is None:
                sd35_pipeline = StableDiffusion35Pipeline.from_pretrained(
                    "stabilityai/stable-diffusion-3.5-large",
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
                )
                sd35_pipeline.to(DEVICE)
                
                if DEVICE == "cuda":
                    try:
                        sd35_pipeline.enable_xformers_memory_efficient_attention()
                    except ImportError:
                        print("xformers not available, using regular attention")
            
            generator = None
            if seed is not None:
                generator = torch.Generator(device=DEVICE).manual_seed(seed)
            
            image = sd35_pipeline(
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
    name="stable_diffusion_3_generate",
    description="Generate images using Stable Diffusion 3 Medium",
    category="ai",
    icon="🎨"
)
class StableDiffusion3GenerateNode(BaseNode):
    
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
            default=1024,
            min=256,
            max=2048,
            step=64,
            description="Generated image height"
        )
        width: int = slider(
            default=1024,
            min=256,
            max=2048,
            step=64,
            description="Generated image width"
        )
        num_inference_steps: int = slider(
            default=28,
            min=10,
            max=100,
            step=1,
            description="Number of inference steps"
        )
        guidance_scale: float = slider(
            default=7.0,
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
                 height: int = 1024,
                 width: int = 1024,
                 num_inference_steps: int = 28,
                 guidance_scale: float = 7.0,
                 seed: Optional[int] = None) -> dict:
        
        try:
            if not init_sd_dependencies():
                return {
                    "image": "",
                    "success": False,
                    "message": "Stable Diffusion dependencies not installed. Please install them using: pip install -r requirements.txt"
                }
            
            if StableDiffusion3Pipeline is None:
                return {
                    "image": "",
                    "success": False,
                    "message": "StableDiffusion3Pipeline not available. Please update diffusers library."
                }
            
            global sd3_pipeline
            
            # 使用提供的Stable Diffusion 3 Medium模型地址
            if sd3_pipeline is None:
                sd3_pipeline = StableDiffusion3Pipeline.from_pretrained(
                    "stabilityai/stable-diffusion-3-medium",
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
                )
                sd3_pipeline.to(DEVICE)
                
                if DEVICE == "cuda":
                    try:
                        sd3_pipeline.enable_xformers_memory_efficient_attention()
                    except ImportError:
                        print("xformers not available, using regular attention")
            
            generator = None
            if seed is not None:
                generator = torch.Generator(device=DEVICE).manual_seed(seed)
            
            image = sd3_pipeline(
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
            # 检查输入图像
            if not init_image:
                return {
                    "image": "",
                    "success": False,
                    "message": "Initial image is required for image-to-image generation"
                }
            
            # 处理输入图像
            if init_image.startswith("data:image/"):
                init_image = init_image.split(",")[1]
            
            init_image_data = base64.b64decode(init_image)
            init_image_pil = Image.open(io.BytesIO(init_image_data)).convert("RGB")
            
            # 使用模型缓存管理器获取或加载模型
            model_key = "sd_v1-5_img2img"
            pipeline = model_cache_manager.get_model(model_key)
            
            if pipeline is None:
                # 模型不在缓存中，加载它
                pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
                    "runwayml/stable-diffusion-v1-5",
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
                )
                pipeline.to(DEVICE)
                
                if DEVICE == "cuda":
                    try:
                        pipeline.enable_xformers_memory_efficient_attention()
                    except ImportError:
                        print("xformers not available, using regular attention")
                
                # 将模型添加到缓存
                model_cache_manager.add_model(model_key, pipeline)
            
            
            generator = None
            if seed is not None:
                generator = torch.Generator(device=DEVICE).manual_seed(seed)
            
            
            image = pipeline(
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
