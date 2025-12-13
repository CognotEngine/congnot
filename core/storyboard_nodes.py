from typing import Dict, Any, Optional, List
import json

from core.node_registry import register_node
from core.base_node import BaseNode, text_area, text_input, slider
import core.model_cache_manager as model_cache_manager

STORYBOARD_AVAILABLE = None
qwen_model = None
qwen_tokenizer = None


def init_storyboard_dependencies():
    """Initialize storyboard generation dependencies"""
    global STORYBOARD_AVAILABLE, qwen_model, qwen_tokenizer

    if STORYBOARD_AVAILABLE is not None:
        return STORYBOARD_AVAILABLE

    try:
        # 使用现有的Qwen依赖
        from core.qwen_nodes import init_qwen_dependencies, QWEN_AVAILABLE, qwen_text_model, qwen_text_tokenizer
        
        if not init_qwen_dependencies():
            STORYBOARD_AVAILABLE = False
            return False
            
        qwen_model = qwen_text_model
        qwen_tokenizer = qwen_text_tokenizer
        STORYBOARD_AVAILABLE = True
        return True
    except ImportError as e:
        print(f"Storyboard dependencies not installed: {e}")
        STORYBOARD_AVAILABLE = False
        return False


@register_node(
    name="storyboard_generator",
    description="Generate storyboard prompts using Qwen LLM",
    category="video",
    icon="📖"
)
class StoryboardGeneratorNode(BaseNode):

    class Inputs(BaseNode.Inputs):
        script_text: str = text_area(
            default="这是一个关于人工智能的故事，描述了一个机器人帮助人类的场景。",
            description="Script text for storyboard generation"
        )
        style_guide: str = text_area(
            default="现代科技风格，明亮的色彩，高对比度，细节丰富",
            description="Style guide for the generated images"
        )
        scene_count: int = slider(
            default=6,
            min=1,
            max=12,
            step=1,
            description="Number of scenes to generate"
        )
        max_prompt_length: int = slider(
            default=100,
            min=50,
            max=200,
            step=10,
            description="Maximum length of each prompt"
        )
        qwen_seed: str = text_input(
            default=None,
            description="Random seed for Qwen generation"
        )

    class Outputs(BaseNode.Outputs):
        image_prompts: List[str]
        audio_prompts: List[str]
        storyboard_json: str
        success: bool
        message: str

    def __call__(self, script_text: str = "这是一个关于人工智能的故事",
                 style_guide: str = "现代科技风格",
                 scene_count: int = 6,
                 max_prompt_length: int = 100,
                 qwen_seed: Optional[int] = None) -> dict:

        if not init_storyboard_dependencies():
            return {
                "image_prompts": [],
                "audio_prompts": [],
                "storyboard_json": "",
                "success": False,
                "message": "Storyboard dependencies not installed"
            }

        try:
            # 构建提示词模板
            prompt_template = f"""
            你是一位专业的视频导演和编剧，请根据以下剧本和风格指南，为{scene_count}个连续的分镜生成详细的图像提示词和音频提示词。
            
            剧本内容：
            {script_text}
            
            风格指南：
            {style_guide}
            
            要求：
            1. 生成{scene_count}个分镜，每个分镜包含图像提示词和音频提示词
            2. 图像提示词要详细描述场景、角色、动作、构图、光线等视觉元素，长度不超过{max_prompt_length}个字符
            3. 音频提示词要描述适合该场景的背景音乐、音效等，长度不超过50个字符
            4. 所有分镜要连贯，形成完整的故事流程
            5. 输出格式必须是JSON，包含两个数组：image_prompts和audio_prompts
            6. 确保JSON格式正确，不要包含其他解释性文字
            
            输出示例：
            {{
                "image_prompts": [
                    "明亮的实验室里，一个机器人站在科学家旁边，微笑着展示一个发明",
                    "机器人在户外帮助老人过马路，周围是绿树成荫的街道"
                ],
                "audio_prompts": [
                    "轻快的科技背景音乐，键盘敲击声",
                    "温馨的弦乐，鸟鸣声"
                ]
            }}
            """

            # 使用Qwen模型生成内容
            from core.qwen_nodes import DEVICE
            import torch

            # 设置种子
            if qwen_seed is not None:
                torch.manual_seed(qwen_seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed_all(qwen_seed)

            # 使用模型缓存管理器获取或加载模型
            global qwen_model, qwen_tokenizer
            if qwen_model is None or qwen_tokenizer is None:
                qwen_model = model_cache_manager.get_model("qwen_text_model")
                qwen_tokenizer = model_cache_manager.get_model("qwen_text_tokenizer")

            # 生成内容
            inputs = qwen_tokenizer(prompt_template, return_tensors="pt").to(DEVICE)
            outputs = qwen_model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.7,
                top_p=0.9,
                do_sample=True
            )

            # 解码生成的内容
            response = qwen_tokenizer.decode(outputs[0], skip_special_tokens=True)

            # 提取JSON部分
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("Could not find valid JSON in model response")
            
            json_response = response[json_start:json_end]
            storyboard_data = json.loads(json_response)

            # 验证输出格式
            if "image_prompts" not in storyboard_data or "audio_prompts" not in storyboard_data:
                raise ValueError("Invalid output format: missing image_prompts or audio_prompts")
                
            if len(storyboard_data["image_prompts"]) != scene_count or len(storyboard_data["audio_prompts"]) != scene_count:
                raise ValueError(f"Expected {scene_count} prompts per type, got {len(storyboard_data['image_prompts'])} image prompts and {len(storyboard_data['audio_prompts'])} audio prompts")

            return {
                "image_prompts": storyboard_data["image_prompts"],
                "audio_prompts": storyboard_data["audio_prompts"],
                "storyboard_json": json.dumps(storyboard_data),
                "success": True,
                "message": "Storyboard generated successfully"
            }

        except Exception as e:
            print(f"Error generating storyboard: {e}")
            return {
                "image_prompts": [],
                "audio_prompts": [],
                "storyboard_json": "",
                "success": False,
                "message": f"Error generating storyboard: {str(e)}"
            }


