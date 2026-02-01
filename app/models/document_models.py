"""
Pydantic models for documents.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentUpload(BaseModel):
    """Request model for document upload."""
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type/extension")
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "quarterly_report.pdf",
                "file_type": "pdf"
            }
        }


class DocumentMetadata(BaseModel):
    """Document metadata."""
    document_id: str = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type")
    file_size: int = Field(..., description="File size in bytes")
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    status: DocumentStatus = Field(default=DocumentStatus.PENDING)
    num_pages: Optional[int] = Field(None, description="Number of pages (PDF)")
    num_chunks: Optional[int] = Field(None, description="Number of text chunks")
    title: Optional[str] = Field(None, description="Document title")
    author: Optional[str] = Field(None, description="Document author")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123abc",
                "filename": "report.pdf",
                "file_type": "pdf",
                "file_size": 1024000,
                "status": "completed",
                "num_pages": 10,
                "num_chunks": 25
            }
        }


class DocumentChunk(BaseModel):
    """Document text chunk with metadata."""
    chunk_id: str = Field(..., description="Unique chunk ID")
    document_id: str = Field(..., description="Parent document ID")
    content: str = Field(..., description="Chunk text content")
    chunk_index: int = Field(..., description="Chunk index in document")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SummaryLength(str, Enum):
    """Summary length options."""
    BRIEF = "brief"
    STANDARD = "standard"
    DETAILED = "detailed"


class DocumentSummary(BaseModel):
    """Document summary response."""
    document_id: str = Field(..., description="Document ID")
    summary: str = Field(..., description="Generated summary")
    length: SummaryLength = Field(..., description="Summary length")
    method: str = Field(..., description="Summarization method used")
    num_chunks: Optional[int] = Field(None, description="Number of chunks processed")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123abc",
                "summary": "This document discusses quarterly financial results...",
                "length": "standard",
                "method": "single_pass",
                "generated_at": "2024-01-01T12:00:00Z"
            }
        }


class SummarizationRequest(BaseModel):
    """Request for document summarization."""
    document_id: Optional[str] = Field(None, description="Document ID to summarize")
    text: Optional[str] = Field(None, description="Direct text to summarize")
    length: SummaryLength = Field(default=SummaryLength.STANDARD)
    document_type: str = Field(default="general", description="Document type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123abc",
                "length": "standard",
                "document_type": "general"
            }
        }


class BatchSummarizationRequest(BaseModel):
    """Request for batch summarization."""
    document_ids: List[str] = Field(..., description="List of document IDs")
    length: SummaryLength = Field(default=SummaryLength.STANDARD)
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_ids": ["doc_123", "doc_456", "doc_789"],
                "length": "brief"
            }
        }


class DocumentListResponse(BaseModel):
    """Response for document listing."""
    documents: List[DocumentMetadata]
    total: int
    page: int
    page_size: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [],
                "total": 100,
                "page": 1,
                "page_size": 20
            }
        }
