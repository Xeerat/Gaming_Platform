
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

# если что EmailStr сразу просматривает валидность почты, поэтму дополнительной тут нет

class SUserRegister(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=5, max_length=10, description="Пароль, от 5 до 10 знаков")
    username: str = Field(..., min_length=3, max_length=10, description="Username, от 3 до 10 символов")

class SUserAuth(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=5, max_length=10, description="Пароль, от 5 до 10 знаков")