from typing import Literal
from functools import lru_cache
from langchain_pinecone import PineconeVectorStore

from app.core.agents.components.embedding_model import get_gemini_embedding_model
from pinecone import Pinecone

from app.core.config import settings


@lru_cache(maxsize=1)
def get_pinecone_client():
    """
    Trả về một instance được cache của Pinecone client

    Returns:
        Pinecone: Instance được cache của Pinecone client
    """
    return Pinecone(api_key=settings.PINECONE_API_KEY)


index_list = Literal["document", "exercise"]


def create_index(index_name: index_list):
    """
    Tạo một index mới trong Pinecone

    Args:
        index_name: Tên của index cần tạo
    """
    pc = get_pinecone_client()
    pc_index = pc.Index(index_name)
    pc_index.create(dimension=768, metric="cosine")


def get_vector_store(index_name: index_list):
    """
    Trả về một vector store được liên kết với index được chỉ định

    Args:
        index_name: Tên của index cần sử dụng

    Returns:
        PineconeVectorStore: Vector store được liên kết với index
    """
    pc = get_pinecone_client()
    pc_index = pc.Index(index_name)
    pc_vector_store = PineconeVectorStore(
        index=pc_index, embedding=get_gemini_embedding_model()
    )
    return pc_vector_store
