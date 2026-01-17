"""
Helper utility functions
"""

import hashlib
from datetime import datetime
from typing import Any, Dict
import re


def generate_document_id(filename: str, content_hash: str = None) -> str:
    """
    Generate a unique document ID based on filename and optional content hash
    
    Args:
        filename: Name of the document file
        content_hash: Optional hash of document content
        
    Returns:
        Unique document identifier
    """
    timestamp = datetime.utcnow().isoformat()
    base_string = f"{filename}_{timestamp}"
    
    if content_hash:
        base_string += f"_{content_hash}"
    
    return hashlib.sha256(base_string.encode()).hexdigest()[:16]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing special characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove any character that isn't alphanumeric, dash, underscore, or dot
    sanitized = re.sub(r'[^\w\-.]', '_', filename)
    return sanitized


def calculate_file_hash(content: bytes) -> str:
    """
    Calculate SHA-256 hash of file content
    
    Args:
        content: File content as bytes
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(content).hexdigest()


def format_bytes(size: int) -> str:
    """
    Format bytes to human-readable size
    
    Args:
        size: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def create_metadata(
    document_id: str,
    filename: str,
    file_size: int,
    file_type: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create metadata dictionary for a document
    
    Args:
        document_id: Document identifier
        filename: Original filename
        file_size: File size in bytes
        file_type: File extension/type
        **kwargs: Additional metadata fields
        
    Returns:
        Metadata dictionary
    """
    metadata = {
        "document_id": document_id,
        "filename": filename,
        "file_size": file_size,
        "file_type": file_type,
        "created_at": datetime.utcnow().isoformat(),
        **kwargs
    }
    return metadata
