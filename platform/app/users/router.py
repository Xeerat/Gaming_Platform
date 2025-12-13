from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from pydantic import EmailStr

from app.dao.dao_models import UsersDAO, TemporaryDAO
from app.users.validation import SUserRegister, SUserAuth
import app.users.auth as auth


# Создаем объект, который будет содержать все маршруты
# Они все будут начинаться с /auth
router = APIRouter(prefix='/auth', tags=['Auth'])

#=========================================================
# Маршрут /auth/registrer/
#=========================================================

# post обозначает, что функция создает и изменяет данные на сервере
@router.post("/register/")
async def register_user(
    email: EmailStr = Form(...),
    password: str = Form(...),
    username: str = Form(...),
    confirm_password: str = Form(...)
) -> dict:
    """ Функция для регистрации пользователя """
    # Проверяем типы данных
    user_data = SUserRegister(
        email=email,
        password=password,
        username=username,
        confirm_password=confirm_password
    )
    # Ищем пользователя по email
    found_user = await UsersDAO.find_one_or_none(email=user_data.email)
    # Если пользователь уже существует, то ошибка
    if found_user:
        return RedirectResponse(
            "/auth/register/?error=Пользователь+с+таким+email+уже+существует.",
            status_code=303
            )
    
    # Ищем пользователя по никнейму
    found_user = await UsersDAO.find_one_or_none(username=user_data.username)
    if found_user:
        return RedirectResponse(
            "/auth/register/?error=Пользователь+с+таким+именем+уже+существует!",
            status_code=303
        )
    
    # Проверяем совпадение паролей
    if user_data.password != user_data.confirm_password:
        return RedirectResponse(
            "/auth/register/?error=Пароли+не+совпадают!",
            status_code=303
        )
    
    # Превращаем объект SUserRegister в словарь
    user_dict = user_data.dict()
    # Удаляем лишний пароль перед добавлением в базу данных
    del user_dict["confirm_password"]
    # Хешируем пароль
    user_dict['password'] = auth.get_password_hash(user_data.password)
    # После добавления пользователя в базу
    user = await TemporaryDAO.add(**user_dict)

    # Генерация токена для подтверждения email
    email_token = auth.create_access_token(
        {"sub": str(user.id), "email": user.email}, email=True
    )
    
    # Отправка письма на почту пользователя
    auth.send_verification_email(user.email, email_token)

    # Переходим на страницу ожидания подтверждения
    return RedirectResponse("/auth/verify-email", status_code=303)

#=========================================================
# Маршрут /auth/login/
#=========================================================

@router.post("/login/")
async def auth_user(
    email: EmailStr = Form(...),
    password: str = Form(...)
) -> dict:
    """ Функция для авторизации пользователя """
    # Проверяем типы данных
    user_data = SUserAuth(
        email=email,
        password=password
    )
    # Ищем пользователя
    user = await auth.authenticate_user(email=user_data.email, password=user_data.password)

    # Если пользователя нет, то уведомление о некорректности пароля и логина
    if user is None:
        return RedirectResponse(
            url="/auth/login/?error=Неверная+почта+или+пароль.",
            status_code=303
        )

    # Создаем токен для пользователя
    access_token = auth.create_access_token({"sub": str(user.id), "email": user.email})
    # Перенаправляем пользователя на главную страницу
    response = RedirectResponse(url="/main/", status_code=303)
    # Добавляем токен в cookie
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return response

#=========================================================
# Маршрут /auth/logout/
#=========================================================

@router.get("/logout/")
async def logout_user():
    """ Функция для разлогинивания пользователя """
    # Перенаправляем пользователя на страницу авторизации
    response = RedirectResponse(url='/auth/login/', status_code=303)
    # Удаляем токен пользователя
    response.delete_cookie(key="users_access_token")
    return response

#=========================================================
# Маршрут /auth/del/
#=========================================================

@router.post("/del/")
async def dell_user(request: Request):
    """ Функция для удаления пользователя """
    # Получаем токен пользователя
    token = request.cookies.get("users_access_token")
    # Если токен закончился, то переход на страницу авторизации
    if not token:
        return RedirectResponse(
            url="/auth/login/?error=Возникла+ошибка+при+удалении+аккаунта.",
            status_code=303
        )
    # Расшифровываем токен
    user_data = auth.decode_access_token(token)

    # Ищем пользователя
    user = await UsersDAO.find_one_or_none(email=user_data.get("email"))
    # Если пользователя нет, то ошибка и переход на страницу авторизации
    if user is None:
        return RedirectResponse(
            url="/auth/login/?error=Такой+пользователь+не+зарегистрирован.",
            status_code=303
        )

    # Удаляем пользователя
    check = await UsersDAO.delete(email=user_data.get('email'))
    # Если получилось удалить пользователя
    if check:
        # Перенаправляем на страницу авторизации с успехом
        response = RedirectResponse(
            url='/auth/login/?success=Удаление+прошло+успешно!', 
            status_code=303
        )
    else:
        # Перенаправляем на страницу авторизации с ошибкой
        response = RedirectResponse(
            url='/auth/login/?error=Возникла+ошибка+при+удалении+аккаунта.', 
            status_code=303
        )
    # Удаляем куки
    response.delete_cookie(key="users_access_token")
    return response
    
#=========================================================
# Маршрут /auth/verify-email
#=========================================================

@router.post("/verify-email")
async def verify_email(token: str = Form(...)):
    """ Функция для подтверждения через email """
    # Расшифровываем токен
    data = auth.decode_access_token(token)
    # Находим данные пользователя во временной базе данных
    user = await TemporaryDAO.find_one_or_none(email=data['email'])
    # Добавляем нового пользователя в основную базу данных
    user_dict = {
        "username": user.username,
        "email": user.email,
        "password": user.password
    }
    user = await UsersDAO.add(**user_dict)

    # Генерация токена для куки
    access_token = auth.create_access_token({"sub": str(user.id), "email": user.email})
    # Переход на основную страницу
    response = RedirectResponse(
        url="/main/?success=Вы+успешно+зарегистрированы!", 
        status_code=303
    )
    # Задаем куки
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return response