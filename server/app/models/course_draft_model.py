from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.database.database import Base


class CourseDraft(Base):
    """
    Model để lưu trữ tạm thời nội dung khóa học do agent tạo ra
    trước khi admin approve
    """

    __tablename__ = "course_drafts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    agent_content: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # JSON string chứa topics, lessons
    status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # pending, approved, rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship
    course = relationship("Course", back_populates="draft")


class CourseReviewChat(Base):
    """
    Model để lưu trữ chat giữa admin và agent trong quá trình review
    """

    __tablename__ = "course_review_chats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_agent: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # True nếu là tin nhắn từ agent
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    course = relationship("Course")
    user = relationship("User")
