import pytest
from passlib.context import CryptContext
from jose import jwt 

from datetime import datetime, timezone, timedelta
from os import getenv
from dotenv import load_dotenv
from typing import Literal
from unittest.mock import AsyncMock, patch

import app.users.auth as auth
from app.database import EMAIL_DATA


load_dotenv()


@pytest.mark.parametrize("for_email, type_time, number", [
    (True, "m", 15),
    (False, "d", 5),
])
def test_create_access_token_correct_time(
    for_email: bool, 
    type_time: Literal["m", "d"], 
    number: int,
):
    """
    Проверка корректности времени действия токена.
    Проверяет край правильного времени.

    Args:
        for_email: определяет время действия токена.
        type_time: тип времени в зависимости от флага for_email.
        number: число единиц времени, которое нужно проверить.
    """
    
    # Arrange
    email = "hello@mail.ru"

    # Act
    token = auth.create_access_token(email=email, for_email=for_email, user_id=0)

    # Assert
    if type_time == "m":
        time = datetime.now(timezone.utc) + timedelta(minutes=number)
    elif type_time == "d":
        time = datetime.now(timezone.utc) + timedelta(days=number)
    time = int(time.timestamp())

    data = jwt.decode(
        token,
        getenv("SECRET_KEY"), 
        getenv("ALGORITHM"),
    )
    expire = data.get("exp")

    # + одна секунда для того, чтобы тест стал точнее
    assert expire <= time + 1


@pytest.mark.parametrize("for_email, type_time, number", [
    (True, "m", 14),
    (False, "d", 4),
])
def test_create_access_token_incorrect_time(
    for_email: bool, 
    type_time: Literal["m", "d"], 
    number: int,
):
    """
    Проверка корректности времени действия токена.
    Проверяет край неправильного времени.

    Args:
        for_email: определяет время действия токена.
        type_time: тип времени в зависимости от флага for_email.
        number: число единиц времени, которое нужно проверить.
    """
    
    # Arrange
    email = "hello@mail.ru"

    # Act
    token = auth.create_access_token(email=email, for_email=for_email, user_id=0)

    # Assert
    if type_time == "m":
        time = datetime.now(timezone.utc) + timedelta(minutes=number)
    elif type_time == "d":
        time = datetime.now(timezone.utc) + timedelta(days=number)
    time = int(time.timestamp())

    data = jwt.decode(
        token,
        getenv("SECRET_KEY"), 
        getenv("ALGORITHM"),
    )
    expire = data.get("exp")
    
    # - одна секунда для того, чтобы тест стал точнее
    assert expire > time - 1


@pytest.mark.parametrize("user_id", [
    (1),
    (2),
    (3),
])
def test_decode_access_token(user_id: int):
    """
    Проверка корректности расшифровки токена.

    Args:
        email: почта, которая будет зашифрована в токен.
    """

    # Arrange
    token = jwt.encode(
        {"user_id": user_id},
        getenv("SECRET_KEY"), 
        getenv("ALGORITHM"),
    )
    
    # Act
    answer_id = auth.decode_access_token(token=token)

    # Assert
    assert answer_id == user_id
    
    
@pytest.mark.parametrize("password", [
    ("abcdsssssss"),
    ("hello"),
    ("hhhhhhh"),
])
def test_get_password_hash(password: str):
    """
    Проверка корретности хэширования пароля.
    
    Args:
        password: пароль, который будет хэширован.
    """
    # Arrange 
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Act
    password_hash = auth.get_password_hash(password)

    # Assert
    assert pwd_context.verify(password, password_hash) is True


@pytest.mark.parametrize("password", [
    ("hello"),
    ("dfsdfsdgsgrggdf332r"),
    ("djsfisfj!@#32342342"),
])
def test_verify_password_true(password: str):
    """
    Проверка корректности функции аутентификации.
    Проверки, когда пароли должны совпасть.

    Args:
        password: пароль, который будет хэширован.
    """

    # Arrange
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_hash = pwd_context.hash(password)

    # Act
    result = auth.verify_password(password, password_hash)

    # Assert
    assert result is True


@pytest.mark.parametrize("password, fake_password", [
    ("hello", "djdjdjdjd"),
    ("dfsdfsdgsgrggdf332r", "dqwe122"),
    ("djsfisfj!@#32342342", "d312kggg"),
])
def test_verify_password_false(password: str, fake_password: str):
    """
    Проверка корректности функции аутентификации.
    Проверки, когда пароли не должны совпасть.

    Args:
        password: пароль, который будет хэширован.
    """

    # Arrange
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_hash = pwd_context.hash(password)

    # Act 
    result = auth.verify_password(fake_password, password_hash)

    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_send_verification_email():
    """Проверка корректности функции отправки письма на почту."""

    # Arrange
    email = "hello@mail.ru"
    title = "test"
    text = "Hello"
    url = "/verify"
    fake_token = "abc123"
    correct_link = f"http://localhost:8000{url}?token={fake_token}"

    with patch("app.users.auth.create_access_token", return_value=fake_token):
        with patch("app.users.auth.SMTP") as mock_smtp:
            mock_server = AsyncMock()
            mock_smtp.return_value.__aenter__.return_value = mock_server

            # Act
            await auth.send_verification_email(
                email=email,
                title=title,
                text=text,
                url_for_token=url,
            )

            # Assert
            mock_server.login.assert_awaited_once()
            mock_server.send_message.assert_awaited_once()

            sent_message = mock_server.send_message.call_args[0][0]
            assert title in sent_message["Subject"]
            assert email in sent_message["To"]
            assert sent_message["From"] == EMAIL_DATA["platform_email"]

            payload = sent_message.get_payload()
            assert text in payload
            assert correct_link in payload
