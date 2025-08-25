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
                id=document_id,  # Use 'id' instead of 'document_id'
                job_id=job_id,
                filename=filename,
                document_url=document_url,
                course_id=course_id,
                status="IN_QUEUE",  # Use the default status from the model
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

    async def call_external_document_processing_api(self, document_url: str) -> str:
        """
        Gọi RunPod API để xử lý tài liệu bằng Docling serverless function
        
        Args:
            document_url (str): URL của tài liệu cần xử lý
            
        Returns:
            str: Job ID từ RunPod API
            
        Raises:
            Exception: Nếu có lỗi khi gọi API
        """
        try:
            from app.core.config import settings
            
            # Kiểm tra xem có RunPod API key không
            if not settings.RUNPOD_API_KEY:
                raise Exception("RunPod API key not configured")
            
            import httpx
            import uuid
            
            # Tạo job ID duy nhất
            job_id = str(uuid.uuid4())
            
            # RunPod API endpoint
            if settings.RUNPOD_ENDPOINT_ID:
                runpod_endpoint = f"https://api.runpod.io/v2/{settings.RUNPOD_ENDPOINT_ID}/run"
                logger.info(f"Using RunPod endpoint ID: {settings.RUNPOD_ENDPOINT_ID}")
            elif settings.DOCUMENT_PROCESSING_ENDPOINT:
                runpod_endpoint = settings.DOCUMENT_PROCESSING_ENDPOINT
                logger.info(f"Using custom document processing endpoint: {settings.DOCUMENT_PROCESSING_ENDPOINT}")
            else:
                raise Exception("RunPod endpoint ID or document processing endpoint not configured")
            
            # Chuẩn bị payload cho RunPod API
            payload = {
                "input": {
                    "url": document_url,
                    "webhook_url": f"{settings.BASE_URL}/admin/document/webhook",
                    "job_id": job_id
                }
            }
            
            # Headers cho RunPod API
            headers = {
                "Authorization": f"Bearer {settings.RUNPOD_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Gọi RunPod API
            logger.info(f"Calling RunPod API at: {runpod_endpoint}")
            logger.info(f"Payload: {payload}")
            
            async with httpx.AsyncClient(timeout=settings.DOCUMENT_PROCESSING_TIMEOUT) as client:
                response = await client.post(
                    runpod_endpoint,
                    json=payload,
                    headers=headers
                )
                
                logger.info(f"RunPod API response status: {response.status_code}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    logger.info(f"RunPod API response: {response_data}")
                    # RunPod trả về job ID
                    job_id_from_api = response_data.get("id", job_id)
                    logger.info(f"Using job ID: {job_id_from_api}")
                    return job_id_from_api
                else:
                    logger.error(f"RunPod API error response: {response.text}")
                    raise Exception(f"RunPod API returned status {response.status_code}: {response.text}")
                    
        except Exception as e:
            logger.error(f"Error calling RunPod document processing API: {str(e)}")
            raise Exception(f"Failed to call RunPod document processing API: {str(e)}")


def get_document_service() -> DocumentService:
    """
    Dependency để inject DocumentService
    """
    return DocumentService()
