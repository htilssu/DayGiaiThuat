from pydantic import BaseModel
from typing import Optional


class DocumentStatus(BaseModel):
    id: str
    filename: str
    status: str  # "processing", "completed", "failed"
    createdAt: str
    error: Optional[str] = None


class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    createdAt: str


class SearchResult(BaseModel):
    content: str
    metadata: dict


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
