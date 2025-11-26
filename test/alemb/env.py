from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import Connection
from alembic import context
from alembic.config import Config
import asyncio
from app.database import DB_URL

from pathlib import Path
from os.path import join

path_to_ini = str(Path(__file__).parent.parent)

from app.migration.models import Base, User


#=========================================================
# Настройка логирования 
#=========================================================

# Берем текущий config - файл "alembic.ini"
config = Config(join(path_to_ini, "alembic.ini"))
# Проверяем есть ли он
if config.config_file_name is not None:
    # Настраиваем логирование в соответствии с параметрами в config
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

#=========================================================
# Оффлайн режим
#=========================================================

def run_migrations_offline() -> None:
    """ 
    Функция для генерации SQL-скрипта без дальнейшего выполнения.
    Подключение к базе данных не происходит.
    """
    # Настройка alembic для работы с базой
    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        # Вставлять ли конкретные значения в sql-запрос или добавлять переменные?
        literal_binds=True,
        # Вид переменных в sql-запросе. В сочетании с literal_binds=True не играет роли
        dialect_opts={"paramstyle": "named"},
    )

    # Создается контекст транзакции для миграции. Это как бы оболочка для миграции
    # Это значит, что все изменения, которые будут применяться, оборачиваются в эту транзакцию
    # Если что-то пойдет не так, то транзакция откатится и база данных не пострадает
    # После этого блока изменения либо применяются, либо откатываются с ошибкой
    with context.begin_transaction():
        # Функция выполняет все миграции, которые не применены 
        context.run_migrations()

#=========================================================
# Онлайн режим
#=========================================================


def do_run_migrations(connection: Connection) -> None:

    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """ 
    Функция для генерации и дальнейшего выполнения SQL-скрипта.
    Происходит подключение к базе данных.
    """
    # Создается объект SQLAlchemy Engine 
    # poolclass=pool.NullPool делает так, чтобы каждый раз создавалось новое соединение, а старое не сохранялось
    connectable = create_async_engine(DB_URL, poolclass=pool.NullPool)
    # Создается соединение
    async with connectable.connect() as connection:
        # Настраиваем alembic для работы с базой
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


#=========================================================
# Выбор режима в зависимости от запуска alembic
#=========================================================

def run_migration():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        print("TABLES FOUND:", target_metadata.tables.keys())
        run_migrations_online()

run_migration() 