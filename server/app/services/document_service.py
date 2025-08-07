import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import select

from app.database.database import get_independent_db_session
from app.models.document_processing_job_model import DocumentProcessingJob

logger = logging.getLogger(__name__)


class DocumentStatus:
    def __init__(self, document_id: str, status: str, progress: int = 0):
        self.document_id = document_id
        self.status = status
        self.progress = progress


class DocumentService:
    def __init__(self):
        self.embeddings = None  # Will be initialized when needed
        self.vector_store = None  # Will be initialized when needed

    async def create_document_processing_job(
        self,
        document_id: str,
        job_id: str,
        filename: str,
        document_url: str,
        course_id: Optional[int] = None,
    ) -> DocumentProcessingJob:
        """
        Tạo job xử lý tài liệu mới
        """
        async with get_independent_db_session() as db:
            job = DocumentProcessingJob(
                job_id=job_id,
                document_id=document_id,
                filename=filename,
                document_url=document_url,
                course_id=course_id,
                status="PENDING",
            )
            db.add(job)
            await db.commit()
            await db.refresh(job)
            return job

    async def update_job_status(
        self,
        job_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> Optional[DocumentProcessingJob]:
        """
        Cập nhật trạng thái job từ webhook
        """
        async with get_independent_db_session() as db:
            try:
                result_query = await db.execute(
                    select(DocumentProcessingJob).where(
                        DocumentProcessingJob.job_id == job_id
                    )
                )
                job = result_query.scalar_one_or_none()

                if not job:
                    return None

                job.status = status
                if result:
                    job.result = json.dumps(result)
                if error_message:
                    job.error_message = error_message
                if status == "COMPLETED":
                    job.processed_at = datetime.utcnow()

                await db.commit()
                await db.refresh(job)
                return job
            except Exception as e:
                await db.rollback()
                raise Exception(f"Failed to update job status: {str(e)}")

    async def process_completed_document(
        self, job_id: str, result: Dict[str, Any]
    ) -> None:
        """
        Xử lý tài liệu đã hoàn thành: semantic chunking và lưu vào RAG
        """
        async with get_independent_db_session() as db:
            try:
                result_query = await db.execute(
                    select(DocumentProcessingJob).where(
                        DocumentProcessingJob.job_id == job_id
                    )
                )
                job = result_query.scalar_one_or_none()

                if not job:
                    raise Exception(f"Job {job_id} not found")

                # Xử lý kết quả từ Docling
                await self._process_docling_result(job, result)

                # Nếu thuộc về course, gọi agent tạo topic và lesson
                if job.course_id:
                    await self._trigger_course_content_generation(job.course_id)

                logger.info(f"Document processing completed for job {job_id}")

            except Exception as e:
                logger.error(f"Error processing completed document {job_id}: {str(e)}")
                raise e

    async def _process_docling_result(
        self, job: DocumentProcessingJob, result: Dict[str, Any]
    ) -> None:
        """
        Xử lý kết quả từ Docling và lưu vào vector database
        """
        # TODO: Implement document processing logic
        logger.info(f"Processing docling result for job {job.job_id}")

    async def _trigger_course_content_generation(self, course_id: int) -> None:
        """
        Gọi agent tạo topic và lesson cho course
        """
        # TODO: Implement course content generation
        logger.info(f"Triggering course content generation for course {course_id}")


def get_document_service() -> DocumentService:
    """
    Dependency để inject DocumentService
    """
    return DocumentService()
