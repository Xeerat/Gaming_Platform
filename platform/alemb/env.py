from logging.config import fileConfig
import asyncio

from sqlalchemy.engine import Connection
from alembic import context

from app.database import DB_URL, async_engine
from app.migration.models import Base


# Настройка логирования
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_offline_migrations() -> None:
    """Выполняет оффлайн миграцию базы данных."""

    context.configure(
        url=DB_URL,
        target_metadata=target_metadata,
        literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_online_migrations(connection: Connection) -> None:
    """
    Выполняет онлайн миграцию базы данных.

    Args:
        connection: объект соединения с базой данных.
    """

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Выполняет онлайн миграцию в асинхронном режиме."""

    async with async_engine.connect() as connection:
        await connection.run_sync(run_online_migrations)

    await async_engine.dispose()


if context.is_offline_mode():
    run_offline_migrations()
else:
    # Проверка запущенного event loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None 
    
    if loop and loop.is_running():
        asyncio.create_task(run_async_migrations())
    else:
        asyncio.run(run_async_migrations())
