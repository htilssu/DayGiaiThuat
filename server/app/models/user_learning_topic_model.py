from sqlalchemy import Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base


class UserLearningTopic(Base):
    __tablename__ = "user_learning_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"))
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
