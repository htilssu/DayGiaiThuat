from typing import List

from fastapi import APIRouter, UploadFile
from langchain_docling import DoclingLoader

router = APIRouter(prefix="/document", tags=["document"])


@router.post("/store")
async def store_document(files: List[UploadFile]):
    """
       :param file: Tệp tài liệu được upload để store vào vectorstore
       :return:
    """
    
    url = "https://arxiv.org/pdf/2308.10379"
    doc = DoclingLoader(url)
    documents = doc.load()  

    return {"a": documents}