@register_node(
    name="video_scene_generator",
    description="Generate individual video scenes with independent seed control",
    category="video",
    icon="🎬"
)
class VideoSceneGeneratorNode(BaseNode):

    class Inputs(BaseNode.Inputs):
        image_prompt: str = text_area(
            default="",
            description="Image prompt for the video scene"
        )
        video_model: str = text_input(
            default="wang22_video_v1",
            description="Video model to use"
        )
        lora_strength: float = slider(
            default=0.7,
            min=0.0,
            max=1.0,
            step=0.1,
            description="LoRA strength"
        )
        denoise: float = slider(
            default=0.8,
            min=0.0,
            max=1.0,
            step=0.1,
            description="Denoise strength"
        )
        sampler_seed: str = text_input(
            default=None,
            description="Random seed for video generation"
        )

    class Outputs(BaseNode.Outputs):
        video_path: str
        success: bool
        message: str

    def __call__(self, image_prompt: str = "",
                 video_model: str = "wang22_video_v1",
                 lora_strength: float = 0.7,
                 denoise: float = 0.8,
                 sampler_seed: Optional[int] = None) -> dict:

        try:
            # 这里应该集成实际的视频生成模型
            # 目前使用占位符实现
            import os
            import tempfile
            
            # 创建一个临时视频文件路径（实际应用中应该使用真实的视频生成）
            temp_dir = tempfile.gettempdir()
            video_filename = f"scene_{sampler_seed or 'temp'}.mp4"
            video_path = os.path.join(temp_dir, video_filename)
            
            # 模拟视频生成过程
            # 在实际应用中，这里应该调用视频生成模型
            print(f"Generating video for prompt: {image_prompt[:50]}...")
            
            return {
                "video_path": video_path,
                "success": True,
                "message": f"Video generated successfully at {video_path}"
            }

        except Exception as e:
            print(f"Error generating video scene: {e}")
            return {
                "video_path": "",
                "success": False,
                "message": f"Error generating video scene: {str(e)}"
            }


@register_node(
    name="audio_scene_generator",
    description="Generate audio for video scenes with independent seed control",
    category="video",
    icon="🔊"
)
class AudioSceneGeneratorNode(BaseNode):

    class Inputs(BaseNode.Inputs):
        audio_prompt: str = text_area(
            default="",
            description="Audio prompt for the scene"
        )
        audio_model: str = text_input(
            default="stable_audio_v1",
            description="Audio model to use"
        )
        duration: int = slider(
            default=5,
            min=1,
            max=30,
            step=1,
            description="Audio duration in seconds"
        )
        audio_seed: str = text_input(
            default=None,
            description="Random seed for audio generation"
        )

    class Outputs(BaseNode.Outputs):
        audio_path: str
        success: bool
        message: str

    def __call__(self, audio_prompt: str = "",
                 audio_model: str = "stable_audio_v1",
                 duration: int = 5,
                 audio_seed: Optional[int] = None) -> dict:

        try:
            # 这里应该集成实际的音频生成模型
            # 目前使用占位符实现
            import os
            import tempfile
            
            # 创建一个临时音频文件路径（实际应用中应该使用真实的音频生成）
            temp_dir = tempfile.gettempdir()
            audio_filename = f"audio_{audio_seed or 'temp'}.wav"
            audio_path = os.path.join(temp_dir, audio_filename)
            
            # 模拟音频生成过程
            # 在实际应用中，这里应该调用音频生成模型
            print(f"Generating audio for prompt: {audio_prompt}...")
            
            return {
                "audio_path": audio_path,
                "success": True,
                "message": f"Audio generated successfully at {audio_path}"
            }

        except Exception as e:
            print(f"Error generating audio: {e}")
            return {
                "audio_path": "",
                "success": False,
                "message": f"Error generating audio: {str(e)}"
            }
