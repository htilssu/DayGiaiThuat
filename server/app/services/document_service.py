from typing import List, Dict
from datetime import datetime
import os
import shutil
from pathlib import Path

from langchain_docling import DoclingLoader

from app.core.agents.components.document_store import get_vector_store
from app.core.config import settings

from app.schemas.document_schema import DocumentStatus


class DocumentService:
    def __init__(self):
        self.document_status: Dict[str, DocumentStatus] = {}
        # Initialize embeddings for semantic chunking
        from app.core.agents.components.embedding_model import get_embedding_model

        self.embeddings = get_embedding_model()

    async def process_document(
        self, temp_path: str, document_id: str, filename: str
    ) -> None:
        """
        Process document asynchronously using DocLing and semantic chunking
        """
        from langchain_experimental.text_splitter import SemanticChunker

        try:
            # Update status to processing
            self.document_status[document_id] = DocumentStatus(
                id=document_id,
                filename=filename,
                status="processing",
                createdAt=datetime.now().isoformat(),
            )

            # Load document using DocLing
            loader = DoclingLoader(temp_path)
            documents = loader.load()

            if not documents:
                raise ValueError("No content could be extracted from the document")

            # Use semantic chunking instead of character-based splitting
            semantic_chunker = SemanticChunker(
                embeddings=self.embeddings,
                breakpoint_threshold_type="percentile",
                breakpoint_threshold_amount=85,
            )

            # Split documents using semantic chunking
            chunks = []
            for doc in documents:
                if doc.page_content.strip():  # Only process non-empty documents
                    doc_chunks = semantic_chunker.split_documents([doc])
                    chunks.extend(doc_chunks)

            if not chunks:
                raise ValueError(
                    "No meaningful chunks could be created from the document"
                )

            # Add metadata to chunks
            for i, chunk in enumerate(chunks):
                chunk.metadata.update(
                    {
                        "source": filename,
                        "document_id": document_id,
                        "chunk_index": i,
                        "uploaded_at": datetime.now().isoformat(),
                        "chunk_type": "semantic",
                        "total_chunks": len(chunks),
                    }
                )

            # Store in vector database
            await self._store_chunks_in_vector_db(chunks)

            # Update status to completed
            self.document_status[document_id] = DocumentStatus(
                id=document_id,
                filename=filename,
                status="completed",
                createdAt=datetime.now().isoformat(),
                chunks_count=len(chunks),
            )

        except Exception as e:
            # Update status to failed
            self.document_status[document_id] = DocumentStatus(
                id=document_id,
                filename=filename,
                status="failed",
                createdAt=datetime.now().isoformat(),
                error=str(e),
            )
            raise e
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    async def _store_chunks_in_vector_db(self, chunks: List) -> None:
        """
        Store document chunks in vector database
        """
        try:
            vector_store = get_vector_store("document")

            # Extract texts and clean metadata
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [self._clean_metadata(chunk.metadata) for chunk in chunks]

            # Store in batches to avoid overwhelming the vector store
            batch_size = 50
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i : i + batch_size]
                batch_metadata = metadatas[i : i + batch_size]

                vector_store.add_texts(
                    texts=batch_texts,
                    metadatas=batch_metadata,
                    embedding_chunk_size=batch_size,
                )

        except Exception as e:
            raise Exception(f"Failed to store chunks in vector database: {str(e)}")

    def _clean_metadata(self, metadata: dict) -> dict:
        """
        Clean metadata to ensure compatibility with Pinecone.
        Pinecone only accepts string, number, boolean or list of strings for metadata values.
        """
        cleaned_metadata = {}

        # Only keep simple types that Pinecone supports
        allowed_keys = {
            "source",
            "document_id",
            "chunk_index",
            "uploaded_at",
            "chunk_type",
            "total_chunks",
            "page",
            "bbox",
        }

        for key, value in metadata.items():
            # Skip complex objects like dl_meta
            if key not in allowed_keys:
                continue

            if isinstance(value, (str, int, float, bool)):
                cleaned_metadata[key] = value
            elif isinstance(value, list) and all(
                isinstance(item, str) for item in value
            ):
                cleaned_metadata[key] = value
            elif value is not None:
                # Convert other types to string representation
                cleaned_metadata[key] = str(value)

        return cleaned_metadata

    async def save_uploaded_file(self, file, document_id: str) -> str:
        """
        Save uploaded file to temporary location
        """
        # Ensure uploads directory exists
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)

        temp_path = upload_dir / f"{document_id}_{file.filename}"

        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            return str(temp_path)
        finally:
            file.file.close()

    def get_document_status(self, document_ids: List[str]) -> List[DocumentStatus]:
        """
        Get status of documents by IDs
        """
        statuses = []
        for doc_id in document_ids:
            if doc_id in self.document_status:
                statuses.append(self.document_status[doc_id])
        return statuses

    async def search_documents(
        self, query: str, limit: int = 5, filter_metadata: Dict = None
    ) -> Dict:
        """
        Search documents in vector database with optional metadata filtering
        """
        try:
            vector_store = get_vector_store("document")

            # Perform similarity search
            if filter_metadata:
                results = vector_store.similarity_search(
                    query, k=limit, filter=filter_metadata
                )
            else:
                results = vector_store.similarity_search(query, k=limit)

            return {
                "query": query,
                "total_results": len(results),
                "results": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "source": doc.metadata.get("source", "unknown"),
                        "chunk_index": doc.metadata.get("chunk_index", 0),
                    }
                    for doc in results
                ],
            }
        except Exception as e:
            raise Exception(f"Document search failed: {str(e)}")

    def get_document_statistics(self) -> Dict:
        """
        Get statistics about processed documents
        """
        total_docs = len(self.document_status)
        completed_docs = sum(
            1
            for status in self.document_status.values()
            if status.status == "completed"
        )
        failed_docs = sum(
            1 for status in self.document_status.values() if status.status == "failed"
        )
        processing_docs = sum(
            1
            for status in self.document_status.values()
            if status.status == "processing"
        )

        return {
            "total_documents": total_docs,
            "completed": completed_docs,
            "failed": failed_docs,
            "processing": processing_docs,
            "success_rate": (
                (completed_docs / total_docs * 100) if total_docs > 0 else 0
            ),
        }


# Create singleton instance
document_service = DocumentService()
