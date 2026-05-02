from pydantic import BaseModel
from typing import Dict, Any, Optional


class SNovelSave(BaseModel):
    title: str = "Без названия"
    data: Dict[str, Any]
    preview: Optional[str]