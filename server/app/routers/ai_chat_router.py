from fastapi import APIRouter

router = APIRouter(
    prefix="/ai-chat",
    tags=["AI Chat"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
        400: {"description": "Bad request"},
    },
)


@router.get("/")
async def get_ai_chat():
    """
    Get AI chat endpoint
    """
    return {"message": "AI Chat endpoint"}


@router.post("/")
async def create_ai_chat():
    """
    Create AI chat session
    """
    return {"message": "AI Chat session created"}
