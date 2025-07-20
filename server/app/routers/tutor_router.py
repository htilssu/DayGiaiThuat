from fastapi import APIRouter, Depends
import uuid

from starlette.responses import StreamingResponse

from app.schemas.tutor_schema import AskTutorSchema
from app.utils.utils import get_current_user
from app.core.agents.tutor_agent import TutorAgent, get_tutor_agent
from app.schemas.user_profile_schema import UserExcludeSecret


router = APIRouter(prefix="/tutor", tags=["Giáo viên"])


@router.post("/chat", response_model=None)
async def post_tutor(
    data: AskTutorSchema,
    user: UserExcludeSecret = Depends(get_current_user),
    tutor_agent: TutorAgent = Depends(get_tutor_agent),
):
    if data.session_id is None:
        data.session_id = str(uuid.uuid4())

    async def tutor_data_streamer():
        try:
            async for chunk in tutor_agent.act_stream(
                type=data.type,
                context_id=data.context_id,
                session_id=data.session_id,
                question=data.question,
            ):
                if chunk:  # Chỉ yield khi chunk có giá trị
                    if isinstance(chunk, str):
                        yield chunk.encode("utf-8")
                    else:
                        yield str(chunk).encode("utf-8")
        except Exception as e:
            error_message = f"Error: {str(e)}"
            yield error_message.encode("utf-8")

    return StreamingResponse(
        tutor_data_streamer(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
