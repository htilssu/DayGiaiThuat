from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


def create_new_gemini_llm_model(thinking_budget: int = 0):
    """
    Tạo một instance mới của model LLM Gemini với thinking_budget được chỉ định

    Args:
        thinking_budget: Số lượng token tối đa cho quá trình "suy nghĩ"

    Returns:
        ChatGoogleGenerativeAI: Instance mới của model LLM
    """
    return ChatGoogleGenerativeAI(
        model=settings.AGENT_LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        thinking_budget=thinking_budget,
    )


def create_new_creative_llm_model():
    """
    Tạo một instance mới của model LLM Gemini với thinking_budget cao hơn
    cho các tác vụ sáng tạo

    Returns:
        ChatGoogleGenerativeAI: Instance mới của model LLM
    """
    return ChatGoogleGenerativeAI(
        model=settings.CREATIVE_LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        thinking_budget=1000,
    )


def get_gemini_llm_model():
    """
    Trả về một instance được cache của model LLM Gemini

    Returns:
        ChatGoogleGenerativeAI: Instance được cache của model LLM
    """
    return ChatGoogleGenerativeAI(
        model=settings.AGENT_LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        thinking_budget=0,
    )
