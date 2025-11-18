
from fastapi import APIRouter, HTTPException, status, Response, Depends
from app.users.auth import get_password_hash
from app.users.dao import UsersDAO
from app.users.schemas import SUserRegister, SUserAuth
from app.users.auth import authenticate_user, create_access_token
from app.users.models import User
from app.users.dependencies import get_current_user



router = APIRouter(prefix='/auth', tags=['Auth'])

# тут идет регистрация
@router.post("/register/")
async def register_user(response: Response, user_data: SUserRegister) -> dict:
    # получает юзера по имейлу
    user = await UsersDAO.find_one_or_none(email=user_data.email)
    # если он есть выдает HTTPException (в зависимости от этого выводить то что пользователь с таким имейлом уже есть)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )
    user2 = await UsersDAO.find_one_or_none(username=user_data.username)
    # если он есть выдает HTTPException (в зависимости от этого выводить то что пользователь с таким именем уже есть)
    # важно то что у нас должны быть уникальные username
    if user2:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь с таким именем уже существует'
        )
    # если пользователя нет в БД, то добавляем его, при этом хэшируем пароль
    user_dict = user_data.dict()
    user_dict['password'] = get_password_hash(user_data.password)
    await UsersDAO.add(**user_dict)
    # чтобы пользователь оставался в аккаунте используем куки
    check = await authenticate_user(email=user_data.email, password=user_data.password)
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'message': 'Вы успешно зарегистрированы!', 
            'access_token': access_token, 
            'refresh_token': None}


@router.post("/login/")
async def auth_user(response: Response, user_data: SUserAuth):
    # для начала проверяем корректность почты и пароля
    check = await authenticate_user(email=user_data.email, password=user_data.password)
    # если неверно выводит следующее
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')
    # чтобы пользователь оставался в аккаунте используем куки
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'access_token': access_token, 'refresh_token': None}

@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)):
    # не уверен как но это скорее всего как то понадобится
    return user_data

@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}

@router.delete("/dell/")
async def dell_user(response: Response, user_data: User = Depends(get_current_user)):
    check = await UsersDAO.delete(email=user_data.email)
    if check:
        
        response.delete_cookie(key="users_access_token")
        return {"message": f"Пользователь удален!"}
    else:
        return {"message": "Ошибка при удалении пользователя"}
    