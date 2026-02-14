from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import EmailStr

from dao.dao_models import UsersDAO
from users.validation import SUserRegister, SUserAuth
from users.auth import get_password_hash, create_access_token
from users.auth import decode_access_token, send_verification_email
from users.auth import authenticate_user


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post("/register/")
async def register_user(data: SUserRegister = Depends()) -> dict:
    """Регистрирует пользователя на платформе."""

    found_user = await UsersDAO.find_one_or_none(email=data.email)
    if found_user:
        return RedirectResponse(
            "/auth/register/?error=Пользователь+с+таким+email+уже+существует.",
            status_code=303,
        )
    
    found_user = await UsersDAO.find_one_or_none(username=data.username)
    if found_user:
        return RedirectResponse(
            "/auth/register/?error=Пользователь+с+таким+именем+уже+существует!",
            status_code=303,
        )
    
    await UsersDAO.add(
        username=data.username,
        email=data.email,
        password=get_password_hash(data.password),
    )
    
    token_for_email = create_access_token({"email": data.email}, email=True)
    send_verification_email(email=data.email, token=token_for_email)

    return RedirectResponse("/auth/verify-email", status_code=303)


@router.post("/login/")
async def auth_user(
    email: EmailStr = Form(...),
    password: str = Form(...)
) -> dict:
    """ Функция для авторизации пользователя """

    user_data = SUserAuth(
        email=email,
        password=password
    )

    user = await authenticate_user(email=user_data.email, password=user_data.password)
    if user is None:
        return RedirectResponse(
            url="/auth/login/?error=Неверная+почта+или+пароль.",
            status_code=303
        )

    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    response = RedirectResponse(url="/main/", status_code=303)
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return response


@router.get("/logout/")
async def logout_user():
    """ Функция для разлогинивания пользователя """
    response = RedirectResponse(url='/auth/login/', status_code=303)
    response.delete_cookie(key="users_access_token")
    return response


@router.post("/del/")
async def dell_user(request: Request):
    """ Функция для удаления пользователя """

    token = request.cookies.get("users_access_token")
    if not token:
        return RedirectResponse(
            url="/auth/login/?error=Возникла+ошибка+при+удалении+аккаунта.",
            status_code=303
        )
    user_data = decode_access_token(token)

    user = await UsersDAO.find_one_or_none(email=user_data.get("email"))
    if user is None:
        return RedirectResponse(
            url="/auth/login/?error=Такой+пользователь+не+зарегистрирован.",
            status_code=303
        )

    check = await UsersDAO.delete(email=user_data.get('email'))
    if check:
        response = RedirectResponse(
            url='/auth/login/?success=Удаление+прошло+успешно!', 
            status_code=303
        )
    else:
        response = RedirectResponse(
            url='/auth/login/?error=Возникла+ошибка+при+удалении+аккаунта.', 
            status_code=303
        )
    response.delete_cookie(key="users_access_token")
    return response
    

@router.post("/verify-email")
async def verify_email(token: str = Form(...)):
    """ Функция для подтверждения через email """

    data = decode_access_token(token)
    user = await UsersDAO.find_one_or_none(email=data['email'])
    user_dict = {
        "username": user.username,
        "email": user.email,
        "password": user.password
    }

    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    response = RedirectResponse(
        url="/main/?success=Вы+успешно+зарегистрированы!", 
        status_code=303
    )
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return response