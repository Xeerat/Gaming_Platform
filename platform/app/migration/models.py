from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import text
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, ARRAY

#=========================================================
# Базовый структурная модель
#=========================================================

class Base(AsyncAttrs, DeclarativeBase):
    """ Базовый класс структуры, расширенный до асинхронного """
    # Не создаем для этой модели таблицу
    __abstract__ = True

#=========================================================
# Класс для работы со структорой таблицы users
#=========================================================

class User(Base):
    """ Класс, который представляет структуру таблицы users """
    __tablename__ = "users"

    # Создаем столбцы для таблицы
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    register_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    # Говорим, что нужно менять существующую таблицу, а не создавать новую
    extend_existing = True

#=========================================================
# Класс для работы со структорой таблицы temporary
#=========================================================

class Temporary(Base):
    """ Класс, который представляет структуру таблицы temporary """
    __tablename__ = "temporary"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    extend_existing = True


#=========================================================
# Класс для работы со структорой таблицы maps
#=========================================================

class Maps(Base):
    """ Класс, который представляет структуру таблицы maps """
    __tablename__ = "maps"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    name = Column(String(50))
    matrix = Column(ARRAY(Integer, dimensions=2))  # здесь хранится 2D-массив
    extend_existing = True

#=========================================================
# Класс для работы со структорой таблицы characters
#=========================================================
    
class Character(Base):
    """ Класс, который представляет структуру таблицы characters """
    __tablename__ = "characters"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    name = Column(String(50))
    matrix = Column(ARRAY(Integer, dimensions=2))  # здесь хранится 2D-массив
    extend_existing = True