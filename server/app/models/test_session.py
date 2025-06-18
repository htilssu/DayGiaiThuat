from datetime import datetime

from app.database.database import Base, DateTime, Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class TestSession(Base):
    __tablename__ = "test_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), index=True)
    test_id: Mapped[int] = mapped_column(Integer, ForeignKey("tests.id"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, index=True)
