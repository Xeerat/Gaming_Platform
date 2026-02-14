from os import getenv 
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool


load_dotenv()


def get_database_url() -> str:
    """
    Формирует URL для асинхронного соединения с базой данных.
     
    Returns:
        Строка-url для асинхронного соединения с базой данных.
    """

    user = getenv("DB_USER")
    password = getenv("DB_PASSWORD")
    host = getenv("DB_HOST")
    port = getenv("DB_PORT")
    name = getenv("DB_NAME")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"


DB_URL = get_database_url()
async_engine = create_async_engine(DB_URL, poolclass=pool.NullPool)


def get_token_data() -> dict:
    """
    Возвращает особые данные для генерации токена.
    
    Returns:
        Словарь содержащий особые данные для генерации токена.
    """

    return {
        "secret_key": getenv("SECRET_KEY"),
        "algorithm": getenv("ALGORITHM")
    }


def get_email_data() -> dict:
    """
    Возвращает особые данные для email верификации.
    
    Returns:
        Словарь содержащий особые данные для email верификации.
    """

    return {
        "email_user": getenv("EMAIL_SECRET"),
        "email_password": getenv("EMAIL_SECRET_PASS"),
        "smtp_server": getenv("SMTP_SERVER"),
        "smtp_port": getenv("SMTP_PORT")
    }