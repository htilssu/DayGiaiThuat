from typing import Literal
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from app.core.agents.components.embedding_model import gemini_embedding_model

# from app.core.config import settings

# pc = Pinecone(api_key=settings.PINECONE_API_KEY)
pc = Pinecone(
    api_key="pcsk_3E3Y6b_MeqXAcSxi9jGfw6oHBzSqyH5FrkCFvdPgeYS6EDYMiZepoKz2cFbiXqx7mUwsf3"
)

index_list = Literal["document", "exercise"]


def get_vector_store(index_name: index_list):
    if index_name not in [index.name for index in pc.list_indexes().indexes]:
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    pc_index = pc.Index(index_name)
    pc_vector_store = PineconeVectorStore(
        index=pc_index, embedding=gemini_embedding_model
    )
    return pc_vector_store


def get_index(index_name: index_list):
    if index_name not in [index.name for index in pc.list_indexes().indexes]:
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    pc_index = pc.Index(index_name)
    return pc_index
