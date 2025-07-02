from typing import List
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks

from app.services.document_service import document_service
from app.schemas.document_schema import DocumentResponse

router = APIRouter(prefix="/admin/document", tags=["document"])


@router.post("/store")
async def store_document(files: List[UploadFile], background_tasks: BackgroundTasks):
    """
    Upload and store documents in vector database using DocLing and semantic chunking
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    document_responses = []

    for file in files:
        document_id = str(uuid4())

        try:
            # Save file to temporary location
            temp_path = await document_service.save_uploaded_file(file, document_id)

            # Create initial response
            document_response = DocumentResponse(
                id=document_id,
                filename=file.filename,
                status="processing",
                createdAt=datetime.now().isoformat(),
            )

            # Add background task for processing with semantic chunking
            background_tasks.add_task(
                document_service.process_document, temp_path, document_id, file.filename
            )

            document_responses.append(document_response)

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to save file {file.filename}: {str(e)}"
            )

    return {"documents": document_responses}


@router.get("/status")
async def get_document_status(ids: str):
    """
    Get status of documents by comma-separated IDs
    """
    document_ids = ids.split(",")
    statuses = document_service.get_document_status(document_ids)
    return statuses


@router.get("/search")
async def search_documents(
    query: str, limit: int = 5, source: str = None, document_id: str = None
):
    """
    Search documents in vector database with semantic chunking
    Supports filtering by source file or document ID
    """
    try:
        # Build filter metadata if provided
        filter_metadata = {}
        if source:
            filter_metadata["source"] = source
        if document_id:
            filter_metadata["document_id"] = document_id

        # Use filter if any filters are provided
        filter_to_use = filter_metadata if filter_metadata else None

        result = await document_service.search_documents(
            query=query, limit=limit, filter_metadata=filter_to_use
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/statistics")
async def get_document_statistics():
    """
    Get statistics about processed documents
    """
    try:
        stats = document_service.get_document_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get statistics: {str(e)}"
        )
