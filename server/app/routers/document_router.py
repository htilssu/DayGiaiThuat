from typing import List
from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks, Depends

from app.services.document_service import get_document_service, DocumentService
from app.services.storage_service import get_storage_service, StorageService
from app.schemas.document_schema import DocumentResponse
from app.utils.utils import get_current_user
from app.schemas.user_profile_schema import UserExcludeSecret

router = APIRouter(prefix="/admin/document", tags=["document"])


def get_admin_user(current_user: UserExcludeSecret = Depends(get_current_user)):
    """Kiểm tra quyền admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền truy cập chức năng này",
        )
    return current_user


@router.post("/store")
async def store_document(
    files: List[UploadFile],
    background_tasks: BackgroundTasks,
    document_service: DocumentService = Depends(get_document_service),
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    """
    Upload documents to object storage and call external API for processing
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    document_responses = []

    for file in files:
        document_id = str(uuid4())

        try:
            # 1. Upload file to object storage
            upload_result = await storage_service.upload_document(file, document_id)
            document_url = upload_result["url"]

            # Create initial response
            document_response = DocumentResponse(
                id=document_id,
                filename=file.filename,
                status="processing",
                createdAt=datetime.now().isoformat(),
            )

            # 2. Add background task for calling external API
            background_tasks.add_task(
                document_service.call_external_document_processing_api,
                document_url,
                document_id,
                file.filename,
            )

            document_responses.append(document_response)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process file {file.filename}: {str(e)}",
            )

    return {"documents": document_responses}


@router.get("/status")
async def get_document_status(
    ids: str, document_service: DocumentService = Depends(get_document_service)
):
    """
    Get status of documents by comma-separated IDs
    """
    document_ids = ids.split(",")
    statuses = document_service.get_document_status(document_ids)
    return statuses


@router.get("/search")
async def search_documents(
    query: str,
    limit: int = 5,
    source: str = None,
    document_id: str = None,
    document_service: DocumentService = Depends(get_document_service),
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
async def get_document_statistics(
    document_service: DocumentService = Depends(get_document_service),
):
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
