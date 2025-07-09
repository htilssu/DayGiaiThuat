from app.core.config import settings


def create_new_llm_model(thinking_budget: int = 0):
    """
    Tạo một instance mới của model LLM Gemini với thinking_budget được chỉ định

    Args:
        thinking_budget: Số lượng token tối đa cho quá trình "suy nghĩ"

    Returns:
        ChatGoogleGenerativeAI: Instance mới của model LLM
    """
    # Lazy import - chỉ import khi cần thiết
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=settings.AGENT_LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        thinking_budget=thinking_budget,
        max_retries=6,
        temperature=0.1,  # Thêm temperature để model ít random hơn
    )


def create_new_creative_llm_model():
    """
    Tạo một instance mới của model LLM Gemini với thinking_budget cao hơn
    cho các tác vụ sáng tạo

    Returns:
        ChatGoogleGenerativeAI: Instance mới của model LLM
    """
    # Lazy import - chỉ import khi cần thiết
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=settings.CREATIVE_LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        thinking_budget=1000,
        max_retries=6,
        temperature=0.7,  # Temperature cao hơn cho creativity
    )


def get_llm_model():
    """
    Trả về một instance được cache của model LLM Gemini

    Returns:
        ChatGoogleGenerativeAI: Instance được cache của model LLM
    """
    return create_new_llm_model()
