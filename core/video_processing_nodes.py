import os
import subprocess
import tempfile
import uuid
from typing import Dict, Any
import base64
from io import BytesIO
from PIL import Image
import cv2

from .base_node import BaseNode, text_input, slider, combo, handle, toggle
from .node_registry import register_node
from .ffmpeg_manager import get_ffmpeg_path


@register_node(
    name="videoLoad",
    description="Video Load Node - Loads a video file and extracts metadata",
    category="video",
    icon="🎥"
)
class VideoLoadNode(BaseNode):
    class Inputs(BaseNode.Inputs):
        video_path: str = text_input(default="", description="Path to video file")
    
    class Outputs(BaseNode.Outputs):
        video_info: dict
        frame_count: int
        fps: float
        width: int
        height: int
    
    def __call__(self, video_path: str = "") -> dict:
        if not video_path or not os.path.exists(video_path):
            return {
                "video_info": {"error": "Invalid video path"},
                "frame_count": 0,
                "fps": 0,
                "width": 0,
                "height": 0
            }
        
        try:
            # 使用OpenCV获取视频信息
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {
                    "video_info": {"error": "Failed to open video"},
                    "frame_count": 0,
                    "fps": 0,
                    "width": 0,
                    "height": 0
                }
            
            # 获取视频属性
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # 释放视频捕获对象
            cap.release()
            
            return {
                "video_info": {"path": video_path, "success": True},
                "frame_count": frame_count,
                "fps": fps,
                "width": width,
                "height": height
            }
        except Exception as e:
            return {
                "video_info": {"error": f"Error: {str(e)}"},
                "frame_count": 0,
                "fps": 0,
                "width": 0,
                "height": 0
            }


@register_node(
    name="extractFrame",
    description="Extract Frame Node - Extracts a specific frame from a video",
    category="video",
    icon="🖼️"
)
class ExtractFrameNode(BaseNode):
    class Inputs(BaseNode.Inputs):
        video_path: str = text_input(default="", description="Path to video file")
        frame_index: int = slider(default=0, min=0, max=1000, step=1, description="Frame index to extract")
    
    class Outputs(BaseNode.Outputs):
        frame: str  # Base64 encoded image
        frame_info: dict
    
    def __call__(self, video_path: str = "", frame_index: int = 0) -> dict:
        if not video_path or not os.path.exists(video_path):
            return {
                "frame": "",
                "frame_info": {"error": "Invalid video path"}
            }
        
        try:
            # 使用OpenCV提取特定帧
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {
                    "frame": "",
                    "frame_info": {"error": "Failed to open video"}
                }
            
            # 获取视频总帧数
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # 检查帧索引是否有效
            if frame_index < 0 or frame_index >= total_frames:
                cap.release()
                return {
                    "frame": "",
                    "frame_info": {"error": f"Frame index {frame_index} is out of range (0-{total_frames-1})"}
                }
            
            # 设置视频位置到目标帧
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            
            # 读取帧
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return {
                    "frame": "",
                    "frame_info": {"error": "Failed to read frame"}
                }
            
            # 将BGR转换为RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 将帧转换为PIL图像
            pil_image = Image.fromarray(frame_rgb)
            
            # 将图像保存到BytesIO
            buffer = BytesIO()
            pil_image.save(buffer, format="PNG")
            frame_data = buffer.getvalue()
            
            # 转换为Base64
            base64_frame = base64.b64encode(frame_data).decode("utf-8")
            
            return {
                "frame": base64_frame,
                "frame_info": {
                    "video_path": video_path,
                    "frame_index": frame_index,
                    "format": "png",
                    "success": True
                }
            }
        except subprocess.CalledProcessError as e:
            return {
                "frame": "",
                "frame_info": {"error": f"FFmpeg error: {e.stderr}"}
            }
        except Exception as e:
            return {
                "frame": "",
                "frame_info": {"error": f"Error: {str(e)}"}
            }


