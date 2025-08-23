from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from app.core.agents.ai_chat_agent import AIChatAgent

# Simple module-level singleton to reuse the agent across requests
_ai_chat_agent_instance: AIChatAgent | None = None

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


class AIChatRequest(BaseModel):
    code: str
    results: List[dict] = Field(default_factory=list, description="Test case results")
    title: str
    user_message: Optional[str] = None
    all_tests_passed: Optional[bool] = None


class AIChatResponse(BaseModel):
    reply: str


@router.post("/", response_model=AIChatResponse)
async def create_ai_chat(payload: AIChatRequest) -> AIChatResponse:
    """
    Create AI chat response based on user's code, test results and message.
    """
    # Use AIChatAgent to compose reply
    global _ai_chat_agent_instance
    if _ai_chat_agent_instance is None:
        _ai_chat_agent_instance = AIChatAgent()

    reply_text = _ai_chat_agent_instance.chat(
        code=payload.code,
        results=payload.results,
        title=payload.title,
        user_message=payload.user_message,
        all_tests_passed=payload.all_tests_passed,
    )

    return AIChatResponse(reply=reply_text)
