from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import Connection
from alembic import context
from alembic.config import Config
from app.database import DB_URL
from app.migration.models import Base, User, Temporary
import asyncio

from pathlib import Path
from os.path import join
# Получаем путь до папки с конфигом
path_to_ini = str(Path(__file__).parent.parent)


#=========================================================
# Настройка логирования 
#=========================================================

# Получаем config-файл
config = Config(join(path_to_ini, "alembic.ini"))
if config.config_file_name is not None:
    # Настраиваем логирование в соответствии с параметрами в config
    fileConfig(config.config_file_name)

#=========================================================
# Метаданные моделей
#=========================================================

# Данные моделей для изменения структуры таблиц
target_metadata = Base.metadata

#=========================================================
# Оффлайн режим
#=========================================================

def run_offline_migrations() -> None:
    """ 
    Функция для генерации SQL-скрипта без дальнейшего выполнения.
    Подключение к базе данных не происходит.
    """
    # Настройка alembic для работы с базой данных
    context.configure(
        # Базы данных разные, поэтому url здесь нужен для определения базы данных текущего проекта
        # Это не установка соединения с ней
        url=DB_URL,
        target_metadata=target_metadata,
        # Вставлять ли конкретные значения в sql-запрос или добавлять переменные?
        literal_binds=True
    )

    # Открытие транзакции для безопасной работы с базой данных
    with context.begin_transaction():
        # Выполнение всех миграций, которые не применены 
        context.run_migrations()

#=========================================================
# Онлайн режим
#=========================================================

def do_migrations(connection: Connection) -> None:
    """
    Фунция для генерации SQL-скрипта и применения его к базе данных через соединение
    
    Входные данные:
    connection: открытое соединение с базой данных
    """
    # Настройка alembic для работы с базой данных
    # Измения применяются к переданному соединению
    context.configure(connection=connection, target_metadata=target_metadata)

    # Применение миграций
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """ 
    Функция для асинхронного соединения с базой данных.
    После соединения применяет миграции.
    """
    # Создаем асинхронный движок для соединения с базой данных
    connectable = create_async_engine(DB_URL, poolclass=pool.NullPool)
    # Создаем соединение
    async with connectable.connect() as connection:
        # Применяем миграции
        await connection.run_sync(do_migrations)
    # Выключаем движок
    await connectable.dispose()


#=========================================================
# Выбор режима в зависимости от запуска alembic
#=========================================================

def run_migration():
    if context.is_offline_mode():
        run_offline_migrations()
    else:
        # Асинхронный запуск миграций
        asyncio.run(run_async_migrations())

run_migration()