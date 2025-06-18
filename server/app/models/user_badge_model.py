from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database.database import Base


class UserBadge(Base):
    __tablename__ = "user_badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    badge_id: Mapped[int] = mapped_column(Integer, ForeignKey("badges.id"))
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
