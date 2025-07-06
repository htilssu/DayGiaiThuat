from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database.database import Base


class DocumentProcessingJob(Base):
    __tablename__ = "document_processing_jobs"

    id = Column(String, primary_key=True, index=True)  # document_id
    job_id = Column(String, nullable=False, unique=True, index=True)  # Runpod job ID
    filename = Column(String, nullable=False)
    document_url = Column(String, nullable=False)
    status = Column(
        String, nullable=False, default="IN_QUEUE"
    )  # IN_QUEUE, IN_PROGRESS, COMPLETED, FAILED
    result = Column(Text, nullable=True)  # JSON result from Runpod
    course_id = Column(
        Integer, ForeignKey("courses.id"), nullable=True
    )  # Nếu thuộc về course
    error_message = Column(Text, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    # Relationships
    course = relationship("Course", back_populates="document_processing_jobs")
