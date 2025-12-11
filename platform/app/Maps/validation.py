
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from typing import List

class SMaps(BaseModel) :
    matrix : List[List[int]]
    map_name : str =  Field(..., min_length=1, max_length=10, description="Map_name должен быть от 1 до 10 символов")