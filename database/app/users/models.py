from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, str_uniq, int_pk, created_at
import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int_pk]
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str_uniq]
    password: Mapped[str]

    friends = relationship(
        "Friends",
        foreign_keys="Friends.user_id",
        back_populates="user"
    )

    register_at: Mapped[created_at]

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"