

import os
import json
import uuid
from typing import List, Dict, Any, Optional

class PresetManager:
    
    
    def __init__(self, storage_file: str = "presets.json"):
        
        self.storage_file = storage_file
        self.presets_dir = "api/presets"
        self.presets_file = os.path.join(self.presets_dir, storage_file)
        
        
        if not os.path.exists(self.presets_dir):
            os.makedirs(self.presets_dir)
        
        
        if not os.path.exists(self.presets_file):
            self._save_presets([])
    
    def _load_presets(self) -> List[Dict[str, Any]]:
        
        try:
            with open(self.presets_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_presets(self, presets: List[Dict[str, Any]]):
        
        with open(self.presets_file, 'w', encoding='utf-8') as f:
            json.dump(presets, f, indent=2, ensure_ascii=False)
    
    def get_all_presets(self) -> List[Dict[str, Any]]:
        
        return self._load_presets()
    
    def get_preset(self, preset_id: str) -> Optional[Dict[str, Any]]:
        
        presets = self._load_presets()
        return next((preset for preset in presets if preset["id"] == preset_id), None)
    
    def save_preset(self, preset_data: Dict[str, Any]) -> Dict[str, Any]:
        
        presets = self._load_presets()
        
        
        preset_id = preset_data.get("id", str(uuid.uuid4()))
        
        
        preset_index = next((i for i, p in enumerate(presets) if p["id"] == preset_id), None)
        
        
        preset = {
            "id": preset_id,
            "name": preset_data.get("name", "Untitled Preset"),
            "data": preset_data.get("data", {}),
            "createdAt": preset_data.get("createdAt", str(uuid.uuid4())) if preset_index is None else presets[preset_index]["createdAt"],
            "updatedAt": str(uuid.uuid4())
        }
        
        if preset_index is not None:
            
            presets[preset_index] = preset
        else:
            
            presets.append(preset)
        
        
        self._save_presets(presets)
        
        return preset
    
    def delete_preset(self, preset_id: str) -> bool:
        
        presets = self._load_presets()
        new_presets = [preset for preset in presets if preset["id"] != preset_id]
        
        if len(new_presets) < len(presets):
            self._save_presets(new_presets)
            return True
        
        return False

preset_manager = PresetManager()