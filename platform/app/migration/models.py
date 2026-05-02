from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import JSON, ForeignKey, text, UniqueConstraint, String

from datetime import datetime


class Base(AsyncAttrs, DeclarativeBase):
    """Базовая ORM-модель."""

    __abstract__ = True


class User(Base):
    """ORM-модель таблицы users."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    register_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
    novels: Mapped[list["Novell"]] = relationship(
        "Novell",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    extend_existing = True
    


class Novell(Base):
    __tablename__ = "novels"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(nullable=False, default="Без названия", unique=True)
    preview: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=text("TIMEZONE('utc', now())")
    )
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    user: Mapped["User"] = relationship(back_populates="novels")