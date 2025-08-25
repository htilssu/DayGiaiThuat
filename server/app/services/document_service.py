import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import httpx
from sqlalchemy import select

from app.core.agents.components.document_store import get_vector_store
from app.core.config import settings
from app.database.database import get_independent_db_session
from app.models.document_processing_job_model import DocumentProcessingJob
from app.schemas.DocumentRequestExternal import DocumentRequestExternal
from app.schemas.document_schema import DocumentStatus

logger = logging.getLogger(__name__)


async def call_external_document_processing_api(
    document: DocumentRequestExternal,
) -> str:
    if not settings.DOCUMENT_PROCESSING_ENDPOINT:
        raise Exception("DOCUMENT_PROCESSING_ENDPOINT chưa được cấu hình")

    try:
        payload = {
            "input": {"url": document.document_url},
            "webhook": document.webhook_url,
        }

        async with httpx.AsyncClient(
            timeout=settings.DOCUMENT_PROCESSING_TIMEOUT
        ) as client:
            response = await client.post(
                settings.DOCUMENT_PROCESSING_ENDPOINT,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": settings.RUNPOD_API_KEY,
                },
            )

            response.raise_for_status()
            result = response.json()

            job_id = result.get("id")
            if not job_id:
                raise Exception("No job ID returned from external API")

            return job_id

    except httpx.TimeoutException:
        error_msg = (
            f"Timeout khi gọi external API sau {settings.DOCUMENT_PROCESSING_TIMEOUT}s"
        )
        logger.error(error_msg)
        raise Exception(error_msg)

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
        logger.error(error_msg)
        raise Exception(error_msg)

    except Exception as e:
        error_msg = f"Lỗi khi gọi external API: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


async def create_document_processing_job(
    document_id: str,
    job_id: str,
    filename: str,
    document_url: str,
    course_id: Optional[int] = None,
) -> DocumentProcessingJob:
    """
    Tạo record DocumentProcessingJob trong database
    """
    async with get_independent_db_session() as db:
        try:
            job = DocumentProcessingJob(
                id=document_id,
                job_id=job_id,
                filename=filename,
                document_url=document_url,
                course_id=course_id,
                status="IN_QUEUE",
            )
            db.add(job)
            await db.commit()
            await db.refresh(job)
            return job
        except Exception as e:
            await db.rollback()
            raise Exception(f"Failed to create document processing job: {str(e)}")
        finally:
            await db.close()


async def update_job_status(
    job_id: str,
    status: str,
    result: str,
    error_message: Optional[str] = None,
) -> Optional[DocumentProcessingJob]:
    """
    Cập nhật trạng thái job từ webhook
    """
    async with get_independent_db_session() as db:
        try:
            job = (
                await db.execute(
                    select(DocumentProcessingJob).where(
                        DocumentProcessingJob.job_id == job_id
                    )
                )
            ).scalar_one_or_none()

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
        finally:
            await db.close()


