from typing import Literal

from pinecone import ServerlessSpec

from app.core.agents.components.embedding_model import get_embedding_model
from app.core.config import settings


def get_pinecone_client():
    from pinecone import Pinecone

    return Pinecone(api_key=settings.PINECONE_API_KEY)


index_list = Literal["document", "exercise"]


def create_index(index_name: index_list):
    """
    Tạo một index mới trong Pinecone

    Args:
        index_name: Tên của index cần tạo
    """
    pc = get_pinecone_client()
    pc.create_index(
        index_name,
        dimension=3072,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )


def get_vector_store(index_name: index_list):
    from langchain_pinecone import PineconeVectorStore

    pc_index = get_index(index_name)
    pc_vector_store = PineconeVectorStore(
        index=pc_index, embedding=get_embedding_model()
    )
    return pc_vector_store


def get_index(index_name: index_list):
    pc = get_pinecone_client()
    if index_name not in [index.name for index in pc.list_indexes().indexes]:
        create_index(index_name)
    pc_index = pc.Index(index_name)
    return pc_index
