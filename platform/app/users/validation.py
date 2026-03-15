from pydantic import BaseModel, EmailStr, model_validator
from fastapi import Form 


class SUserRegister(BaseModel):
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
        description="Пароль, от 8 до 15 знаков"
    )
    confirm_password: str = Form(
        ..., 
        min_length=8, 
        max_length=15, 
        description="Повторный пароль, от 8 до 15 знаков"
    )

    @model_validator(mode="after")
    def match_password(self):
        """Проверяет совпадение паролей."""
        
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        return self


class SUserAuth(BaseModel):
    """Проверка валидности данных при аутентификации."""
    
    email: EmailStr = Form(
        ..., 
        description="Электронная почта",
    )
    password: str = Form(
        ..., 
        min_length=8, 
        max_length=15, 
        description="Пароль, от 8 до 15 знаков",
    )


class SUserForgotPassword(BaseModel):
    """Валидация данных первой страницы вкладки 'Забыли пароль?'"""

    email: EmailStr = Form(
        ...,
        description="Электронная почта",
    )


class SUserUpdatePassword(BaseModel):
    """Валидация данных второй страницы вкладки 'Забыли пароль?'"""

    password: str = Form(
        ...,
        min_length=8, 
        max_length=15,
        description="Пароль от 8 до 15 знаков",
    )
    confirm_password: str = Form(
        ..., 
        min_length=8, 
        max_length=15, 
        description="Повторный пароль, от 8 до 15 знаков",
    )
    token: str = Form(
        None,
        description="Токен отправленый на почту",
    )

    @model_validator(mode="after")
    def match_password(self):
        """Проверяет совпадение паролей."""
        
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")
        return self