from typing import List, TYPE_CHECKING

from app.database.database import Base
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.reply_model import Reply
    from app.models.user_model import User


class Discussion(Base):
    __tablename__ = "discussions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Foreign key to user who created the discussion
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="discussions")
    replies: Mapped[List["Reply"]] = relationship(
        "Reply", back_populates="discussion", cascade="all, delete-orphan"
    ) 