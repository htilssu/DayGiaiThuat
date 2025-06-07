from typing import Literal
from langchain_pinecone import PineconeVectorStore

from app.core.agents.components.embedding_model import gemini_embedding_model
from pinecone import Pinecone

from app.core.config import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)

index_list = Literal["document", "exercise"]


def create_index(index_name: index_list):
    pc_index = pc.Index(index_name)
    pc_index.create(dimension=768, metric="cosine")


def get_vector_store(index_name: index_list):
    pc_index = pc.Index(index_name)
    pc_vector_store = PineconeVectorStore(
        index=pc_index, embedding=gemini_embedding_model
    )
    return pc_vector_store
