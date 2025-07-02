from pydantic import BaseModel
from typing import Optional, List


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
    chunks_count: Optional[int] = None


class SearchResult(BaseModel):
    content: str
    metadata: dict
    source: str
    chunk_index: int


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResult]


class DocumentStatistics(BaseModel):
    total_documents: int
    completed: int
    failed: int
    processing: int
    success_rate: float