@register_node(
    name="videoComposer",
    description="Video Composer Node - Composes frames into a video",
    category="video",
    icon="🎬"
)
class VideoComposerNode(BaseNode):
    class Inputs(BaseNode.Inputs):
        frames_dir: str = text_input(default="", description="Directory containing frames")
        output_path: str = text_input(default="output.mp4", description="Output video path")
        fps: float = slider(default=24.0, min=1.0, max=60.0, step=0.1, description="Frames per second")
        codec: str = combo(default="libx264", options=["libx264", "libx265", "libvpx"], description="Video codec")
    
    class Outputs(BaseNode.Outputs):
        video: str
        success: bool
        message: str
    
    def __call__(self, frames_dir: str = "", output_path: str = "output.mp4", fps: float = 24.0, codec: str = "libx264") -> dict:
        if not frames_dir or not os.path.exists(frames_dir):
            return {
                "video": "",
                "success": False,
                "message": "Invalid frames directory"
            }
        
        try:
            # 获取所有帧文件并排序
            frame_files = sorted([
                f for f in os.listdir(frames_dir)
                if f.endswith((".png", ".jpg", ".jpeg"))
            ])
            
            if not frame_files:
                return {
                    "video": "",
                    "success": False,
                    "message": "No frame files found"
                }
            
            # 使用FFmpeg将帧合成为视频
            cmd = [
                get_ffmpeg_path(),
                "-framerate", str(fps),
                "-i", os.path.join(frames_dir, "%d.png"),  # 假设帧文件命名为1.png, 2.png等
                "-c:v", codec,
                "-pix_fmt", "yuv420p",
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "video": output_path,
                "success": True,
                "message": f"Video created successfully: {output_path}"
            }
        except subprocess.CalledProcessError as e:
            return {
                "video": "",
                "success": False,
                "message": f"FFmpeg error: {e.stderr}"
            }
        except Exception as e:
            return {
                "video": "",
                "success": False,
                "message": f"Error: {str(e)}"
            }


@register_node(
    name="frameIndexManager",
    description="Frame Index Manager Node - Manages frame indices for video processing",
    category="video",
    icon="🔢"
)
class FrameIndexManagerNode(BaseNode):
    class Inputs(BaseNode.Inputs):
        current_frame: int = slider(default=0, min=0, max=1000, step=1, description="Current frame index")
        total_frames: int = slider(default=100, min=1, max=10000, step=1, description="Total number of frames")
        loop_mode: bool = toggle(default=False, description="Enable loop mode")
        reverse_mode: bool = toggle(default=False, description="Enable reverse mode")
    
    class Outputs(BaseNode.Outputs):
        frame_index: int
        is_first_frame: bool
        is_last_frame: bool
        progress: float
    
    def __call__(self, current_frame: int = 0, total_frames: int = 100, loop_mode: bool = False, reverse_mode: bool = False) -> dict:
        # 确保帧索引在有效范围内
        if total_frames <= 0:
            total_frames = 1
        
        if loop_mode:
            frame_index = current_frame % total_frames
        else:
            frame_index = max(0, min(current_frame, total_frames - 1))
        
        if reverse_mode:
            frame_index = total_frames - 1 - frame_index
        
        is_first_frame = frame_index == 0
        is_last_frame = frame_index == total_frames - 1
        progress = frame_index / (total_frames - 1) if total_frames > 1 else 0.0
        
        return {
            "frame_index": frame_index,
            "is_first_frame": is_first_frame,
            "is_last_frame": is_last_frame,
            "progress": progress
        }


