"""
Text splitter for intelligent document chunking.
"""
import logging
from typing import List, Optional, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

logger = logging.getLogger(__name__)


class DocumentTextSplitter:
    """
    Intelligent text splitter with configurable chunking strategy.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
        length_function: callable = len,
        separators: Optional[List[str]] = None,
    ):
        """
        Initialize text splitter.
        
        Args:
            chunk_size: Target size of each chunk (in characters/tokens)
            chunk_overlap: Number of characters to overlap between chunks
            length_function: Function to measure chunk length
            separators: List of separators for splitting (defaults to paragraph/sentence)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Default separators for semantic chunking
        if separators is None:
            separators = [
                "\n\n",  # Paragraphs
                "\n",    # Lines
                ". ",    # Sentences
                ", ",    # Clauses
                " ",     # Words
                "",      # Characters
            ]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=length_function,
            separators=separators,
        )

    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        try:
            chunks = self.splitter.split_text(text)
            logger.info(
                f"Split text into {len(chunks)} chunks "
                f"(size: {self.chunk_size}, overlap: {self.chunk_overlap})"
            )
            return chunks
        except Exception as e:
            logger.error(f"Error splitting text: {e}")
            raise

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks while preserving metadata.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Document objects with metadata
        """
        try:
            chunked_docs = self.splitter.split_documents(documents)
            
            # Add chunk metadata
            for i, doc in enumerate(chunked_docs):
                doc.metadata['chunk_id'] = i
                doc.metadata['chunk_size'] = len(doc.page_content)
            
            logger.info(
                f"Split {len(documents)} documents into {len(chunked_docs)} chunks"
            )
            
            return chunked_docs
            
        except Exception as e:
            logger.error(f"Error splitting documents: {e}")
            raise

    def split_document_with_metadata(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Document]:
        """
        Split a single text document into chunks with metadata.
        
        Args:
            text: Document text
            metadata: Document metadata to preserve
            
        Returns:
            List of chunked documents
        """
        try:
            # Create initial document
            doc = Document(page_content=text, metadata=metadata)
            
            # Split and preserve metadata
            chunks = self.split_documents([doc])
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting document with metadata: {e}")
            raise

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation).
        ~4 characters per token for English text.
        """
        return len(text) // 4

    def should_split(self, text: str) -> bool:
        """
        Check if text needs splitting based on chunk size.
        """
        return len(text) > self.chunk_size


class AdaptiveTextSplitter(DocumentTextSplitter):
    """
    Adaptive text splitter that adjusts chunk size based on content type.
    """

    def __init__(
        self,
        default_chunk_size: int = 1000,
        code_chunk_size: int = 500,
        table_chunk_size: int = 2000,
        chunk_overlap: int = 150,
    ):
        """
        Initialize adaptive splitter with different sizes for different content.
        
        Args:
            default_chunk_size: Default chunk size
            code_chunk_size: Chunk size for code
            table_chunk_size: Chunk size for tables (larger to preserve structure)
            chunk_overlap: Overlap between chunks
        """
        super().__init__(
            chunk_size=default_chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        self.code_splitter = RecursiveCharacterTextSplitter(
            chunk_size=code_chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        
        self.table_splitter = RecursiveCharacterTextSplitter(
            chunk_size=table_chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n"],
        )

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents adaptively based on content type.
        """
        all_chunks = []
        
        for doc in documents:
            # Detect content type
            content_type = self._detect_content_type(doc.page_content)
            
            # Choose appropriate splitter
            if content_type == 'code':
                chunks = self.code_splitter.split_documents([doc])
            elif content_type == 'table':
                chunks = self.table_splitter.split_documents([doc])
            else:
                chunks = self.splitter.split_documents([doc])
            
            # Add content type to metadata
            for chunk in chunks:
                chunk.metadata['content_type'] = content_type
            
            all_chunks.extend(chunks)
        
        logger.info(f"Adaptively split into {len(all_chunks)} chunks")
        
        return all_chunks

    def _detect_content_type(self, text: str) -> str:
        """
        Detect content type (code, table, or general text).
        """
        # Simple heuristics
        if '```' in text or text.count('\n    ') > 5:
            return 'code'
        elif '|' in text and text.count('|') > 10:
            return 'table'
        else:
            return 'general'


def create_text_splitter(
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
    adaptive: bool = False,
) -> DocumentTextSplitter:
    """
    Factory function to create text splitter.
    
    Args:
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks
        adaptive: Use adaptive splitter
        
    Returns:
        DocumentTextSplitter instance
    """
    if adaptive:
        return AdaptiveTextSplitter(
            default_chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    else:
        return DocumentTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
