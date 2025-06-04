from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.database import Base
from server.app.models.user import User


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id : Mapped[int] = mapped_column(primary_key=True, index=True)
    name : Mapped[str] = mapped_column(index=True)
    created_at : Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at : Mapped[datetime] = mapped_column(default=datetime.now)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"))
    path : Mapped[dict] = mapped_column(JSON, nullable=True)    
    
    user : Mapped["User"] = relationship(back_populates="learning_paths")