class DocumentService:
    def __init__(self):
        self.document_status: Dict[str, DocumentStatus] = {}
        from app.core.agents.components.embedding_model import get_embedding_model

        self.embeddings = get_embedding_model()

    async def process_completed_document(self, job_id: str, result: str) -> None:
        async with get_independent_db_session() as db:
            try:
                job = (
                    await db.execute(
                        select(DocumentProcessingJob).where(
                            DocumentProcessingJob.job_id == job_id
                        )
                    )
                ).scalar_one_or_none()

                if not job:
                    raise Exception(f"Job {job_id} not found")

                await self._process_docling_result(job, result)

                # Nếu thuộc về course, gọi agent tạo topic và lesson
                if job.course_id:
                    await self._trigger_course_content_generation(job.course_id)

                logger.info(f"Document processing completed for job {job_id}")

            except Exception as e:
                logger.error(f"Error processing completed document {job_id}: {str(e)}")
                raise e
            finally:
                await db.close()

    async def _process_docling_result(
        self, job: DocumentProcessingJob, result: str
    ) -> None:
        """
        Xử lý kết quả từ Docling và lưu vào vector database
        """
        from langchain_core.documents import Document
        from langchain_experimental.text_splitter import SemanticChunker

        try:
            if not result:
                raise ValueError("No content found in processing result")

            doc = Document(
                page_content=result,
                metadata={
                    "source": job.filename,
                    "document_id": job.id,
                    "document_url": job.document_url,
                    "course_id": job.course_id,
                    "processed_at": datetime.now().isoformat(),
                },
            )

            semantic_chunker = SemanticChunker(
                embeddings=self.embeddings,
                breakpoint_threshold_type="percentile",
                breakpoint_threshold_amount=95,
                buffer_size=3,
            )

            chunks = semantic_chunker.split_documents([doc])

            if not chunks:
                raise ValueError("No meaningful chunks could be created")

            for i, chunk in enumerate(chunks):
                chunk.metadata.update(
                    {
                        "chunk_index": i,
                        "chunk_type": "semantic",
                        "total_chunks": len(chunks),
                    }
                )

            await self._store_chunks_in_vector_db(chunks)

            logger.info(f"Processed {len(chunks)} chunks for document {job.id}")

        except Exception as e:
            raise Exception(f"Failed to process docling result: {str(e)}")

    async def _trigger_course_content_generation(self, course_id: int) -> None:
        try:

            # TODO: Implement the actual agent call to generate course content

            logger.info(f"Triggered course content generation for course {course_id}")

        except Exception as e:
            logger.error(
                f"Error triggering course content generation for course {course_id}: {str(e)}"
            )

    async def _store_chunks_in_vector_db(self, chunks: List) -> None:
        try:
            vector_store = get_vector_store("document")

            texts = [chunk.page_content for chunk in chunks]
            metadatas = [self._clean_metadata(chunk.metadata) for chunk in chunks]

            batch_size = 50
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i : i + batch_size]
                batch_metadata = metadatas[i : i + batch_size]

                vector_store.add_texts(
                    texts=batch_texts,
                    metadatas=batch_metadata,
                    embedding_chunk_size=batch_size,
                )

        except Exception as e:
            raise Exception(f"Failed to store chunks in vector database: {str(e)}")

    def _clean_metadata(self, metadata: dict) -> dict:
        cleaned_metadata = {}

        # Only keep simple types that Pinecone supports
        allowed_keys = {
            "source",
            "document_id",
            "chunk_index",
            "uploaded_at",
            "chunk_type",
            "total_chunks",
            "page",
            "bbox",
            "course_id",
            "document_url",
            "processed_at",
        }

        for key, value in metadata.items():
            if key not in allowed_keys:
                continue

            if isinstance(value, (str, int, float, bool)):
                cleaned_metadata[key] = value
            elif isinstance(value, list) and all(
                isinstance(item, str) for item in value
            ):
                cleaned_metadata[key] = value
            elif value is not None:
                cleaned_metadata[key] = str(value)

        return cleaned_metadata

    async def save_uploaded_file(self, file, document_id: str) -> str:
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)

        temp_path = upload_dir / f"{document_id}_{file.filename}"

        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return str(temp_path)
        finally:
            file.file.close()

    async def get_document_status(
        self, document_ids: List[str]
    ) -> List[DocumentStatus]:
        async with get_independent_db_session() as db:
            try:
                jobs = (
                    (
                        await db.execute(
                            select(DocumentProcessingJob).where(
                                DocumentProcessingJob.id.in_(document_ids)
                            )
                        )
                    )
                    .scalars()
                    .all()
                )

                return [
                    DocumentStatus(
                        id=job.id,
                        filename=job.filename,
                        status=job.status,
                        createdAt=job.created_at.isoformat(),
                        error=job.error_message,
                        chunks_count=None,
                    )
                    for job in jobs
                ]
            except Exception as e:
                raise Exception(f"Failed to get document status: {str(e)}")

    async def search_documents(
        self, query: str, limit: int = 5, filter_metadata: Dict = None
    ) -> Dict:
        try:
            vector_store = get_vector_store("document")

            if filter_metadata:
                results = vector_store.similarity_search(
                    query, k=limit, filter=filter_metadata
                )
            else:
                results = vector_store.similarity_search(query, k=limit)

            return {
                "query": query,
                "total_results": len(results),
                "results": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "source": doc.metadata.get("source", "unknown"),
                        "chunk_index": doc.metadata.get("chunk_index", 0),
                    }
                    for doc in results
                ],
            }
        except Exception as e:
            raise Exception(f"Document search failed: {str(e)}")

    async def get_document_statistics(self) -> Dict:
        """
        Get statistics about processed documents from database
        """

        async with get_independent_db_session() as db:
            try:
                total_docs = (
                    (await db.execute(select(DocumentProcessingJob))).scalars().all()
                )

                total_count = len(total_docs)
                processing_count = len(
                    [j for j in total_docs if j.status == "IN_PROGRESS"]
                )
                completed_count = len(
                    [j for j in total_docs if j.status == "COMPLETED"]
                )
                failed_count = len([j for j in total_docs if j.status == "FAILED"])

                # TODO: Calculate total chunks from vector DB
                total_chunks = 0

                return {
                    "total_documents": total_count,
                    "processing_documents": processing_count,
                    "completed_documents": completed_count,
                    "failed_documents": failed_count,
                    "total_chunks": total_chunks,
                }
            finally:
                await db.close()

            return {}


async def get_document_service() -> DocumentService:
    return DocumentService()
