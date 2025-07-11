from app.database.database import Base
from app.models.topic_model import Topic
from app.models.user_model import User
from sqlalchemy import Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserTopic(Base):

    __tablename__ = "user_topics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"))
    progress: Mapped[int] = mapped_column(Integer, default=0)
    completed_lessons: Mapped[int] = mapped_column(Integer, default=0)
    current_lesson_id: Mapped[int] = mapped_column(Integer, ForeignKey("lessons.id"))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    topic: Mapped[Topic] = relationship("Topic", back_populates="user_topics")
    user: Mapped["User"] = relationship("User", back_populates="user_topics")
