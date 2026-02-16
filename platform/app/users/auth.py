from passlib.context import CryptContext
from pydantic import EmailStr
from jose import jwt
from email.mime.text import MIMEText

from datetime import datetime, timedelta, timezone
from aiosmtplib import SMTP

from database import TOKEN_DATA, EMAIL_DATA


def create_access_token(email: EmailStr, for_email: bool = False) -> str:
    """
    Создает токен для пользователя.

    Args:
        email: электронная почта пользователя.
        for_email: флаг для определения времени действия токена.
                Если True, то время действия 15 минут.
                Если False, то время действия 5 дней.
    
    Returns:
        Токен для пользователя.
    """

    if for_email:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=5)

    data = {"exp": expire, "email": email}
    token = jwt.encode(
        data, 
        key=TOKEN_DATA['secret_key'],
        algorithm=TOKEN_DATA['algorithm'],
    )

    return token


def decode_access_token(token: str) -> dict:
    """
    Расшифровывает токен пользователя.
    
    Args:
        token: токен пользователя.
    
    Returns:
        Словарь с почтой пользователя. Ключ "email".
    
    Raises:
        ExpiredSignatureError - если у токена истек срок годности.
        JWTError - если с токеном какая то проблема.
    """

    return jwt.decode(
        token,
        TOKEN_DATA['secret_key'], 
        TOKEN_DATA['algorithm'],
    )


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Хэширует пароль пользователя.

    Args:
        password: пароль пользователя.
    
    Returns:
        Хэш пароля.
    """

    return pwd_context.hash(password)


def verify_password(password: str, hash: str) -> bool:
    """
    Сравнивает введённый пользователем пароль с настоящим.

    Args:
        password: пароль введённый пользователем.
        hash: хэш настоящего пароля пользователя.
    
    Returns:
        True - если пароль совпал, False иначе.
    """

    return pwd_context.verify(password, hash)


async def send_verification_email(email: EmailStr) -> None:
    """
    Отправляет письмо верификации на почту пользователя.

    Args:
        email: электронная почта пользователя.
    """

    token = create_access_token(email=email, for_email=True)
    link = f"http://localhost:8000/auth/verify-email?token={token}"

    msg = MIMEText(f"Подтвердите вашу почту: {link}")
    msg["Subject"] = "Подтверждение почты"
    msg["From"] = EMAIL_DATA["platform_email"] 
    msg["To"] = email

    async with SMTP(
        hostname=EMAIL_DATA["smtp_server"],
        port=EMAIL_DATA["smtp_port"],
        use_tls=True
    ) as server:
        await server.login(
            EMAIL_DATA["platform_email"], 
            EMAIL_DATA["platform_password"],
        )
        await server.send_message(msg)
