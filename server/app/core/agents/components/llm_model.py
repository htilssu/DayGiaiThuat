from app.core.config import settings


def create_new_llm_model(
    thinking_budget: int = 0,
    top_k: int = 1,
    top_p: float = 0.95,
    temperature: float = 0.1,
):
    """
    Tạo một instance mới của model LLM Gemini với thinking_budget được chỉ định

    Args:
        thinking_budget: Số lượng token tối đa cho quá trình "suy nghĩ"

    Returns:
        ChatGoogleGenerativeAI: Instance mới của model LLM
        :param temperature: Độ sang tạo của mô hình (0.1 cho độ chính xác cao, 0.7 cho sáng tạo)
        :param thinking_budget: Số lượng token tối đa cho quá trình "suy nghĩ"
        :param top_p: Xác suất tích lũy tối đa cho các token được chọn
        :param top_k: Số lượng token hàng đầu được xem xét trong quá trình chọn lựa
    """
    # Lazy import - chỉ import khi cần thiết
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=settings.AGENT_LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        thinking_budget=thinking_budget,
        max_retries=6,
        top_p=top_p,
        temperature=temperature,
    )


def create_new_creative_llm_model(
    thinking_budget: int = 200,
    temperature: float = 0.7,
    top_k: int = 1,
    top_p: float = 0.95,
):
    """
    Tạo một instance mới của model LLM Gemini với thinking_budget cao hơn
    cho các tác vụ sáng tạo

    Returns:
        ChatGoogleGenerativeAI: Instance mới của model LLM
    """
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=settings.CREATIVE_LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        thinking_budget=thinking_budget,
        top_k=top_k,
        top_p=top_p,
        max_retries=6,
        temperature=temperature,  # Temperature cao hơn cho creativity
    )


def get_llm_model():
    """
    Trả về một instance được cache của model LLM Gemini

    Returns:
        ChatGoogleGenerativeAI: Instance được cache của model LLM
    """
    return create_new_llm_model()
