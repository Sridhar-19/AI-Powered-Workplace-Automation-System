"""
Embeddings service for generating and caching vector embeddings.
"""
import logging
import hashlib
import json
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EmbeddingsService:
    """
    Service for generating embeddings with caching support.
    """

    def __init__(
        self,
        model: str = "text-embedding-ada-002",
        batch_size: int = 100,
        use_cache: bool = True,
    ):
        """
        Initialize embeddings service.
        
        Args:
            model: OpenAI embedding model
            batch_size: Batch size for embedding generation
            use_cache: Enable caching
        """
        self.embeddings = OpenAIEmbeddings(
            model=model,
            openai_api_key=settings.OPENAI_API_KEY,
        )
        self.batch_size = batch_size
        self.use_cache = use_cache
        self.cache: Dict[str, List[float]] = {}

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text."""
        return hashlib.md5(text.encode()).hexdigest()

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # Check cache
            if self.use_cache:
                cache_key = self._get_cache_key(text)
                if cache_key in self.cache:
                    logger.debug("Cache hit for embedding")
                    return self.cache[cache_key]
            
            # Generate embedding
            embedding = self.embeddings.embed_query(text)
            
            # Cache result
            if self.use_cache:
                self.cache[cache_key] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with batching.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            cache_hits = 0
            texts_to_embed = []
            text_indices = []
            
            # Check cache for each text
            if self.use_cache:
                for i, text in enumerate(texts):
                    cache_key = self._get_cache_key(text)
                    if cache_key in self.cache:
                        embeddings.append(self.cache[cache_key])
                        cache_hits += 1
                    else:
                        texts_to_embed.append(text)
                        text_indices.append(i)
                        embeddings.append(None)  # Placeholder
            else:
                texts_to_embed = texts
                text_indices = list(range(len(texts)))
                embeddings = [None] * len(texts)
            
            # Generate embeddings for uncached texts in batches
            if texts_to_embed:
                for i in range(0, len(texts_to_embed), self.batch_size):
                    batch = texts_to_embed[i:i + self.batch_size]
                    batch_embeddings = self.embeddings.embed_documents(batch)
                    
                    # Store in results and cache
                    for j, embedding in enumerate(batch_embeddings):
                        idx = text_indices[i + j]
                        embeddings[idx] = embedding
                        
                        if self.use_cache:
                            cache_key = self._get_cache_key(texts[idx])
                            self.cache[cache_key] = embedding
            
            logger.info(
                f"Generated {len(texts_to_embed)} embeddings, "
                f"{cache_hits} cache hits"
            )
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def embed_documents(
        self,
        documents: List[Document]
    ) -> List[Dict[str, Any]]:
        """
        Generate embeddings for documents and prepare for Pinecone.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of vectors ready for Pinecone upsert
        """
        try:
            # Extract texts
            texts = [doc.page_content for doc in documents]
            
            # Generate embeddings
            embeddings = self.embed_texts(texts)
            
            # Prepare vectors for Pinecone
            vectors = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                vector = {
                    "id": doc.metadata.get("id", f"doc_{i}"),
                    "values": embedding,
                    "metadata": {
                        **doc.metadata,
                        "text": doc.page_content[:1000],  # Store first 1000 chars
                    }
                }
                vectors.append(vector)
            
            logger.info(f"Prepared {len(vectors)} vectors for Pinecone")
            
            return vectors
            
        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
            raise

    def clear_cache(self):
        """Clear embedding cache."""
        self.cache.clear()
        logger.info("Cleared embedding cache")

    def get_cache_size(self) -> int:
        """Get number of cached embeddings."""
        return len(self.cache)

    def save_cache(self, filepath: str):
        """
        Save cache to file.
        
        Args:
            filepath: Path to save cache
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.cache, f)
            logger.info(f"Saved embedding cache to {filepath}")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
            raise

    def load_cache(self, filepath: str):
        """
        Load cache from file.
        
        Args:
            filepath: Path to load cache from
        """
        try:
            with open(filepath, 'r') as f:
                self.cache = json.load(f)
            logger.info(f"Loaded {len(self.cache)} embeddings from {filepath}")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            raise


def create_embeddings_service(
    model: str = "text-embedding-ada-002",
    use_cache: bool = True,
) -> EmbeddingsService:
    """
    Factory function to create embeddings service.
    
    Args:
        model: Embedding model to use
        use_cache: Enable caching
        
    Returns:
        EmbeddingsService instance
    """
    return EmbeddingsService(
        model=model,
        use_cache=use_cache,
    )
