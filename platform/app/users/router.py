from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from dao.dao_models import UsersDAO
from users.validation import SUserRegister, SUserAuth
from users.auth import get_password_hash, create_access_token, verify_password
from users.auth import decode_access_token, send_verification_email


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post("/register/")
async def register_user(request: Request) -> RedirectResponse:
    """Регистрирует пользователя на платформе."""

    form = await request.form()
    try:
        data = SUserRegister(**form)
    except ValidationError:
        return RedirectResponse(
            url="/auth/register/?error=Пароли+не+совпадают.",
            status_code=303,
        )
    
    try:
        await UsersDAO.add_user(
            username=data.username,
            email=data.email,
            password=get_password_hash(data.password),
        )
    except IntegrityError as error:
        if "email" in str(error.orig):
            return RedirectResponse(
                url="/auth/register/?error= \
                Пользователь+с+таким+email+уже+существует.",
                status_code=303,
            )
        else:
            return RedirectResponse(
                url="/auth/register/?error= \
                Пользователь+с+таким+именем+уже+существует!",
                status_code=303,
            )
    except SQLAlchemyError:
        return RedirectResponse(
            url="/auth/register/?error= \
                Возникла+ошибка+при+добавлении+пользователя.",
            status_code=303
        )
    
    await send_verification_email(email=data.email)

    return RedirectResponse("/auth/verify-email", status_code=303)


@router.post("/login/")
async def auth_user(data: SUserAuth = Depends()) -> RedirectResponse:
    """Аутентифицирует пользователя на платформе."""

    user = await UsersDAO.find_user(email=data.email)
    if not user or not verify_password(data.password, user.password):
        return RedirectResponse(
            url="/auth/login/?error=Неверная+почта+или+пароль.",
            status_code=303,
        )

    response = RedirectResponse(url="/main/", status_code=303)

    token = create_access_token(email=data.email)
    response.set_cookie(key="users_access_token", value=token, httponly=True)

    return response


@router.get("/logout/")
async def logout_user() -> RedirectResponse:
    """Разлогинивает пользователя с платформы."""

    response = RedirectResponse(url='/auth/login/', status_code=303)
    response.delete_cookie(key="users_access_token")

    return response


@router.post("/del/")
async def delete_user(request: Request) -> RedirectResponse:
    """Удаляет аккаунт пользователя с платформы."""

    token = request.cookies.get("users_access_token")
    if not token:
        return RedirectResponse(
            url="/auth/login/?error=Пользователь+не+авторизован.",
            status_code=303,
        )
    
    try:
        data = decode_access_token(token)
    except Exception as error:
        return RedirectResponse(
            url=f"/main/?error={error}", 
            status_code=303,
        )

    user = await UsersDAO.find_user(email=data.get("email"))
    if not user:
        return RedirectResponse(
            url="/auth/login/?error=Такой+пользователь+не+зарегистрирован.",
            status_code=303,
        )

    try:
        await UsersDAO.delete_user(email=data.get('email'))
    except SQLAlchemyError as error:
        return RedirectResponse(
            url="/main/?error=Возникла+ошибка+при+удалении+пользователя.",
            status_code=303,
        )

    response = RedirectResponse(
        url='/auth/login/?success=Удаление+прошло+успешно!', 
        status_code=303,
    )
    response.delete_cookie(key="users_access_token")

    return response
    

@router.post("/verify-email")
async def verify_email(token: str = Form(...)):
    """Переводит пользователя на его аккаунт после подтверждения почты."""

    try:
        data = decode_access_token(token)
    except Exception as error:
        return RedirectResponse(
            url=f"/main/?error={error}", 
            status_code=303,
        )

    response = RedirectResponse(
        url="/main/?success=Вы+успешно+зарегистрированы!", 
        status_code=303,
    )
    
    token = create_access_token(email=data["email"])
    response.set_cookie(key="users_access_token", value=token, httponly=True)

    return response