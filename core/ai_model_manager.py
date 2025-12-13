import os
import yaml
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AIModelManager:
    """AI模型管理器"""
    
    def __init__(self, ai_system_path: str):
        self.ai_system_path = ai_system_path
        self.model_config = self._load_model_config()
        self.model_paths = self._build_model_paths()
        # 添加用户友好的模型类型映射
        self.model_type_mapping = {
            'base': 'checkpoints',        # 将'base'映射到'checkpoints'
            'lora': 'loras',              # 将'lora'映射到'loras'
            'vae': 'vae',                 # 'vae'保持不变
            'text_encoder': 'text_encoders',  # 添加文本编码器
            'clip_vision': 'clip_vision',     # 添加CLIP视觉模型
            'controlnet': 'controlnet',       # 添加ControlNet模型
            'embedding': 'embeddings',        # 添加嵌入模型
            'upscale': 'upscale_models',      # 添加超分辨率模型
            'hunyuan_video': 'hunyuan_video'  # 添加HunyuanVideo模型
        }
    
    def _load_model_config(self) -> Dict[str, Dict[str, str]]:
        """加载模型配置"""
        config_paths = [
            os.path.join(self.ai_system_path, "extra_model_paths.yaml"),
            os.path.join(self.ai_system_path, "extra_model_paths.yaml.example")
        ]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        return yaml.safe_load(f) or {}
                except yaml.YAMLError as e:
                    logger.error(f"Failed to parse model config: {config_path}, Error: {e}")
                    return {}
        
        logger.warning("No model config found, using default paths")
        return {}
    
    def _build_model_paths(self) -> Dict[str, List[str]]:
        """构建模型路径字典"""
        # 使用uploads/models/作为默认模型路径
        uploads_path = os.path.join(os.path.dirname(__file__), "..", "uploads", "models")
        uploads_path = os.path.abspath(uploads_path)
        
        default_paths = {
            'checkpoints': [os.path.join(uploads_path, "checkpoints")],
            'text_encoders': [os.path.join(uploads_path, "text_encoders")],
            'clip_vision': [os.path.join(uploads_path, "clip_vision")],
            'controlnet': [os.path.join(uploads_path, "controlnet")],
            'loras': [os.path.join(uploads_path, "loras")],
            'vae': [os.path.join(uploads_path, "vae")],
            'embeddings': [os.path.join(uploads_path, "embeddings")],
            'upscale_models': [os.path.join(uploads_path, "upscale_models")],
            'hunyuan_video': [os.path.join(uploads_path, "hunyuan_video")]  # 添加HunyuanVideo模型路径
        }
        
        # 从配置文件中加载自定义路径
        for config_name, config in self.model_config.items():
            if 'base_path' in config:
                base_path = config['base_path']
                for model_type, path in config.items():
                    if model_type == 'base_path' or model_type == 'is_default':
                        continue
                    
                    if model_type not in default_paths:
                        default_paths[model_type] = []
                    
                    if isinstance(path, str):
                        # 处理多行路径字符串
                        paths = [p.strip() for p in path.split('\n') if p.strip()]
                        for p in paths:
                            full_path = os.path.join(base_path, p)
                            if full_path not in default_paths[model_type]:
                                default_paths[model_type].append(full_path)
                    elif isinstance(path, list):
                        # 处理路径列表
                        for p in path:
                            full_path = os.path.join(base_path, p)
                            if full_path not in default_paths[model_type]:
                                default_paths[model_type].append(full_path)
        
        return default_paths
    
    def get_available_models(self, model_type: str) -> List[str]:
        """获取指定类型的可用模型列表
        
        Args:
            model_type: 模型类型，如 'base', 'vae', 'lora' 等
            
        Returns:
            可用模型文件路径列表
        """
        # 检查是否是用户友好的模型类型
        if model_type in self.model_type_mapping:
            model_type = self.model_type_mapping[model_type]
        
        if model_type not in self.model_paths:
            return []
        
        available_models = []
        supported_extensions = {'.ckpt', '.safetensors', '.pt', '.pth'}
        
        for path in self.model_paths[model_type]:
            if os.path.exists(path):
                try:
                    for filename in os.listdir(path):
                        file_path = os.path.join(path, filename)
                        if os.path.isfile(file_path):
                            ext = os.path.splitext(filename)[1].lower()
                            if ext in supported_extensions:
                                available_models.append(file_path)
                except Exception as e:
                    logger.error(f"Failed to list models in {path}: {e}")
        
        return available_models
    
    def get_model_info(self, model_path: str) -> Dict[str, str]:
        """获取模型信息
        
        Args:
            model_path: 模型文件路径
            
        Returns:
            模型信息字典
        """
        filename = os.path.basename(model_path)
        model_type = self._get_model_type_from_path(model_path)
        
        return {
            'path': model_path,
            'name': filename,
            'type': model_type,
            'size': os.path.getsize(model_path) if os.path.exists(model_path) else 0
        }
    
    def _get_model_type_from_path(self, model_path: str) -> str:
        """从路径推断模型类型"""
        for model_type, paths in self.model_paths.items():
            for path in paths:
                if model_path.startswith(path):
                    # 将内部模型类型转换为用户友好的类型
                    for friendly_type, internal_type in self.model_type_mapping.items():
                        if model_type == internal_type:
                            return friendly_type
                    return model_type
        return 'unknown'
    
    def get_user_friendly_model_types(self) -> List[str]:
        """获取用户友好的模型类型列表
        
        Returns:
            用户友好的模型类型列表
        """
        return list(self.model_type_mapping.keys())
    
    def upload_model(self, model_type: str, file_content: bytes, filename: str) -> bool:
        """上传模型到指定类型的目录
        
        Args:
            model_type: 模型类型
            file_content: 模型文件内容
            filename: 模型文件名
            
        Returns:
            上传是否成功
        """
        # 检查是否是用户友好的模型类型
        if model_type in self.model_type_mapping:
            model_type = self.model_type_mapping[model_type]
        
        if model_type not in self.model_paths or not self.model_paths[model_type]:
            logger.error(f"Invalid model type: {model_type}")
            return False
        
        # 使用第一个路径作为上传目录
        upload_path = self.model_paths[model_type][0]
        
        # 确保目录存在
        if not os.path.exists(upload_path):
            try:
                os.makedirs(upload_path)
            except Exception as e:
                logger.error(f"Failed to create upload directory: {upload_path}, Error: {e}")
                return False
        
        # 保存文件
        file_path = os.path.join(upload_path, filename)
        try:
            with open(file_path, 'wb') as f:
                f.write(file_content)
            logger.info(f"Model uploaded successfully: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save model file: {file_path}, Error: {e}")
            return False
    
    def delete_model(self, model_path: str) -> bool:
        """删除指定路径的模型
        
        Args:
            model_path: 模型文件路径
            
        Returns:
            删除是否成功
        """
        if not os.path.exists(model_path):
            logger.error(f"Model not found: {model_path}")
            return False
        
        # 验证模型路径是否在管理范围内
        is_managed = False
        for paths in self.model_paths.values():
            for path in paths:
                if model_path.startswith(path):
                    is_managed = True
                    break
            if is_managed:
                break
        
        if not is_managed:
            logger.error(f"Model path is not managed by AIModelManager: {model_path}")
            return False
        
        try:
            os.remove(model_path)
            logger.info(f"Model deleted successfully: {model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete model: {model_path}, Error: {e}")
            return False

# 创建全局实例
ai_system_path = "f:\goting\Cognot\AI-System-master\AI-System-master"
if not os.path.exists(ai_system_path):
    # 如果路径不存在，尝试使用相对路径
    ai_system_path = os.path.join(os.path.dirname(__file__), "..", "AI-System-master", "AI-System-master")
    ai_system_path = os.path.abspath(ai_system_path)

ai_model_manager = AIModelManager(ai_system_path)
