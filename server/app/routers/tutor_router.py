from fastapi import APIRouter, Depends
import httpx

from app.schemas.tutor_schema import AskTutorSchema
from app.utils.utils import get_current_user

router = APIRouter(prefix="/tutor", tags=["Giáo viên"])


@router.post("/ask", response_model=None)
async def post_tutor(user=Depends(get_current_user), data: AskTutorSchema = None):
    http_client = httpx.AsyncClient()
    response = await http_client.post(
        "http://localhost:5678/webhook/2d57a76b-98c7-431d-9cae-83bfc6543a9f",
        json=data.model_dump(),
        timeout=300,
    )

    return {"status_code": response.status_code, "data": response.json()}
