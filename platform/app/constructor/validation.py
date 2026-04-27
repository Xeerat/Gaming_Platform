from pydantic import BaseModel

from typing import List, Dict, Any, Optional


class SCharSave(BaseModel):
    """Модель для сохранения спрайта через JSON."""
    
    sprite_name: str
    sprite_type: str
    data: List[List[Dict[str, Any]]]


class SMapSave(BaseModel):
    """Модель для сохранения map через JSON."""
    
    map_name: str
    data: List[List[Dict[str, Any]]]


class SLogic(BaseModel):
    sprite_name: str
    name: str = "main"
    trigger_config: Optional[Dict[str, Any]] = None
    dialog_config: Optional[Dict[str, Any]] = None
    dialog_role: Optional[str] = None