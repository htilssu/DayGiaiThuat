from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.core.agents.ai_chat_agent import AIChatAgent


router = APIRouter(prefix="/ai-chat", tags=["ai-chat"])


class AIChatRequest(BaseModel):
    code: str
    results: List[dict]
    title: str
    user_message: Optional[str] = None
    all_tests_passed: Optional[bool] = None


class AIChatResponse(BaseModel):
    reply: str


@router.post("/", response_model=AIChatResponse)
async def ai_chat(request: AIChatRequest):
    try:
        agent = AIChatAgent("AIzaSyCBRk6miLbcoWpjpKt__sdYRahOcx2C2i0")
        reply = agent.chat(
            code=request.code,
            results=request.results,
            title=request.title,
            user_message=request.user_message,
            all_tests_passed=request.all_tests_passed,
        )
        return AIChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
