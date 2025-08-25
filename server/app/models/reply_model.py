from typing import TYPE_CHECKING

from app.database.database import Base
from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.discussion_model import Discussion
    from app.models.user_model import User


class Reply(Base):
    __tablename__ = "replies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Foreign key to discussion this reply belongs to
    discussion_id: Mapped[int] = mapped_column(
        ForeignKey("discussions.id"), nullable=False, index=True
    )

    # Foreign key to user who created the reply
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    # Relationships
    discussion: Mapped["Discussion"] = relationship(
        "Discussion", back_populates="replies"
    )
    user: Mapped["User"] = relationship("User", back_populates="replies")
