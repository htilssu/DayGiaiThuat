from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


def create_new_gemini_llm_model(thinking_budget: int = 0):
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        thinking_budget=thinking_budget,
    )


gemini_llm_model = ChatGoogleGenerativeAI(
    model=settings.LLM_MODEL,
    google_api_key=settings.GOOGLE_API_KEY,
    thinking_budget=0,
)
