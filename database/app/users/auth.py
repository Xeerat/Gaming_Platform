import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from passlib.context import CryptContext
from pydantic import EmailStr
from app.users.dao import UsersDAO
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import get_auth_data


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# чтобы пользователь после захода оставался в аккаунте используем токены
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
    return encode_jwt

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# по факту проекрка на существование пользователя и на то что верно введен пароль
async def authenticate_user(email: EmailStr, password: str):
    user = await UsersDAO.find_one_or_none(email=email)
    if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
        return None
    return user