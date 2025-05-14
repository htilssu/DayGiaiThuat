from langchain_pinecone import PineconeVectorStore

from app.core.agents.components.embedding_model import gemini_embedding_model
from pinecone import Pinecone

from app.core.config import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)

pc_index = pc.Index("giaithuat")

pinecone_vector_store =  PineconeVectorStore(index=pc_index, embedding=gemini_embedding_model)

