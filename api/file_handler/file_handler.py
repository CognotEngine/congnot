import os
import uuid
import shutil
from typing import Dict, List, Optional, BinaryIO
from pathlib import Path
import mimetypes

class FileHandler:
    def __init__(self, upload_dir: str = "./uploads"):
        
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        
        self.image_dir = self.upload_dir / "images"
        self.audio_dir = self.upload_dir / "audio"
        self.video_dir = self.upload_dir / "video"
        self.document_dir = self.upload_dir / "documents"
        self.other_dir = self.upload_dir / "other"
        
        
        for dir_path in [self.image_dir, self.audio_dir, self.video_dir, self.document_dir, self.other_dir]:
            dir_path.mkdir(exist_ok=True)
        
        
        self.supported_types = {
            "image": ["image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"],
            "audio": ["audio/mpeg", "audio/wav", "audio/ogg", "audio/flac"],
            "video": ["video/mp4", "video/avi", "video/mov", "video/webm"],
            "document": ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                         "text/plain", "text/csv", "application/json", "application/javascript"]
        }
    
    def _get_file_type(self, content_type: str) -> str:
        
        for file_type, types in self.supported_types.items():
            if content_type in types:
                return file_type
        return "other"
    
    def _get_file_extension(self, content_type: str) -> str:
        
        ext = mimetypes.guess_extension(content_type)
        return ext if ext else ".bin"
    
    def _get_storage_path(self, file_type: str) -> Path:
        
        paths = {
            "image": self.image_dir,
            "audio": self.audio_dir,
            "video": self.video_dir,
            "document": self.document_dir,
            "other": self.other_dir
        }
        return paths.get(file_type, self.other_dir)
    
    def upload_file(self, file: BinaryIO, content_type: str, filename: Optional[str] = None) -> Dict:
        
        
        file_type = self._get_file_type(content_type)
        
        
        file_ext = self._get_file_extension(content_type)
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        
        storage_path = self._get_storage_path(file_type)
        
        
        file_path = storage_path / unique_filename
        
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file, buffer)
        
        
        return {
            "file_id": str(uuid.uuid4()),
            "filename": filename or unique_filename,
            "storage_filename": unique_filename,
            "file_type": file_type,
            "content_type": content_type,
            "file_size": file_path.stat().st_size,
            "storage_path": str(file_path),
            "relative_path": str(file_path.relative_to(self.upload_dir)),
            "upload_time": file_path.stat().st_ctime
        }
    
    def download_file(self, file_path: str) -> Optional[Path]:
        
        
        if not file_path.startswith(str(self.upload_dir)):
            file_path = self.upload_dir / file_path
        
        file_path = Path(file_path)
        
        
        if file_path.exists() and file_path.is_file():
            return file_path
        
        return None
    
    def delete_file(self, file_path: str) -> bool:
        
        
        if not file_path.startswith(str(self.upload_dir)):
            file_path = self.upload_dir / file_path
        
        file_path = Path(file_path)
        
        
        if file_path.exists() and file_path.is_file():
            try:
                file_path.unlink()
                return True
            except Exception:
                return False
        
        return False
    
    def list_files(self, file_type: Optional[str] = None) -> List[Dict]:
        
        files = []
        
        
        if file_type:
            target_dir = self._get_storage_path(file_type)
            directories = [target_dir]
        else:
            directories = [self.image_dir, self.audio_dir, self.video_dir, self.document_dir, self.other_dir]
        
        
        for directory in directories:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    
                    content_type, _ = mimetypes.guess_type(str(file_path))
                    
                    files.append({
                        "filename": file_path.name,
                        "file_type": directory.name,
                        "content_type": content_type or "application/octet-stream",
                        "file_size": file_path.stat().st_size,
                        "storage_path": str(file_path),
                        "relative_path": str(file_path.relative_to(self.upload_dir)),
                        "upload_time": file_path.stat().st_ctime,
                        "last_modified": file_path.stat().st_mtime
                    })
        
        
        files.sort(key=lambda x: x["upload_time"], reverse=True)
        
        return files
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        
        
        if not file_path.startswith(str(self.upload_dir)):
            file_path = self.upload_dir / file_path
        
        file_path = Path(file_path)
        
        
        if file_path.exists() and file_path.is_file():
            
            content_type, _ = mimetypes.guess_type(str(file_path))
            
            return {
                "filename": file_path.name,
                "file_type": file_path.parent.name,
                "content_type": content_type or "application/octet-stream",
                "file_size": file_path.stat().st_size,
                "storage_path": str(file_path),
                "relative_path": str(file_path.relative_to(self.upload_dir)),
                "upload_time": file_path.stat().st_ctime,
                "last_modified": file_path.stat().st_mtime
            }
        
        return None
    
    def clean_old_files(self, days: int = 30) -> int:
        
        import time
        
        deleted_count = 0
        cutoff_time = time.time() - (days * 86400)  
        
        
        for directory in [self.image_dir, self.audio_dir, self.video_dir, self.document_dir, self.other_dir]:
            for file_path in directory.iterdir():
                if file_path.is_file() and file_path.stat().st_ctime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception:
                        continue
        
        return deleted_count

file_handler = FileHandler()
