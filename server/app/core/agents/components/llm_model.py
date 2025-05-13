from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

llm_model_name = "models/gemini-2.5-flash-preview-04-17"

gemini_llm_model = ChatGoogleGenerativeAI(model=llm_model_name,
                                          google_api_key=settings.GOOGLE_API_KEY, )
