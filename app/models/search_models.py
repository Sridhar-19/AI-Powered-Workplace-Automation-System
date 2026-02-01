"""
Pydantic models for search functionality.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class SearchQuery(BaseModel):
    """Search query request."""
    query: str = Field(..., description="Search query text", min_length=1)
    top_k: int = Field(default=5, description="Number of results to return", ge=1, le=50)
    namespace: str = Field(default="", description="Pinecone namespace")
    filter: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    include_metadata: bool = Field(default=True, description="Include metadata in results")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What were the Q4 revenue targets?",
                "top_k": 5,
                "include_metadata": True
            }
        }


class SearchResult(BaseModel):
    """Single search result."""
    document_id: str = Field(..., description="Document ID")
    score: float = Field(..., description="Similarity score")
    text: str = Field(..., description="Matched text content")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123",
                "score": 0.85,
                "text": "Q4 revenue targets were set at $2.5M...",
                "metadata": {"source": "report.pdf", "page": 3}
            }
        }


class SearchResponse(BaseModel):
    """Search response with multiple results."""
    query: str = Field(..., description="Original query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    search_time_ms: float = Field(..., description="Search time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "revenue targets",
                "results": [],
                "total_results": 5,
                "search_time_ms": 145.2
            }
        }


class SimilarDocumentRequest(BaseModel):
    """Request to find similar documents."""
    document_id: str = Field(..., description="Document ID to find similar documents for")
    top_k: int = Field(default=5, description="Number of similar documents", ge=1, le=20)
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123",
                "top_k": 5
            }
        }
