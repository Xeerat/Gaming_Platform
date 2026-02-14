from pydantic import EmailStr, model_validator
from fastapi import Form 
from fastapi.responses import RedirectResponse
from dataclasses import dataclass

@dataclass
class SUserRegister:
    """Валидация данных при регистрации."""

    email: EmailStr = Form(
        ..., 
        description="Электронная почта"
    )
    username: str = Form(
        ..., 
        min_length=3, 
        max_length=15, 
        description="Username, от 3 до 15 символов"
    )
    password: str = Form(
        ...,
        min_length=8, 
        max_length=15, 
        description="Пароль"
    )
    confirm_password: str = Form(
        ..., 
        min_length=8, 
        max_length=15, 
        description="Пароль, от 8 до 15 знаков"
    )

    @model_validator(mode="after")
    def match_password(self):
        """Проверяет совпадение паролей."""
        
        if self.password != self.confirm_password:
            return RedirectResponse(
                "/auth/register/?error=Пароли+не+совпадают!",
                status_code=303
            )
        return self


#=========================================================
# Проверка валидности при авторизации
#=========================================================

class SUserAuth:
    """ Класс проверки валидности данных при авторизации """
    email: EmailStr = Form(..., description="Электронная почта")
    password: str = Form(..., min_length=8, max_length=15, description="Пароль, от 8 до 15 знаков")