from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from os import getenv
from dotenv import load_dotenv

import app.database as database


load_dotenv()


def test_get_database_url():
    """Проверка функции, возвращающей url для связи с БД."""

    # Arrange
    user = getenv("DB_USER")
    password = getenv("DB_PASSWORD")
    host = getenv("DB_HOST")
    port = getenv("DB_PORT")
    name = getenv("DB_NAME")
    right_link = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"

    # Act
    link = database.get_database_url()

    # Assert
    assert right_link == link


def test_get_token_data():
    """Проверка функции, возвращающей данные для генерации токена."""

    # Arrange
    secret_key = getenv("SECRET_KEY")
    algorithm = getenv("ALGORITHM")

    # Act
    data = database.get_token_data()

    # Assert
    assert data["secret_key"] == secret_key
    assert data["algorithm"] == algorithm


def test_get_email_data():
    """Проверка функции, возвращающей данные для email верификации."""

    # Arrange
    platform_email = getenv("PLATFORM_EMAIL")
    platform_password = getenv("PLATFORM_PASSWORD")
    smtp_server = getenv("SMTP_SERVER")
    smtp_port = getenv("SMTP_PORT")

    # Act
    data = database.get_email_data()

    # Assert
    assert data["platform_email"] == platform_email
    assert data["platform_password"] == platform_password
    assert data["smtp_server"] == smtp_server
    assert data["smtp_port"] == smtp_port


def test_database_global_variable():
    """Проверка необходимых глобальных переменных в database.py."""

    assert "None" not in database.DB_URL

    assert database.TOKEN_DATA["secret_key"] != None
    assert database.TOKEN_DATA["algorithm"] != None

    assert database.EMAIL_DATA["platform_email"] != None
    assert database.EMAIL_DATA["platform_password"] != None
    assert database.EMAIL_DATA["smtp_server"] != None
    assert database.EMAIL_DATA["smtp_port"] != None

    assert isinstance(database.async_engine, AsyncEngine) == True
    assert isinstance(database.async_session_maker, async_sessionmaker) == True