from app.core.config import settings


def get_embedding_model():
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    return GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL, google_api_key=settings.GOOGLE_API_KEY,
    )
