from functools import lru_cache
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings


@lru_cache(maxsize=1)
def get_gemini_embedding_model():
    """
    Trả về một instance được cache của model embedding Gemini

    Returns:
        GoogleGenerativeAIEmbeddings: Instance được cache của model embedding
    """
    return GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL, google_api_key=settings.GOOGLE_API_KEY
    )
