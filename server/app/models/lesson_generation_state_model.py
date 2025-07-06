from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.database import Base

class LessonGenerationState(Base):
    __tablename__ = "lesson_generation_states"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    status = Column(String, nullable=False, default="in_progress")  # e.g., in_progress, completed, failed
    request_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    topic = relationship("Topic")
    lesson = relationship("Lesson")
