from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import text
from datetime import datetime


class Base(AsyncAttrs, DeclarativeBase):
    """ Базовый класс структуры, расширенный до асинхронного """
    # Эта строка говорит о том, что для данного класса таблица не будет создана
    __abstract__ = True

class User(Base):
    """ Класс, который представляет структуру таблицы users """
    __tablename__ = "users"

    # Объявляем столбцы класса
    # Mapped позволяет создавать столбец определенного типа
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    register_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    # Этот атрибут опреляет можно ли изменять уже существующую таблицу. Если нет - то он создает новую
    extend_existing = True