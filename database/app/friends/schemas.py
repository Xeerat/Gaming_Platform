
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class SFriend_request(BaseModel) :
    username_to : str =  Field(..., min_length=3, max_length=10, description="Username, от 3 до 10 символов")
