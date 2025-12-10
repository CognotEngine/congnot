import os
import sys
import subprocess
import logging
from typing import Optional

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FFmpeg路径管理器
class FFmpegManager:
    def __init__(self):
        self.ffmpeg_path: Optional[str] = None
        self.ffprobe_path: Optional[str] = None
        self._initialize_ffmpeg()
    
    def _initialize_ffmpeg(self):
        """
        初始化FFmpeg路径
        1. 首先尝试使用imageio-ffmpeg提供的二进制文件
        2. 如果失败，尝试从系统PATH中查找
        3. 如果仍然失败，记录警告但不抛出异常
        """
        try:
            # 尝试从imageio-ffmpeg获取FFmpeg路径
            from imageio_ffmpeg import get_ffmpeg_exe
            self.ffmpeg_path = get_ffmpeg_exe()
            # 构造ffprobe路径（通常与ffmpeg在同一目录）
            ffmpeg_dir = os.path.dirname(self.ffmpeg_path)
            
            # 查找ffprobe文件（可能有不同的命名格式）
            self.ffprobe_path = None
            for file in os.listdir(ffmpeg_dir):
                if file.startswith('ffprobe'):
                    self.ffprobe_path = os.path.join(ffmpeg_dir, file)
                    break
            
            # 如果找不到，尝试使用与ffmpeg相似的命名格式
            if not self.ffprobe_path:
                ffmpeg_filename = os.path.basename(self.ffmpeg_path)
                ffprobe_filename = ffmpeg_filename.replace('ffmpeg', 'ffprobe')
                self.ffprobe_path = os.path.join(ffmpeg_dir, ffprobe_filename)
            
            logger.info(f"Found FFmpeg at: {self.ffmpeg_path}")
            logger.info(f"Found FFprobe at: {self.ffprobe_path}")
            
        except Exception as e:
            logger.warning(f"Failed to get FFmpeg from imageio-ffmpeg: {e}")
            # 尝试从系统PATH中查找，但不强制要求找到
            try:
                self._find_ffmpeg_in_path()
            except Exception as path_e:
                logger.warning(f"Failed to find FFmpeg in system PATH: {path_e}")
                # 继续运行，不抛出异常
    
    def _find_ffmpeg_in_path(self):
        """从系统PATH中查找FFmpeg"""
        try:
            # 尝试运行ffmpeg命令
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                # 获取FFmpeg路径
                if sys.platform == 'win32':
                    try:
                        where_result = subprocess.run(['where', 'ffmpeg'], capture_output=True, text=True, check=True)
                        self.ffmpeg_path = where_result.stdout.strip().split('\n')[0]
                        where_result = subprocess.run(['where', 'ffprobe'], capture_output=True, text=True, check=True)
                        self.ffprobe_path = where_result.stdout.strip().split('\n')[0]
                    except subprocess.CalledProcessError:
                        logger.warning("Could not find FFmpeg paths using where command")
                        return False
                else:
                    try:
                        which_result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True, check=True)
                        self.ffmpeg_path = which_result.stdout.strip()
                        which_result = subprocess.run(['which', 'ffprobe'], capture_output=True, text=True, check=True)
                        self.ffprobe_path = which_result.stdout.strip()
                    except subprocess.CalledProcessError:
                        logger.warning("Could not find FFmpeg paths using which command")
                        return False
                
                logger.info(f"Found FFmpeg in PATH at: {self.ffmpeg_path}")
                logger.info(f"Found FFprobe in PATH at: {self.ffprobe_path}")
                return True
            else:
                logger.warning("FFmpeg command returned non-zero exit code")
                return False
            
        except FileNotFoundError:
            logger.warning("FFmpeg executable not found in system PATH")
            return False
        except Exception as e:
            logger.warning(f"Error while checking FFmpeg in PATH: {e}")
            return False
    
    def get_ffmpeg_path(self) -> str:
        """获取FFmpeg可执行文件路径"""
        if self.ffmpeg_path and os.path.exists(self.ffmpeg_path):
            return self.ffmpeg_path
        raise FileNotFoundError("FFmpeg executable not found. Please ensure FFmpeg is installed or imageio-ffmpeg is properly installed.")
    
    def get_ffprobe_path(self) -> str:
        """获取FFprobe可执行文件路径"""
        if self.ffprobe_path:
            # 尝试直接使用找到的路径，不进行严格的存在性检查
            # 因为imageio-ffmpeg的二进制文件路径可能有特殊处理
            return self.ffprobe_path
        
        # 如果没有找到，尝试从系统PATH中查找
        self._find_ffmpeg_in_path()
        if self.ffprobe_path:
            return self.ffprobe_path
        
        raise FileNotFoundError("FFprobe executable not found. Please ensure FFmpeg is installed or imageio-ffmpeg is properly installed.")
    
    def test_ffmpeg(self) -> bool:
        """测试FFmpeg是否正常工作"""
        try:
            result = subprocess.run(
                [self.get_ffmpeg_path(), '-version'],
                capture_output=True, text=True, check=True
            )
            logger.info(f"FFmpeg version: {result.stdout.splitlines()[0]}")
            return True
        except Exception as e:
            logger.error(f"FFmpeg test failed: {e}")
            return False

# 创建全局FFmpeg管理器实例
ffmpeg_manager = FFmpegManager()

# 导出函数供其他模块使用
def get_ffmpeg_path() -> str:
    """获取FFmpeg可执行文件路径"""
    return ffmpeg_manager.get_ffmpeg_path()

def get_ffprobe_path() -> str:
    """获取FFprobe可执行文件路径"""
    return ffmpeg_manager.get_ffprobe_path()

def test_ffmpeg() -> bool:
    """测试FFmpeg是否正常工作"""
    return ffmpeg_manager.test_ffmpeg()
