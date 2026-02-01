"""
Search service for semantic search.
"""
import logging
import time
from typing import List, Dict, Any

from app.core.pinecone_service import create_pinecone_service
from app.core.embeddings_service import create_embeddings_service
from app.chains.qa_chain import create_qa_chain
from app.models.search_models import SearchResult
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SearchService:
    """Service for semantic search operations."""

    def __init__(self):
        self.pinecone_service = create_pinecone_service()
        self.embeddings_service = create_embeddings_service()
        self.qa_chain = create_qa_chain()

    async def search(
        self,
        query: str,
        top_k: int = 5,
        namespace: str = "",
        filter: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Perform semantic search.
        
        Args:
            query: Search query
            top_k: Number of results
            namespace: Pinecone namespace
            filter: Metadata filters
            
        Returns:
            Search results with timing
        """
        try:
            start_time = time.time()
            
            # Generate query embedding
            query_embedding = self.embeddings_service.embed_text(query)
            
            # Search in Pinecone
            matches = self.pinecone_service.query(
                query_vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=True
            )
            
            # Format results
            results = []
            for match in matches:
                result = SearchResult(
                    document_id=match.get('id', ''),
                    score=match.get('score', 0.0),
                    text=match.get('metadata', {}).get('text', ''),
                    metadata=match.get('metadata', {})
                )
                results.append(result)
            
            search_time_ms = (time.time() - start_time) * 1000
            
            logger.info(f"Search completed: {len(results)} results in {search_time_ms:.2f}ms")
            
            return {
                "query": query,
                "results": results,
                "total_results": len(results),
                "search_time_ms": search_time_ms
            }
            
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            raise

    async def search_with_answer(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Search and generate answer using RAG.
        
        Args:
            query: Search query
            top_k: Number of results to retrieve
            
        Returns:
            Search results with generated answer
        """
        try:
            # Perform search
            search_results = await self.search(query, top_k)
            
            # Prepare context from search results
            context_parts = []
            for i, result in enumerate(search_results["results"]):
                context_parts.append(
                    f"[Source {i+1}] {result.text}"
                )
            
            context = "\n\n".join(context_parts)
            
            # Generate answer
            answer_result = self.qa_chain.answer_question(
                question=query,
                context=context,
                include_sources=True
            )
            
            return {
                **search_results,
                "answer": answer_result["answer"]
            }
            
        except Exception as e:
            logger.error(f"Error in search with answer: {e}")
            raise

    async def find_similar_documents(
        self,
        document_id: str,
        top_k: int = 5
    ) -> List[SearchResult]:
        """
        Find documents similar to a given document.
        
        Args:
            document_id: Source document ID
            top_k: Number of similar documents
            
        Returns:
            List of similar documents
        """
        try:
            # Fetch document vectors from Pinecone
            vectors = self.pinecone_service.fetch([document_id])
            
            if not vectors:
                raise ValueError(f"Document {document_id} not found")
            
            # Get the embedding
            doc_vector = vectors[document_id]['values']
            
            # Search for similar vectors
            matches = self.pinecone_service.query(
                query_vector=doc_vector,
                top_k=top_k + 1,  # +1 to exclude the document itself
                include_metadata=True
            )
            
            # Filter out the source document and format results
            results = []
            for match in matches:
                if match['id'] != document_id:
                    result = SearchResult(
                        document_id=match['id'],
                        score=match['score'],
                        text=match.get('metadata', {}).get('text', ''),
                        metadata=match.get('metadata', {})
                    )
                    results.append(result)
            
            logger.info(f"Found {len(results)} similar documents to {document_id}")
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error finding similar documents: {e}")
            raise


# Global service instance
_search_service = None


def get_search_service() -> SearchService:
    """Get or create search service instance."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
