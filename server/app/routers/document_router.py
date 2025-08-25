from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks, Depends

from app.schemas.DocumentRequestExternal import DocumentRequestExternal
from app.schemas.document_schema import (
    DocumentResponse,
    RunpodWebhookRequest,
)
from app.schemas.user_profile_schema import UserExcludeSecret
from app.services.document_service import (
    get_document_service,
    DocumentService,
    call_external_document_processing_api,
    create_document_processing_job,
    update_job_status,
)
from app.services.storage_service import get_storage_service, StorageService
from app.utils.utils import get_current_user

router = APIRouter(prefix="/admin/document", tags=["Tài liệu"])

webhook_router = APIRouter(prefix="/document", tags=["Tài liệu - Webhook"])


def get_admin_user(current_user: UserExcludeSecret = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền truy cập chức năng này",
        )
    return current_user


@router.post("/store")
async def store_document(
    files: List[UploadFile],
    course_id: Optional[int] = None,
    storage_service: StorageService = Depends(get_storage_service),
    admin_user: UserExcludeSecret = Depends(get_admin_user),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    document_responses = []

    for file in files:
        document_id = str(uuid4())

        try:
            upload_result = await storage_service.upload_document(file, document_id)
            document_url = upload_result["url"]

            job_id = await call_external_document_processing_api(
                DocumentRequestExternal(
                    document_url, "https://three-glasses-brush.loca.lt/document/webhook"
                )
            )

            await create_document_processing_job(
                document_id=document_id,
                job_id=job_id,
                filename=file.filename or "",
                document_url=document_url or "",
                course_id=course_id,
            )

            document_response = DocumentResponse(
                id=document_id,
                filename=file.filename or "",
                status="IN_QUEUE",
                createdAt=datetime.now().isoformat(),
                job_id=job_id,
                course_id=course_id,
            )

            document_responses.append(document_response)

        except Exception as e:
            print(f"Failed to process file {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process file {file.filename}: {str(e)}",
            )

    return {"documents": document_responses}


@webhook_router.post("/webhook")
async def handle_runpod_webhook(
    webhook_data: RunpodWebhookRequest,
    background_tasks: BackgroundTasks,
    document_service: DocumentService = Depends(get_document_service),
):
    try:
        job = await update_job_status(
            job_id=webhook_data.id,
            status=webhook_data.status,
            result=webhook_data.output,
            error_message=webhook_data.error,
        )

        if not job:
            raise HTTPException(
                status_code=404, detail=f"Job {webhook_data.id} not found"
            )

        if webhook_data.status == "COMPLETED" and webhook_data.output:
            background_tasks.add_task(
                document_service.process_completed_document,
                job_id=webhook_data.id,
                result=webhook_data.output,
            )

        return {"status": "success", "message": "Webhook processed successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process webhook: {str(e)}"
        )


@router.get("/status")
async def get_document_status(
    ids: str, document_service: DocumentService = Depends(get_document_service)
):
    document_ids = ids.split(",")
    statuses = document_service.get_document_status(document_ids)
    return statuses


@router.get("/search")
async def search_documents(
    query: str,
    limit: int = 5,
    source: str = "",
    document_id: str = "",
    document_service: DocumentService = Depends(get_document_service),
):
    try:
        filter_metadata = {}
        if source:
            filter_metadata["source"] = source
        if document_id:
            filter_metadata["document_id"] = document_id

        filter_to_use = filter_metadata if filter_metadata else {}

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
    try:
        stats = await document_service.get_document_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get statistics: {str(e)}"
        )
