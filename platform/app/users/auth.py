from passlib.context import CryptContext
from pydantic import EmailStr
from datetime import datetime, timedelta, timezone
from jose import jwt

from dao.dao_models import UsersDAO
from database import get_token_data, get_email_data

from email.mime.text import MIMEText
import smtplib

#=========================================================
# Шифрование токена
#=========================================================

def create_access_token(data: dict, email: bool = False) -> str:
    """ Функция для создания токенов для пользователей """
    to_encode = data.copy()
    # Если нужен токен для подтверждения email
    if email:
        # Таймер на 15 минут
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    else:
        # Таймер на 14 дней для обычных токенов
        expire = datetime.now(timezone.utc) + timedelta(days=14)
    to_encode.update({"exp": expire})

    # Получаем особые данные
    auth_data = get_token_data()
    try:
        # Создаем токен для пользователя
        encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
        return encode_jwt
    except Exception as e:
        raise ValueError(f"Не удалось создать токен: {e}")

#=========================================================
# Расшифровка токена
#=========================================================

def decode_access_token(token: str) -> dict:
    """ Функция для расшифровки токена """
    # Получаем особые данные
    auth_data = get_token_data()
    # Расшифровываем токен
    try:
        user_data = jwt.decode(token, auth_data['secret_key'], auth_data['algorithm'])
    except jwt.ExpiredSignatureError:
        raise ValueError("Истек срок годности токена")
    except jwt.InvalidTokenError:
        raise ValueError("Некорректный токен")
    return user_data

#=========================================================
# Хеширование пароля
#=========================================================

# Создаем объект для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

#=========================================================
# Отправка письма с подтверждением на email
#=========================================================

def send_verification_email(email: EmailStr, token: str):
    """ Функция для генерации и отправки сообщения с подтверждением на email """
    # Получаем особые данные для верификации email
    auth_data = get_email_data()
    # Создаем ссылку для подтверждения email
    verification_link = f"http://localhost:8000/auth/verify-email?token={token}"
    
    # Создаем сообщение 
    msg = MIMEText(f"Подтвердите вашу почту: {verification_link}")
    msg["Subject"] = "Подтверждение почты"
    msg["From"] = auth_data["email_user"] 
    msg["To"] = email

    # Открываем безопасное соединение с google сервером почты
    with smtplib.SMTP_SSL(auth_data["smtp_server"], auth_data["smtp_port"]) as server:
        # Авторизуемся на почте
        server.login(auth_data["email_user"], auth_data["email_password"])
        # Отправляем созданное сообщение 
        server.send_message(msg)
