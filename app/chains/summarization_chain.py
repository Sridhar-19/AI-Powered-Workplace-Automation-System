"""
LangChain chain for document summarization.
"""
import logging
from typing import Dict, Any, Optional, List
from langchain.chains import LLMChain, MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from app.config import get_settings
from app.prompts.summary_prompts import (
    get_summary_prompt,
    map_summary_prompt,
    reduce_summary_prompt,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class SummarizationChain:
    """
    Chain for document summarization with support for different summary lengths
    and long document handling via map-reduce.
    """

    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.3,
        max_tokens: int = 1000,
    ):
        """
        Initialize the summarization chain.
        
        Args:
            model: OpenAI model to use
            temperature: Sampling temperature (lower = more focused)
            max_tokens: Maximum tokens for summary
        """
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=settings.OPENAI_API_KEY,
        )
        self.max_doc_length = 4000  # tokens

    def summarize(
        self,
        text: str,
        length: str = "standard",
        document_type: str = "general",
    ) -> Dict[str, Any]:
        """
        Summarize a document.
        
        Args:
            text: Document text to summarize
            length: Summary length ('brief', 'standard', 'detailed')
            document_type: Type of document ('general', 'technical', 'few-shot')
            
        Returns:
            Dictionary with summary and metadata
        """
        try:
            # Get appropriate prompt
            prompt = get_summary_prompt(length, document_type)
            
            # Check if document is too long for single pass
            if self._estimate_tokens(text) > self.max_doc_length:
                logger.info("Document too long, using map-reduce summarization")
                return self._map_reduce_summarize(text)
            
            # Create chain
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Generate summary
            result = chain.invoke({"text": text})
            
            summary = result.get("text", "").strip()
            
            logger.info(f"Generated {length} summary, length: {len(summary)} chars")
            
            return {
                "summary": summary,
                "length": length,
                "document_type": document_type,
                "method": "single_pass",
            }
            
        except Exception as e:
            logger.error(f"Error in summarization: {e}")
            raise

    def _map_reduce_summarize(self, text: str) -> Dict[str, Any]:
        """
        Summarize a long document using map-reduce strategy.
        
        Args:
            text: Long document text
            
        Returns:
            Dictionary with summary and metadata
        """
        try:
            # Split the document
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=3000,
                chunk_overlap=200,
            )
            chunks = text_splitter.split_text(text)
            docs = [Document(page_content=chunk) for chunk in chunks]
            
            logger.info(f"Split document into {len(docs)} chunks for map-reduce")
            
            # Map chain - summarize each chunk
            map_chain = LLMChain(llm=self.llm, prompt=map_summary_prompt)
            
            # Reduce chain - combine summaries
            reduce_chain = LLMChain(llm=self.llm, prompt=reduce_summary_prompt)
            
            # Create the combine documents chain
            combine_documents_chain = StuffDocumentsChain(
                llm_chain=reduce_chain,
                document_variable_name="text",
            )
            
            # Reduce documents chain
            reduce_documents_chain = ReduceDocumentsChain(
                combine_documents_chain=combine_documents_chain,
                collapse_documents_chain=combine_documents_chain,
                token_max=4000,
            )
            
            # Full map-reduce chain
            map_reduce_chain = MapReduceDocumentsChain(
                llm_chain=map_chain,
                reduce_documents_chain=reduce_documents_chain,
                document_variable_name="text",
                return_intermediate_steps=False,
            )
            
            # Execute
            result = map_reduce_chain.invoke({"input_documents": docs})
            
            summary = result.get("output_text", "").strip()
            
            logger.info(f"Generated map-reduce summary, length: {len(summary)} chars")
            
            return {
                "summary": summary,
                "length": "standard",
                "document_type": "general",
                "method": "map_reduce",
                "num_chunks": len(docs),
            }
            
        except Exception as e:
            logger.error(f"Error in map-reduce summarization: {e}")
            raise

    def batch_summarize(
        self,
        texts: List[str],
        length: str = "standard",
        document_type: str = "general",
    ) -> List[Dict[str, Any]]:
        """
        Summarize multiple documents.
        
        Args:
            texts: List of document texts
            length: Summary length
            document_type: Type of documents
            
        Returns:
            List of summary dictionaries
        """
        summaries = []
        for i, text in enumerate(texts):
            try:
                logger.info(f"Summarizing document {i+1}/{len(texts)}")
                summary = self.summarize(text, length, document_type)
                summaries.append(summary)
            except Exception as e:
                logger.error(f"Error summarizing document {i+1}: {e}")
                summaries.append({
                    "summary": "",
                    "error": str(e),
                    "length": length,
                    "document_type": document_type,
                })
        
        return summaries

    def _estimate_tokens(self, text: str) -> int:
        """
        Rough estimation of token count.
        ~4 characters per token is a reasonable approximation.
        """
        return len(text) // 4


def create_summarization_chain(
    model: str = "gpt-4-turbo-preview",
    temperature: float = 0.3,
    max_tokens: int = 1000,
) -> SummarizationChain:
    """
    Factory function to create a summarization chain.
    
    Args:
        model: OpenAI model to use
        temperature: Sampling temperature
        max_tokens: Maximum tokens for summary
        
    Returns:
        SummarizationChain instance
    """
    return SummarizationChain(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
