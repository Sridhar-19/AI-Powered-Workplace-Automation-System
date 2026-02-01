"""
Document management service.
"""
import logging
import uuid
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime

from app.core.document_loader import create_document_loader
from app.core.text_splitter import create_text_splitter
from app.core.embeddings_service import create_embeddings_service
from app.core.pinecone_service import create_pinecone_service
from app.models.document_models import DocumentMetadata, DocumentStatus, DocumentChunk
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class DocumentService:
    """Service for document management operations."""

    def __init__(self):
        self.document_loader = create_document_loader()
        self.text_splitter = create_text_splitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        self.embeddings_service = create_embeddings_service()
        self.pinecone_service = create_pinecone_service()
        self.documents_db: Dict[str, DocumentMetadata] = {}  # In-memory storage

    async def upload_and_process_document(
        self,
        file_content: bytes,
        filename: str,
        file_type: str
    ) -> DocumentMetadata:
        """
        Upload and process a document.
        
        Args:
            file_content: Document file content
            filename: Original filename
            file_type: File extension
            
        Returns:
            Document metadata
        """
        try:
            document_id = str(uuid.uuid4())
            
            # Create metadata
            metadata = DocumentMetadata(
                document_id=document_id,
                filename=filename,
                file_type=file_type,
                file_size=len(file_content),
                status=DocumentStatus.PROCESSING
            )
            
            self.documents_db[document_id] = metadata
            
            # Load document
            documents = self.document_loader.load_from_bytes(
                file_content, filename, file_type
            )
            
            # Update metadata
            if documents:
                first_doc = documents[0]
                metadata.title = first_doc.metadata.get("title", filename)
                metadata.author = first_doc.metadata.get("author", "")
                metadata.num_pages = first_doc.metadata.get("num_pages")
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            metadata.num_chunks = len(chunks)
            
            # Add document_id to chunk metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata["document_id"] = document_id
                chunk.metadata["id"] = f"{document_id}_chunk_{i}"
            
            # Generate embeddings and store in Pinecone
            vectors = self.embeddings_service.embed_documents(chunks)
            self.pinecone_service.upsert(vectors=vectors)
            
            # Update status
            metadata.status = DocumentStatus.COMPLETED
            self.documents_db[document_id] = metadata
            
            logger.info(f"Processed document {document_id}: {metadata.num_chunks} chunks")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            if document_id in self.documents_db:
                self.documents_db[document_id].status = DocumentStatus.FAILED
            raise

    async def get_document(self, document_id: str) -> Optional[DocumentMetadata]:
        """Get document metadata by ID."""
        return self.documents_db.get(document_id)

    async def delete_document(self, document_id: str) -> bool:
        """
        Delete document and its chunks from Pinecone.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            if document_id not in self.documents_db:
                return False
            
            # Delete from Pinecone (filter by document_id in metadata)
            self.pinecone_service.delete(
                filter={"document_id": document_id}
            )
            
            # Delete from local storage
            del self.documents_db[document_id]
            
            logger.info(f"Deleted document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            raise

    async def list_documents(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> List[DocumentMetadata]:
        """List all documents with pagination."""
        all_docs = list(self.documents_db.values())
        return all_docs[skip:skip + limit]

    async def get_document_count(self) -> int:
        """Get total document count."""
        return len(self.documents_db)


# Global service instance
_document_service: Optional[DocumentService] = None


def get_document_service() -> DocumentService:
    """Get or create document service instance."""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service
