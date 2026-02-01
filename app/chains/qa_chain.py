"""
LangChain chain for question-answering (QA) with retrieval.
This will be enhanced with Pinecone integration in Phase 3.
"""
import logging
from typing import Dict, Any, List, Optional
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.schema import Document

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# QA prompt template
QA_PROMPT_TEMPLATE = """You are a helpful AI assistant that answers questions based on the provided context.

Use the following pieces of context to answer the question at the end. If you don't know the answer based on the context, say "I don't have enough information to answer that question."

Always cite the source of your information when possible.

Context:
{context}

Question: {question}

Answer:"""

qa_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=QA_PROMPT_TEMPLATE,
)


# QA with sources template
QA_WITH_SOURCES_TEMPLATE = """You are a helpful AI assistant that answers questions based on provided context and always cites sources.

Use the following pieces of context to answer the question. Each piece of context has a source identifier.

For your answer:
1. Provide a clear, concise answer to the question
2. Cite which sources (by ID) you used
3. If the context doesn't contain enough information, say so

Context:
{context}

Question: {question}

Answer (with source citations):"""

qa_with_sources_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=QA_WITH_SOURCES_TEMPLATE,
)


# Conversational QA template (with memory)
CONVERSATIONAL_QA_TEMPLATE = """You are a helpful AI assistant having a conversation with a human.

Use the following pieces of context and conversation history to answer the current question.

Conversation History:
{chat_history}

Context:
{context}

Current Question: {question}

Answer:"""

conversational_qa_prompt = PromptTemplate(
    input_variables=["chat_history", "context", "question"],
    template=CONVERSATIONAL_QA_TEMPLATE,
)


class QAChain:
    """
    Question-answering chain with support for context-based responses.
    Will be enhanced with vector retrieval in Phase 3.
    """

    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.2,
        max_tokens: int = 500,
    ):
        """
        Initialize the QA chain.
        
        Args:
            model: OpenAI model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens for answer
        """
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=settings.OPENAI_API_KEY,
        )
        self.chat_history: List[Dict[str, str]] = []

    def answer_question(
        self,
        question: str,
        context: str,
        include_sources: bool = False,
    ) -> Dict[str, Any]:
        """
        Answer a question based on provided context.
        
        Args:
            question: User's question
            context: Relevant context to answer the question
            include_sources: Whether to include source citations
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Choose appropriate prompt
            prompt = qa_with_sources_prompt if include_sources else qa_prompt
            
            # Create chain
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Generate answer
            result = chain.invoke({
                "context": context,
                "question": question,
            })
            
            answer = result.get("text", "").strip()
            
            logger.info(f"Answered question, length: {len(answer)} chars")
            
            return {
                "answer": answer,
                "question": question,
                "sources_included": include_sources,
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise

    def answer_with_conversation_history(
        self,
        question: str,
        context: str,
        update_history: bool = True,
    ) -> Dict[str, Any]:
        """
        Answer a question with conversation history for context.
        
        Args:
            question: User's question
            context: Relevant context
            update_history: Whether to add this Q&A to history
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Format chat history
            chat_history_str = "\n".join([
                f"Q: {item['question']}\nA: {item['answer']}"
                for item in self.chat_history[-5:]  # Last 5 exchanges
            ])
            
            if not chat_history_str:
                chat_history_str = "No previous conversation."
            
            # Create chain
            chain = LLMChain(llm=self.llm, prompt=conversational_qa_prompt)
            
            # Generate answer
            result = chain.invoke({
                "chat_history": chat_history_str,
                "context": context,
                "question": question,
            })
            
            answer = result.get("text", "").strip()
            
            # Update history if requested
            if update_history:
                self.chat_history.append({
                    "question": question,
                    "answer": answer,
                })
            
            logger.info(
                f"Answered conversational question, "
                f"history length: {len(self.chat_history)}"
            )
            
            return {
                "answer": answer,
                "question": question,
                "conversation_turns": len(self.chat_history),
            }
            
        except Exception as e:
            logger.error(f"Error in conversational QA: {e}")
            raise

    def answer_from_documents(
        self,
        question: str,
        documents: List[Document],
        include_sources: bool = True,
    ) -> Dict[str, Any]:
        """
        Answer a question from a list of documents.
        
        Args:
            question: User's question
            documents: List of Document objects with content and metadata
            include_sources: Whether to include source citations
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Format documents as context
            context_parts = []
            for i, doc in enumerate(documents):
                source = doc.metadata.get("source", f"Document {i+1}")
                context_parts.append(f"[Source {i+1}: {source}]\n{doc.page_content}")
            
            context = "\n\n".join(context_parts)
            
            # Answer the question
            result = self.answer_question(question, context, include_sources)
            
            # Add document metadata
            result["num_documents"] = len(documents)
            result["sources"] = [
                doc.metadata.get("source", f"Document {i+1}")
                for i, doc in enumerate(documents)
            ]
            
            return result
            
        except Exception as e:
            logger.error(f"Error answering from documents: {e}")
            raise

    def clear_history(self):
        """Clear conversation history."""
        self.chat_history = []
        logger.info("Cleared conversation history")

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.chat_history.copy()


def create_qa_chain(
    model: str = "gpt-4-turbo-preview",
    temperature: float = 0.2,
    max_tokens: int = 500,
) -> QAChain:
    """
    Factory function to create a QA chain.
    
    Args:
        model: OpenAI model to use
        temperature: Sampling temperature
        max_tokens: Maximum tokens for answer
        
    Returns:
        QAChain instance
    """
    return QAChain(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
