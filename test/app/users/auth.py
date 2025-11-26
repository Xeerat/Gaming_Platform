from passlib.context import CryptContext
from pydantic import EmailStr
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.dao.dao_models import UsersDAO
from app.database import get_auth_data

#=========================================================
# Создание токена
#=========================================================

# Создаем объект для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict) -> str:
    """ Функция для создания токенов для пользователей """
    to_encode = data.copy()
    # Ставим время действительности токена
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})

    # Получаем особые данные
    auth_data = get_auth_data()
    # Создаем токен для пользователя
    encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
    return encode_jwt

#=========================================================
# Хеширование пароля
#=========================================================

def get_password_hash(password: str) -> str:
    """ Функция для хеширования паролей пользователей """
    return pwd_context.hash(password)

#=========================================================
# Аутентификация
#=========================================================

async def authenticate_user(email: EmailStr, password: str):
    """ Функция для проверки существования пользователя """
    user = await UsersDAO.find_one_or_none(email=email)
    if not user or pwd_context.verify(password, user.password) is False:
        return None
    return user