@register_node(
    name="opticalFlowCalculator",
    description="Optical Flow Calculator Node - Calculates optical flow between frames",
    category="video",
    icon="🌊"
)
class OpticalFlowCalculatorNode(BaseNode):
    class Inputs(BaseNode.Inputs):
        video_path: str = text_input(default="", description="Path to video file")
        algorithm: str = combo(default="farneback", options=["farneback", "lucas-kanade"], description="Optical flow algorithm")
        start_frame: int = slider(default=0, min=0, max=1000, step=1, description="Start frame index")
        end_frame: int = slider(default=10, min=1, max=1000, step=1, description="End frame index")
    
    class Outputs(BaseNode.Outputs):
        flow_data: str  # Base64 encoded flow data
        flow_visualization: str  # Base64 encoded visualization
        flow_info: dict
    
    def __call__(self, video_path: str = "", algorithm: str = "farneback", start_frame: int = 0, end_frame: int = 10) -> dict:
        if not video_path or not os.path.exists(video_path):
            return {
                "flow_data": "",
                "flow_visualization": "",
                "flow_info": {"error": "Invalid video path"}
            }
        
        try:
            import numpy as np
            # 使用 OpenCV 实现光流计算
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return {
                    "flow_data": "",
                    "flow_visualization": "",
                    "flow_info": {"error": "Could not open video file"}
                }
            
            # 获取视频信息
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # 验证帧范围
            if start_frame < 0 or end_frame < 0 or start_frame >= total_frames or end_frame >= total_frames:
                cap.release()
                return {
                    "flow_data": "",
                    "flow_visualization": "",
                    "flow_info": {
                        "error": f"Frame range out of bounds. Total frames: {total_frames}"
                    }
                }
            
            # 读取第一帧
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            ret, prev_frame = cap.read()
            if not ret:
                cap.release()
                return {
                    "flow_data": "",
                    "flow_visualization": "",
                    "flow_info": {"error": "Could not read first frame"}
                }
            
            # 转换为灰度图
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            
            # 创建一个临时文件来保存光流可视化视频
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_flow_video:
                temp_flow_path = temp_flow_video.name
            
            # 设置视频编写器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_flow_path, fourcc, fps, (width, height))
            
            # 处理每一帧
            for frame_idx in range(start_frame + 1, end_frame + 1):
                ret, curr_frame = cap.read()
                if not ret:
                    break
                
                # 转换为灰度图
                curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
                
                # 计算光流
                if algorithm == "farneback":
                    flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                else:  # lucas-kanade
                    # 使用 Lucas-Kanade 方法
                    features = cv2.goodFeaturesToTrack(prev_gray, maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
                    if features is None:
                        flow = np.zeros((height, width, 2), dtype=np.float32)
                    else:
                        features_next, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, features, None)
                        
                        # 创建光流场
                        flow = np.zeros((height, width, 2), dtype=np.float32)
                        for i, (new, old) in enumerate(zip(features_next, features)):
                            if status[i] == 1:
                                a, b = new.ravel()
                                c, d = old.ravel()
                                flow[int(d), int(c)] = [a - c, b - d]
                
                # 可视化光流
                hsv = np.zeros_like(prev_frame)
                hsv[..., 1] = 255
                
                mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                hsv[..., 0] = ang * 180 / np.pi / 2
                hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
                bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                
                # 写入视频
                out.write(bgr)
                
                # 更新前一帧
                prev_gray = curr_gray.copy()
            
            # 释放资源
            cap.release()
            out.release()
            
            # 将光流视频转换为Base64
            with open(temp_flow_path, "rb") as f:
                flow_video_data = f.read()
            
            # 清理临时文件
            os.unlink(temp_flow_path)
            
            # 转换为Base64
            base64_flow = base64.b64encode(flow_video_data).decode("utf-8")
            
            return {
                "flow_data": base64_flow,
                "flow_visualization": base64_flow,  # 使用可视化视频作为简化处理
                "flow_info": {
                    "video_path": video_path,
                    "algorithm": algorithm,
                    "start_frame": start_frame,
                    "end_frame": end_frame,
                    "total_frames_processed": end_frame - start_frame,
                    "success": True
                }
            }
        except Exception as e:
            return {
                "flow_data": "",
                "flow_visualization": "",
                "flow_info": {
                    "error": f"Error: {str(e)}"
                }
            }
