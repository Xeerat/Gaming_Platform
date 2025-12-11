from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import text
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, ARRAY
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
    is_verified: Mapped[bool] = mapped_column(default=False, server_default=text('false'), nullable=False)
    register_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    # Говорим, что нужно менять существующую таблицу, а не создавать новую
    extend_existing = True


class Maps(Base):
    __tablename__ = "maps"
    
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))

    name = Column(String(50))
    matrix = Column(ARRAY(Integer, dimensions=2))  # здесь хранится 2D-массив

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
    
class Character(Base):
    __tablename__ = "char"
    
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))

    name = Column(String(50))
    matrix = Column(ARRAY(Integer, dimensions=2))  # здесь хранится 2D-массив

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"