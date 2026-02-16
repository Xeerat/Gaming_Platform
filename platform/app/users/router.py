from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose.exceptions import ExpiredSignatureError, JWTError

from dao.dao_models import UsersDAO
from users.validation import SUserRegister, SUserAuth
from users.auth import get_password_hash, create_access_token, verify_password
from users.auth import decode_access_token, send_verification_email

from urllib.parse import quote


router = APIRouter(prefix='/auth', tags=['Auth'])


def redirect_message(
        url: str, 
        message: str = "", 
        error: bool = None, 
        success: bool = None,
) -> RedirectResponse:
    """
    Формирует и возвращает RedirectResponse.

    Args:
        url: ссылка для перехода по нужному маршруту.
        message: сообщение которое нужно отправить по маршруту.
        error: флаг, если нужно передать ошибку.
        success: флаг, если нужно передать успех.
    
    Returns:
        Возвращает RedirectResponse cо сформированной ссылкой.
    """

    type_message = ""
    if error:
        type_message = "error="
    elif success:
        type_message = "success="

    return RedirectResponse(
        url=f"{url}?{type_message}{quote(message)}", 
        status_code=303,
    )


@router.post("/register/")
async def register_user(request: Request) -> RedirectResponse:
    """Регистрирует пользователя на платформе."""

    form = await request.form()
    try:
        data = SUserRegister(**form)
        await UsersDAO.add_user(
            username=data.username,
            email=data.email,
            password=get_password_hash(data.password),
        )

    except ValidationError:
        message="Пароли не совпадают."

    except IntegrityError as e:
        if "email" in str(e.orig):
            message="Пользователь с таким email уже существует."
        else:
            message="Пользователь с таким именем уже существует."

    except SQLAlchemyError:
        message="Возникла ошибка при добавлении пользователя."

    else:
        await send_verification_email(email=data.email)
        return redirect_message(url="/auth/verify-email")
    
    return redirect_message(
        url="/auth/register/",
        message=message,
        error=True,
    )


@router.post("/login/")
async def auth_user(data: SUserAuth = Depends()) -> RedirectResponse:
    """Аутентифицирует пользователя на платформе."""

    user = await UsersDAO.find_user(email=data.email)
    if not user or not verify_password(data.password, user.password):
        return redirect_message(
            url="/auth/login/",
            message="Неверная почта или пароль",
            error=True,
        )

    response = redirect_message(url="/main/")
    token = create_access_token(email=data.email)
    response.set_cookie(key="users_access_token", value=token, httponly=True)
    return response


@router.get("/logout/")
async def logout_user() -> RedirectResponse:
    """Разлогинивает пользователя с платформы."""

    response = redirect_message(url='/auth/login/')
    response.delete_cookie(key="users_access_token")
    return response


@router.post("/del/")
async def delete_user(request: Request) -> RedirectResponse:
    """Удаляет аккаунт пользователя с платформы."""

    token = request.cookies.get("users_access_token")
    try:
        data = decode_access_token(token)
        result = await UsersDAO.delete_user(email=data.get('email'))
        if not result:
            return redirect_message(
                url="/auth/login/",
                message="Такой пользователь не зарегистрирован.",
                error=True,
            )

    except ExpiredSignatureError:
        message = "Истек срок годности токена."
        url = "/main/"

    except JWTError:
        message = "Пользователь не авторизован."
        url = "/auth/login/"

    except SQLAlchemyError:
        message = "Возникла ошибка при удалении пользователя."
        url = "/main/"

    else:
        response = redirect_message(
            url="/auth/login/",
            message="Удаление прошло успешно!", 
            success=True,
        )
        response.delete_cookie(key="users_access_token")
        return response
    
    return redirect_message(url=url, message=message, error=True)
    

@router.post("/verify-email")
async def verify_email(token: str = Form(...)):
    """Переводит пользователя на его аккаунт после подтверждения почты."""

    try:
        data = decode_access_token(token)
        user = await UsersDAO.find_user(email=data["email"])
        if not user:
            return redirect_message(
                url="/auth/login/",
                message="Невалидный токен.",
                error=True,
            )

    except ExpiredSignatureError:
        message = "Истек срок годности токена."

    except JWTError:
        message = "Невалидный токен."

    else:
        response = redirect_message(
            url="/main/",
            message="Вы успешно зарегистрированы!",
            success=True,
        )
        token = create_access_token(email=data["email"])
        response.set_cookie(
            key="users_access_token", 
            value=token,
            httponly=True,
        )
        return response

    return redirect_message(
        url="/auth/login/",
        message=message,
        error=True,
    )