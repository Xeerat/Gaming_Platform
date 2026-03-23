from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from typing import List

from datetime import datetime


class Base(AsyncAttrs, DeclarativeBase):
    """Базовая ORM-модель."""

    __abstract__ = True


class User(Base):
    """ORM-модель таблицы users."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str] = mapped_column()
    register_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
    extend_existing = True

    maps: Mapped[list["Map"]] = relationship(
        back_populates="owner", 
        cascade="all, delete-orphan",
        lazy="selectin" 
    )



class Map(Base):
    """ORM-модель таблицы maps"""

    __tablename__ = "maps"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    mapname: Mapped[str] = mapped_column()
    data: Mapped[List[List[int]]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
    owner: Mapped["User"] = relationship(back_populates="maps")
    __table_args__ = (
        UniqueConstraint("user_id", "mapname", name="uq_user_map_name"),
    )
    extend_existing = True