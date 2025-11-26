from pydantic import BaseModel, EmailStr, Field 

#=========================================================
# Проверка валидности при регистрации
#=========================================================

class SUserRegister(BaseModel):
    """ Класс проверки валидности данных при регистрации """
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=5, max_length=15, description="Пароль, от 5 до 15 знаков")
    username: str = Field(..., min_length=3, max_length=10, description="Username, от 3 до 10 символов")

#=========================================================
# Проверка валидности при авторизации
#=========================================================

class SUserAuth(BaseModel):
    """ Класс проверки валидности данных при авторизации """
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=5, max_length=15, description="Пароль, от 5 до 15 знаков")