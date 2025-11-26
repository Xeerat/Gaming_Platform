from fastapi import APIRouter, HTTPException, status, Response

from app.dao.dao_models import UsersDAO
from app.users.validation import SUserRegister, SUserAuth
from app.users.auth import authenticate_user, create_access_token, get_password_hash


# Создаем объект, который будет содержать все маршруты
# Они все будут начинаться с /auth
router = APIRouter(prefix='/auth', tags=['Auth'])

#=========================================================
# Маршрут /auth/registrer/
#=========================================================

# post обозначает, что функция создает и изменяет данные на сервере
@router.post("/register/")
async def register_user(response: Response, user_data: SUserRegister) -> dict:
    """ Функция для регистрации пользователя """
    # Ищем пользователя по email
    found_user = await UsersDAO.find_one_or_none(email=user_data.email)
    # Если пользователь уже существует, то ошибка
    if found_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )
    
    # Ищем пользователя по никнейму
    found_user = await UsersDAO.find_one_or_none(username=user_data.username)
    if found_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь с таким именем уже существует'
        )
    
    # Превращаем объект SUserRegister в словарь
    user_dict = user_data.dict()
    # Хешируем пароль
    user_dict['password'] = get_password_hash(user_data.password)
    # Добавляем нового пользователя
    await UsersDAO.add(**user_dict)

    # Используем cookie, чтобы сохранить вход пользователя
    # Получаем пользователя
    user = await authenticate_user(email=user_data.email, password=user_data.password)
    if user is None:
        raise HTTPException(status_code=500, detail="Ошибка при авто-входе после регистрации")
    # Создаем ему токен
    access_token = create_access_token({"sub": str(user.id)})
    # Добавляем токен в cookie
    # Также запрещаем доступ к cookie через JavaScript ради безопасности
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'message': 'Вы успешно зарегистрированы!', 
            'access_token': access_token, 
            'refresh_token': None}


#=========================================================
# Маршрут /auth/login/
#=========================================================

@router.post("/login/")
async def auth_user(response: Response, user_data: SUserAuth):
    """ Функция для авторизации пользователя """
    # Ищем пользователя
    user = await authenticate_user(email=user_data.email, password=user_data.password)
    # Если пользователя нет, то ошибка
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')
    
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'access_token': access_token, 'refresh_token': None}


#=========================================================
# Маршрут /auth/logout/
#=========================================================

@router.post("/logout/")
async def logout_user(response: Response):
    """ Функция для разлогинивания пользователя """
    # Удаляем токен пользователя
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}

#=========================================================
# Маршрут /auth/del/
#=========================================================

# delete обозначает, что функция удаляет данные с сервера
@router.delete("/del/")
async def dell_user(response: Response, user_data: SUserAuth):
    """ Функция для удаления пользователя """
    # Ищем пользователя
    user = await authenticate_user(email=user_data.email, password=user_data.password)
    # Если пользователя нет, то ошибка
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Такого пользователя нет')

    # Удаляем пользователя и его токен
    check = await UsersDAO.delete(email=user_data.email)
    if check:
        response.delete_cookie(key="users_access_token")
        return {"message": f"Пользователь удален!"}
    else:
        return {"message": "Ошибка при удалении пользователя"}
    