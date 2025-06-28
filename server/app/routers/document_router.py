from typing import List, Dict
from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks

from app.core.agents.components.document_store import get_vector_store
from app.schemas.document_schema import DocumentResponse, DocumentStatus

import shutil

router = APIRouter(prefix="/admin/document", tags=["document"])

# In-memory storage for document status (in production, use Redis or database)
document_status: Dict[str, DocumentStatus] = {}


def get_loader_for_file(filename: str):
    """Get appropriate loader based on file type"""
    from langchain_community.document_loaders import (
        PyPDFLoader,
        TextLoader,
        Docx2txtLoader,
    )

    file_extension = filename.split(".")[-1].lower()
    if file_extension == "pdf":
        return PyPDFLoader
    elif file_extension == "txt":
        return TextLoader
    elif file_extension in ["doc", "docx"]:
        return Docx2txtLoader
    else:
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type: {file_extension}"
        )


async def process_document(temp_path: str, document_id: str, filename: str):
    """Process document asynchronously"""
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    try:
        # Update status to processing
        document_status[document_id] = DocumentStatus(
            id=document_id,
            filename=filename,
            status="processing",
            createdAt=datetime.utcnow().isoformat(),
        )
        # Load document based on file type
        loader_class = get_loader_for_file(filename)
        loader = loader_class(temp_path)
        try:
            documents = loader.load()
        except Exception as e:
            print(f"[ERROR] Failed to load document: {e}")
            raise
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        # Add metadata to chunks
        for chunk in chunks:
            chunk.metadata.update(
                {
                    "source": filename,
                    "document_id": document_id,
                    "uploaded_at": datetime.utcnow().isoformat(),
                }
            )
        # Store in pinecone
        texts = [doc.page_content for doc in chunks]
        vector_store = get_vector_store("document")
        vector_store.add_texts(
            texts=texts,
            metadatas=[chunk.metadata for chunk in chunks],
            embedding_chunk_size=50,
        )

        # Update status to completed
        document_status[document_id] = DocumentStatus(
            id=document_id,
            filename=filename,
            status="completed",
            createdAt=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        # Update status to failed
        document_status[document_id] = DocumentStatus(
            id=document_id,
            filename=filename,
            status="failed",
            createdAt=datetime.utcnow().isoformat(),
            error=str(e),
        )
    finally:
        # Clean up the temporary file
        import os

        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/store")
async def store_document(files: List[UploadFile], background_tasks: BackgroundTasks):
    """
    Upload and store documents in vector database
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    document_responses = []
    for file in files:
        document_id = str(uuid4())

        # Save file to a temporary location first
        temp_path = f"/tmp/{document_id}_{file.filename}"
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        finally:
            file.file.close()

        # Create initial response
        document_response = DocumentResponse(
            id=document_id,
            filename=file.filename,
            status="processing",
            createdAt=datetime.utcnow().isoformat(),
        )
        # Add background task for processing
        background_tasks.add_task(
            process_document, temp_path, document_id, file.filename
        )
        document_responses.append(document_response)
    return {"documents": document_responses}


@router.get("/status")
async def get_document_status(ids: str):
    """
    Get status of documents by comma-separated IDs
    """
    document_ids = ids.split(",")
    statuses = []
    for doc_id in document_ids:
        if doc_id in document_status:
            statuses.append(document_status[doc_id])
    return statuses


@router.get("/search")
async def search_documents(query: str, limit: int = 5):
    """
    Search documents in vector database
    """
    try:
        vector_store = get_vector_store("document")
        results = vector_store.similarity_search(query, k=limit)
        return {
            "query": query,
            "results": [
                {"content": doc.page_content, "metadata": doc.metadata}
                for doc in results
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
