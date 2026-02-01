"""
Pinecone vector database service for semantic search.
"""
import logging
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from langchain.schema import Document

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PineconeService:
    """
    Service for interacting with Pinecone vector database.
    """

    def __init__(
        self,
        index_name: Optional[str] = None,
        dimension: int = 1536,  # OpenAI ada-002 embedding dimension
        metric: str = "cosine",
    ):
        """
        Initialize Pinecone service.
        
        Args:
            index_name: Name of the Pinecone index
            dimension: Dimension of embeddings
            metric: Distance metric (cosine, euclidean, dotproduct)
        """
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = index_name or settings.PINECONE_INDEX_NAME
        self.dimension = dimension
        self.metric = metric
        self.index = None

    def create_index(self, delete_if_exists: bool = False):
        """
        Create a Pinecone index.
        
        Args:
            delete_if_exists: Delete existing index if it exists
        """
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes().names()
            
            if self.index_name in existing_indexes:
                if delete_if_exists:
                    logger.info(f"Deleting existing index: {self.index_name}")
                    self.pc.delete_index(self.index_name)
                else:
                    logger.info(f"Index {self.index_name} already exists")
                    self.index = self.pc.Index(self.index_name)
                    return
            
            # Create new index
            logger.info(f"Creating index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(
                    cloud=settings.PINECONE_CLOUD,
                    region=settings.PINECONE_REGION
                )
            )
            
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Created Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise

    def get_index(self):
        """Get or create index connection."""
        if self.index is None:
            try:
                self.index = self.pc.Index(self.index_name)
            except Exception as e:
                logger.error(f"Error connecting to index: {e}")
                raise
        return self.index

    def upsert(
        self,
        vectors: List[Dict[str, Any]],
        namespace: str = "",
        batch_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Upsert vectors to Pinecone.
        
        Args:
            vectors: List of vector dictionaries with id, values, and metadata
            namespace: Namespace for the vectors
            batch_size: Batch size for upserting
            
        Returns:
            Upsert statistics
        """
        try:
            index = self.get_index()
            
            # Batch upsert
            total_upserted = 0
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                response = index.upsert(
                    vectors=batch,
                    namespace=namespace
                )
                total_upserted += response.get('upserted_count', len(batch))
            
            logger.info(
                f"Upserted {total_upserted} vectors to namespace '{namespace}'"
            )
            
            return {
                "upserted_count": total_upserted,
                "namespace": namespace,
            }
            
        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            raise

    def query(
        self,
        query_vector: List[float],
        top_k: int = 5,
        namespace: str = "",
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Query Pinecone for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            namespace: Namespace to query
            filter: Metadata filter
            include_metadata: Include metadata in results
            
        Returns:
            List of matches with scores and metadata
        """
        try:
            index = self.get_index()
            
            response = index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=include_metadata,
            )
            
            matches = response.get('matches', [])
            
            logger.info(f"Found {len(matches)} matches in namespace '{namespace}'")
            
            return matches
            
        except Exception as e:
            logger.error(f"Error querying vectors: {e}")
            raise

    def delete(
        self,
        ids: Optional[List[str]] = None,
        delete_all: bool = False,
        namespace: str = "",
        filter: Optional[Dict[str, Any]] = None,
    ):
        """
        Delete vectors from Pinecone.
        
        Args:
            ids: List of vector IDs to delete
            delete_all: Delete all vectors in namespace
            namespace: Namespace to delete from
            filter: Metadata filter for deletion
        """
        try:
            index = self.get_index()
            
            if delete_all:
                index.delete(delete_all=True, namespace=namespace)
                logger.info(f"Deleted all vectors from namespace '{namespace}'")
            elif ids:
                index.delete(ids=ids, namespace=namespace)
                logger.info(f"Deleted {len(ids)} vectors from namespace '{namespace}'")
            elif filter:
                index.delete(filter=filter, namespace=namespace)
                logger.info(f"Deleted vectors with filter from namespace '{namespace}'")
            
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            raise

    def fetch(
        self,
        ids: List[str],
        namespace: str = ""
    ) -> Dict[str, Any]:
        """
        Fetch specific vectors by ID.
        
        Args:
            ids: List of vector IDs
            namespace: Namespace to fetch from
            
        Returns:
            Dictionary of vectors
        """
        try:
            index = self.get_index()
            response = index.fetch(ids=ids, namespace=namespace)
            
            logger.info(f"Fetched {len(ids)} vectors from namespace '{namespace}'")
            
            return response.get('vectors', {})
            
        except Exception as e:
            logger.error(f"Error fetching vectors: {e}")
            raise

    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Index statistics including vector count, dimension, etc.
        """
        try:
            index = self.get_index()
            stats = index.describe_index_stats()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            raise


def create_pinecone_service(
    index_name: Optional[str] = None,
    dimension: int = 1536,
) -> PineconeService:
    """
    Factory function to create Pinecone service.
    
    Args:
        index_name: Name of the index
        dimension: Embedding dimension
        
    Returns:
        PineconeService instance
    """
    return PineconeService(
        index_name=index_name,
        dimension=dimension,
    )
