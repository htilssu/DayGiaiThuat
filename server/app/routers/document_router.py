from typing import List

from fastapi import APIRouter, UploadFile

router = APIRouter(prefix="/admin/document", tags=["document"])


@router.post("/store")
async def store_document(files: List[UploadFile]):
    """
    :param file: Tệp tài liệu được upload để store vào vectorstore
    :return:
    """
    # Lazy import - chỉ import khi cần thiết
    from langchain_docling import DoclingLoader

    url = "https://arxiv.org/pdf/2308.10379"
    doc = DoclingLoader(url)
    documents = doc.load()

    return {
        "message": "Document stored successfully",
        "documents_count": len(documents),
    }
