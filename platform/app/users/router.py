from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose.exceptions import ExpiredSignatureError, JWTError

from dao.dao_models import UsersDAO
from users.validation import SUserRegister, SUserAuth, SUserForgotPassword
from users.validation import SUserUpdatePassword
from users.auth import get_password_hash, create_access_token, verify_password
from users.auth import decode_access_token, send_verification_email

from urllib.parse import quote


router = APIRouter(prefix='/auth', tags=['Auth'])


def redirect_message(
        url: str, 
        message: str = "", 
        error: bool = None, 
        success: bool = None,
        token: str = None,
) -> RedirectResponse:
    """
    Формирует и возвращает RedirectResponse.

    Args:
        url: ссылка для перехода по нужному маршруту.
        message: сообщение которое нужно отправить по маршруту.
        error: флаг, если нужно передать ошибку.
        success: флаг, если нужно передать успех.
        token: токен, который нужно передать на страницу.
    
    Returns:
        Возвращает RedirectResponse cо сформированной ссылкой.
    """

    type_message = ""
    if error:
        type_message = "error="
    elif success:
        type_message = "success="

    add_token = ""
    if token:
        add_token = f"&token={token}"

    return RedirectResponse(
        url=f"{url}?{type_message}{quote(message)}{add_token}", 
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
        await send_verification_email(
            email=data.email,
            title="Подтверждение почты.",
            text="Подтвердите вашу почту, перейдя по ссылке:",
            url_for_token="/auth/verify-email",
        )
        return redirect_message(url="/auth/verify-email")
    
    return redirect_message(
        url="/auth/register/",
        message=message,
        error=True,
    )


@router.post("/login/")
async def auth_user(request: Request) -> RedirectResponse:
    """Аутентифицирует пользователя на платформе."""
    
    form = await request.form()
    try:
        data = SUserAuth(**form)

    except ValidationError:
        return redirect_message(
            url="/auth/login/",
            message="Введена некорректная электронная почта.",
            error=True,
        )
    
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
        email = decode_access_token(token)
        result = await UsersDAO.delete_user(email=email)
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
async def verify_email(request: Request) -> RedirectResponse:
    """Переводит пользователя на его аккаунт после подтверждения почты."""

    form = await request.form()
    token = dict(form).get("token")
    try:
        email = decode_access_token(token)
        user = await UsersDAO.find_user(email=email)
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
        token = create_access_token(email=email)
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


@router.post("/forgot_password/")
async def forgot_password_user(request: Request) -> RedirectResponse:
    """Обрабатывает первую страницу вкладки 'Забыли пароль?'"""

    form = await request.form()
    try:
        data = SUserForgotPassword(**form)

    except ValidationError:
        return redirect_message(
            url="/auth/forgot_password/",
            message="Введена некорректная электронная почта.",
            error=True,
        )

    found = await UsersDAO.find_user(email=data.email)
    if not found:
        return redirect_message(
            url="/auth/forgot_password/",
            message="Такой пользователь не зарегистрирован.",
            error=True,
        )

    await send_verification_email(
        email=data.email,
        title="Смена пароля.",
        text="Перейдите по ссылке, чтобы сменить пароль:",
        url_for_token="/auth/forgot_password/",
    )

    return redirect_message(
        url="/auth/forgot_password/",
        message="Вам на почту отправлено письмо для смены пароля.",
        success=True,
    )


@router.post("/update_password/")
async def update_password_user(request: Request) -> RedirectResponse:
    """Обрабатывает вторую страницу вкладки 'Забыли пароль?'"""

    form = await request.form()
    try:
        data = SUserUpdatePassword(**form)
        email = decode_access_token(token=data.token)
        new_password = get_password_hash(password=data.password)
        await UsersDAO.update_user_password(email=email, password=new_password)
    
    except ValidationError:
        return redirect_message(
            url="/auth/update_password/",
            message="Пароли не совпадают",
            error=True,
            token=dict(form).get("token")
        )
    
    except ExpiredSignatureError:
        message = "Истек срок годности токена."

    except JWTError:
        message = "Невалидный токен."
    
    except SQLAlchemyError:
        message = "Возникла ошибка при обновлении пароля."

    else:
        response = redirect_message(
            url="/main/",
            message="Пароль успешно изменен.",
            success=True,
        )
        token = create_access_token(email=email)
        response.set_cookie(
            key="users_access_token", 
            value=token, 
            httponly=True
        )
        return response

    return redirect_message(
        url="/auth/login/",
        message=message,
        error=True,
    )