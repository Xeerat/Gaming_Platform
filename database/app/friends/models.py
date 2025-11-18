from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, str_uniq, int_pk, created_at
import datetime

class Friend_Request(Base):
    __tablename__ = "friend_requests"

    id: Mapped[int_pk]

    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    send_at: Mapped[created_at]

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
    


class Friends(Base):
    __tablename__ = "friends"
    
    id: Mapped[int_pk]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    friend_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    at: Mapped[created_at]

    user = relationship("User", foreign_keys=[user_id], back_populates="friends")
    friend = relationship("User", foreign_keys=[friend_id])

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"