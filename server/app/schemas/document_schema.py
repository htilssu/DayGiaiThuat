from typing import Optional, Any, Dict, List
from pydantic import BaseModel
from datetime import datetime


class DocumentStatus(BaseModel):
    id: str
    filename: str
    status: str  # "processing", "completed", "failed"
    createdAt: str
    error: Optional[str] = None
    chunks_count: Optional[int] = None


class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    createdAt: str
    job_id: Optional[str] = None
    course_id: Optional[int] = None


class DocumentProcessingJobResponse(BaseModel):
    id: str
    job_id: str
    filename: str
    status: str
    course_id: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None


class RunpodWebhookRequest(BaseModel):

    id: str
    status: str
    output: str
    error: Optional[str] = None
    executionTime: Optional[int] = None
    delayTime: Optional[int] = None


class DocumentSearchResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: float


class DocumentSearchResponse(BaseModel):
    results: List[DocumentSearchResult]
    total: int
    query: str


class DocumentStatistics(BaseModel):
    total_documents: int
    processing_documents: int
    completed_documents: int
    failed_documents: int
    total_chunks: int


class StoreByTextRequest(BaseModel):
    text: str
    course_id: Optional[int] = None
