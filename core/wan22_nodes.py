from typing import Dict, Any, Optional
from PIL import Image
import io
import base64
import os
import tempfile
import cv2
import numpy as np

from core.node_registry import register_node
from core.base_node import BaseNode, text_area, slider, text_input, handle

WAN22_AVAILABLE = None
torch = None
WanVideoPipeline = None
DEVICE = None
text_to_video_pipeline = None
img_to_video_pipeline = None


def init_wan22_dependencies():
    """Initialize WAN2.2 dependencies"""
    global WAN22_AVAILABLE, torch, WanVideoPipeline, DEVICE

    if WAN22_AVAILABLE is not None:
        return WAN22_AVAILABLE

    try:
        from diffusers import WanVideoPipeline
        import torch

        DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"WAN2.2 using device: {DEVICE}")

        WAN22_AVAILABLE = True
        return True
    except ImportError as e:
        print(f"WAN2.2 dependencies not installed: {e}")
        WAN22_AVAILABLE = False
        return False


@register_node(
    name="wan22_text_to_video",
    description="Generate videos using WAN2.2 text-to-video model",
    category="ai",
    icon="🎥"
)
class Wan22TextToVideoNode(BaseNode):

    class Inputs(BaseNode.Inputs):
        prompt: str = text_area(
            default="一只猫对着镜头笑",
            description="Prompt for video generation"
        )
        negative_prompt: str = text_area(
            default="ugly, deformed, blurry, low quality, watermark",
            description="Content not desired in the video"
        )
        height: int = slider(
            default=480,
            min=256,
            max=1080,
            step=64,
            description="Generated video height"
        )
        width: int = slider(
            default=720,
            min=256,
            max=1920,
            step=64,
            description="Generated video width"
        )
        num_frames: int = slider(
            default=60,
            min=16,
            max=120,
            step=8,
            description="Number of frames in the video (24fps = 2.5s for 60 frames)"
        )
        guidance_scale: float = slider(
            default=9.0,
            min=1.0,
            max=20.0,
            step=0.5,
            description="Guidance scale"
        )
        num_inference_steps: int = slider(
            default=50,
            min=10,
            max=100,
            step=5,
            description="Number of inference steps"
        )
        seed: str = text_input(
            default=None,
            description="Random seed (optional)"
        )

    class Outputs(BaseNode.Outputs):
        video_path: str
        success: bool
        message: str

    def __call__(self, prompt: str = "一只猫对着镜头笑",
                 negative_prompt: str = "ugly, deformed, blurry, low quality, watermark",
                 height: int = 480,
                 width: int = 720,
                 num_frames: int = 60,
                 guidance_scale: float = 9.0,
                 num_inference_steps: int = 50,
                 seed: Optional[int] = None) -> dict:

        if not init_wan22_dependencies():
            return {
                "video_path": "",
                "success": False,
                "message": "WAN2.2 dependencies not installed. Please install them using: pip install -r requirements.txt"
            }

        try:
            global text_to_video_pipeline

            # Initialize pipeline if not already done
            if text_to_video_pipeline is None:
                print("Loading WAN2.2 text-to-video pipeline...")
                text_to_video_pipeline = WanVideoPipeline.from_pretrained(
                    "Wan-Video/Wan2.2-T2V",
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
                    variant="fp16" if DEVICE == "cuda" else ""
                )
                text_to_video_pipeline.to(DEVICE)

                # Enable memory efficient attention if available
                if DEVICE == "cuda":
                    try:
                        text_to_video_pipeline.enable_xformers_memory_efficient_attention()
                        print("Enabled xformers memory efficient attention")
                    except ImportError:
                        print("xformers not available, using regular attention")

            # Set seed if provided
            generator = None
            if seed is not None:
                generator = torch.Generator(device=DEVICE).manual_seed(seed)

            # Generate video frames
            print(f"Generating video with prompt: '{prompt}'")
            video_frames = text_to_video_pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                height=height,
                width=width,
                num_frames=num_frames,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                generator=generator
            ).frames[0]

            # Create temporary directory for video output
            os.makedirs("uploads/video", exist_ok=True)
            temp_video_path = tempfile.mktemp(suffix=".mp4", dir="uploads/video")

            # Save frames to video using OpenCV
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = 24.0
            video_writer = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))

            for frame in video_frames:
                # Convert PIL frame to numpy array
                frame_np = np.array(frame)
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
                video_writer.write(frame_bgr)

            video_writer.release()

            return {
                "video_path": temp_video_path,
                "success": True,
                "message": "Video generated successfully"
            }

        except Exception as e:
            print(f"Error generating video: {str(e)}")
            return {
                "video_path": "",
                "success": False,
                "message": f"Error generating video: {str(e)}"
            }


