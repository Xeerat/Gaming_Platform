
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from typing import List

class SChar(BaseModel) :
    matrix : List[List[int]]
    char_name : str =  Field(..., min_length=1, max_length=10, description="Char_name должен быть от 1 до 10 символов")