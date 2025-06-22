from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings

gemini_embedding_model = GoogleGenerativeAIEmbeddings(
    model=settings.EMBEDDING_MODEL,
    google_api_key=settings.GOOGLE_API_KEY
)
