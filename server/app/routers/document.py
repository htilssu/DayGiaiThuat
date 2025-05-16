from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from app.schemas.exercise import GetExerciseSchema

router = APIRouter(prefix="/document", tags=["document"])


class DocumentStoreSchema(BaseModel):
    file: str


@router.post("/store", response_model=GetExerciseSchema)
async def store_document(file: UploadFile):
    """
       :param file: Tệp tài liệu được upload để store vào vectorstore
       :return:
    """
    return file.filename