@register_node(
    name="wan22_image_to_video",
    description="Generate videos using WAN2.2 image-to-video model",
    category="ai",
    icon="🖼️🎥"
)
class Wan22ImageToVideoNode(BaseNode):

    class Inputs(BaseNode.Inputs):
        image: str = handle(
            description="Initial image for video generation"
        )
        prompt: str = text_area(
            default="一只猫对着镜头笑",
            description="Prompt for video generation"
        )
        negative_prompt: str = text_area(
            default="ugly, deformed, blurry, low quality, watermark",
            description="Content not desired in the video"
        )
        num_frames: int = slider(
            default=60,
            min=16,
            max=120,
            step=8,
            description="Number of frames in the video (24fps = 2.5s for 60 frames)"
        )
        guidance_scale: float = slider(
            default=9.0,
            min=1.0,
            max=20.0,
            step=0.5,
            description="Guidance scale"
        )
        num_inference_steps: int = slider(
            default=50,
            min=10,
            max=100,
            step=5,
            description="Number of inference steps"
        )
        seed: str = text_input(
            default=None,
            description="Random seed (optional)"
        )

    class Outputs(BaseNode.Outputs):
        video_path: str
        success: bool
        message: str

    def __call__(self, image: str = "",
                 prompt: str = "一只猫对着镜头笑",
                 negative_prompt: str = "ugly, deformed, blurry, low quality, watermark",
                 num_frames: int = 60,
                 guidance_scale: float = 9.0,
                 num_inference_steps: int = 50,
                 seed: Optional[int] = None) -> dict:

        if not init_wan22_dependencies():
            return {
                "video_path": "",
                "success": False,
                "message": "WAN2.2 dependencies not installed. Please install them using: pip install -r requirements.txt"
            }

        try:
            global img_to_video_pipeline

            # Check if image is provided
            if not image:
                return {
                    "video_path": "",
                    "success": False,
                    "message": "Initial image is required for image-to-video generation"
                }

            # Process input image
            if image.startswith("data:image/"):
                # Remove data URI prefix
                image = image.split(",")[1]

            image_data = base64.b64decode(image)
            init_image = Image.open(io.BytesIO(image_data)).convert("RGB")
            width, height = init_image.size

            # Initialize pipeline if not already done
            if img_to_video_pipeline is None:
                print("Loading WAN2.2 image-to-video pipeline...")
                img_to_video_pipeline = WanVideoPipeline.from_pretrained(
                    "Wan-Video/Wan2.2-I2V",
                    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
                    variant="fp16" if DEVICE == "cuda" else ""
                )
                img_to_video_pipeline.to(DEVICE)

                # Enable memory efficient attention if available
                if DEVICE == "cuda":
                    try:
                        img_to_video_pipeline.enable_xformers_memory_efficient_attention()
                        print("Enabled xformers memory efficient attention")
                    except ImportError:
                        print("xformers not available, using regular attention")

            # Set seed if provided
            generator = None
            if seed is not None:
                generator = torch.Generator(device=DEVICE).manual_seed(seed)

            # Generate video frames
            print(f"Generating video from image with prompt: '{prompt}'")
            video_frames = img_to_video_pipeline(
                prompt=prompt,
                image=init_image,
                negative_prompt=negative_prompt,
                num_frames=num_frames,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                generator=generator
            ).frames[0]

            # Create temporary directory for video output
            os.makedirs("uploads/video", exist_ok=True)
            temp_video_path = tempfile.mktemp(suffix=".mp4", dir="uploads/video")

            # Save frames to video using OpenCV
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = 24.0
            video_writer = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))

            for frame in video_frames:
                # Convert PIL frame to numpy array
                frame_np = np.array(frame)
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
                video_writer.write(frame_bgr)

            video_writer.release()

            return {
                "video_path": temp_video_path,
                "success": True,
                "message": "Video generated successfully from image"
            }

        except Exception as e:
            print(f"Error generating video from image: {str(e)}")
            return {
                "video_path": "",
                "success": False,
                "message": f"Error generating video from image: {str(e)}"
            }
