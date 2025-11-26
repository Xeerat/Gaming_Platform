from os import getenv 
from dotenv import load_dotenv

#=========================================================
# Создание URL для связи с базой данных
#=========================================================

# Загружаем переменные среды из файла .env
load_dotenv()

def get_database_url() -> str:
    """ Функция, которая формирует URL для взаимодействия с базой данных. """
    user = getenv("DB_USER")
    password = getenv("DB_PASSWORD")
    host = getenv("DB_HOST")
    port = getenv("DB_PORT")
    name = getenv("DB_NAME")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"

DB_URL = get_database_url()

#=========================================================
# Получение данных для генерации токена пользователя
#=========================================================

def get_auth_data():
    key = getenv("SECRET_KEY")
    algorithm = getenv("ALGORITHM")
    return {"secret_key": key, "algorithm": algorithm}