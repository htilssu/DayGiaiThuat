from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database.database import Base


class DocumentProcessingJob(Base):
    __tablename__ = "document_processing_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)  # document_id
    job_id: Mapped[str] = mapped_column(
        String, nullable=False, unique=True, index=True
    )
    filename: Mapped[str] = mapped_column(String, nullable=False)
    document_url: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="IN_QUEUE"
    )  # IN_QUEUE, IN_PROGRESS, COMPLETED, FAILED
    result: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    course_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("courses.id"), nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    course = relationship("Course", back_populates="document_processing_jobs")
