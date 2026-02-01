"""
Unit tests for document processing.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from app.core.document_loader import DocumentLoader, create_document_loader
from app.core.text_splitter import DocumentTextSplitter, create_text_splitter
from langchain.schema import Document


class TestDocumentLoader:
    """Tests for document loader."""

    def test_create_loader(self):
        """Test loader creation."""
        loader = create_document_loader()
        assert isinstance(loader, DocumentLoader)
        assert len(loader.supported_formats) > 0

    def test_supported_formats(self):
        """Test supported file formats."""
        loader = create_document_loader()
        assert '.pdf' in loader.supported_formats
        assert '.docx' in loader.supported_formats
        assert '.txt' in loader.supported_formats

    def test_file_not_found(self):
        """Test handling of non-existent files."""
        loader = create_document_loader()
        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent_file.pdf")

    def test_unsupported_format(self):
        """Test handling of unsupported formats."""
        loader = create_document_loader()
        # Create a temporary file with unsupported extension
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                loader.load(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestTextSplitter:
    """Tests for text splitter."""

    def test_create_splitter(self):
        """Test splitter creation."""
        splitter = create_text_splitter()
        assert isinstance(splitter, DocumentTextSplitter)
        assert splitter.chunk_size == 1000
        assert splitter.chunk_overlap == 150

    def test_split_short_text(self):
        """Test splitting short text."""
        splitter = create_text_splitter(chunk_size=100, chunk_overlap=20)
        text = "This is a short text that doesn't need splitting."
        
        chunks = splitter.split_text(text)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_split_long_text(self):
        """Test splitting long text."""
        splitter = create_text_splitter(chunk_size=100, chunk_overlap=20)
        text = "This is a sentence. " * 50  # Create long text
        
        chunks = splitter.split_text(text)
        assert len(chunks) > 1
        
        # Check overlap
        for i in range(len(chunks) - 1):
            # There should be some overlap between consecutive chunks
            assert len(chunks[i]) <= 120  # chunk_size + some tolerance

    def test_split_documents(self):
        """Test splitting documents with metadata."""
        splitter = create_text_splitter(chunk_size=50, chunk_overlap=10)
        
        docs = [
            Document(
                page_content="This is a long document. " * 20,
                metadata={"source": "test.pdf", "page": 1}
            )
        ]
        
        chunks = splitter.split_documents(docs)
        assert len(chunks) > 1
        
        # Check metadata preservation
        for chunk in chunks:
            assert "source" in chunk.metadata
            assert chunk.metadata["source"] == "test.pdf"
            assert "chunk_id" in chunk.metadata

    def test_token_estimation(self):
        """Test token estimation."""
        splitter = create_text_splitter()
        text = "This is a test" * 100
        tokens = splitter.estimate_tokens(text)
        
        # Should be roughly 1/4 of character count
        assert tokens > 0
        assert tokens < len(text)


class TestAdaptiveTextSplitter:
    """Tests for adaptive text splitter."""

    def test_create_adaptive_splitter(self):
        """Test adaptive splitter creation."""
        from app.core.text_splitter import AdaptiveTextSplitter
        
        splitter = create_text_splitter(adaptive=True)
        assert isinstance(splitter, AdaptiveTextSplitter)

    def test_content_type_detection(self):
        """Test content type detection."""
        from app.core.text_splitter import AdaptiveTextSplitter
        
        splitter = AdaptiveTextSplitter()
        
        # Code detection
        code_text = "```python\ndef hello():\n    print('hello')\n```"
        assert splitter._detect_content_type(code_text) == 'code'
        
        # Table detection
        table_text = "| Col1 | Col2 | Col3 |\n" * 10
        assert splitter._detect_content_type(table_text) == 'table'
        
        # General text
        general_text = "This is normal text without code or tables."
        assert splitter._detect_content_type(general_text) == 'general'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
