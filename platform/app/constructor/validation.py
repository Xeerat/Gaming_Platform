from pydantic import BaseModel, EmailStr, model_validator
from fastapi import Form 
from typing import List, Dict, Any


class SCharSave(BaseModel):
    """Модель для сохранения спрайта через JSON."""
    
    sprite_name: str
    data: List[List[Dict[str, Any]]]

class SMapSave(BaseModel):
    """Модель для сохранения map через JSON."""
    
    map_name: str
    data: List[List[Dict[str, Any]]]