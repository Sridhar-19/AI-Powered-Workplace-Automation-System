"""
OpenAI client with error handling, retry logic, and rate limiting.
"""
import time
from typing import Optional, Dict, Any, List
from functools import wraps
import logging
from openai import OpenAI, AsyncOpenAI
from openai import RateLimitError, APIError, APIConnectionError, APITimeoutError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class OpenAIClientWrapper:
    """
    Wrapper for OpenAI client with built-in error handling and retry logic.
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.async_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.total_tokens_used = 0
        self.total_cost = 0.0
        
        # Cost per 1K tokens (as of 2024)
        self.pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "text-embedding-ada-002": {"input": 0.0001, "output": 0.0},
        }

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage."""
        if model not in self.pricing:
            # Use GPT-4 pricing as default for unknown models
            model = "gpt-4"
        
        pricing = self.pricing[model]
        cost = (input_tokens / 1000 * pricing["input"]) + (output_tokens / 1000 * pricing["output"])
        return cost

    def _update_usage_stats(self, usage: Dict[str, Any], model: str):
        """Update usage statistics."""
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        
        self.total_tokens_used += total_tokens
        cost = self._calculate_cost(model, input_tokens, output_tokens)
        self.total_cost += cost
        
        logger.info(
            f"OpenAI API call - Model: {model}, "
            f"Input: {input_tokens} tokens, Output: {output_tokens} tokens, "
            f"Cost: ${cost:.4f}, Total cost: ${self.total_cost:.4f}"
        )

    @retry(
        retry=retry_if_exception_type(
            (RateLimitError, APIConnectionError, APITimeoutError)
        ),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a chat completion with retry logic.
        
        Args:
            messages: List of message dictionaries
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters for the API call
            
        Returns:
            API response with completion
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            
            # Update usage statistics
            if hasattr(response, "usage") and response.usage:
                self._update_usage_stats(response.usage.model_dump(), model)
            
            return {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "finish_reason": response.choices[0].finish_reason,
                "usage": response.usage.model_dump() if response.usage else {},
            }
            
        except RateLimitError as e:
            logger.warning(f"Rate limit hit, retrying... Error: {e}")
            raise
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in chat completion: {e}")
            raise

    @retry(
        retry=retry_if_exception_type(
            (RateLimitError, APIConnectionError, APITimeoutError)
        ),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def async_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Async version of chat_completion.
        """
        try:
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            
            # Update usage statistics
            if hasattr(response, "usage") and response.usage:
                self._update_usage_stats(response.usage.model_dump(), model)
            
            return {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "finish_reason": response.choices[0].finish_reason,
                "usage": response.usage.model_dump() if response.usage else {},
            }
            
        except RateLimitError as e:
            logger.warning(f"Rate limit hit, retrying... Error: {e}")
            raise
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in async chat completion: {e}")
            raise

    @retry(
        retry=retry_if_exception_type(
            (RateLimitError, APIConnectionError, APITimeoutError)
        ),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def create_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-ada-002",
    ) -> List[List[float]]:
        """
        Create embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            model: Embedding model to use
            
        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=model,
                input=texts,
            )
            
            # Update usage statistics
            if hasattr(response, "usage") and response.usage:
                self._update_usage_stats(response.usage.model_dump(), model)
            
            # Extract embeddings in order
            embeddings = [item.embedding for item in response.data]
            
            logger.info(f"Created {len(embeddings)} embeddings using {model}")
            return embeddings
            
        except RateLimitError as e:
            logger.warning(f"Rate limit hit while creating embeddings, retrying... Error: {e}")
            raise
        except APIError as e:
            logger.error(f"OpenAI API error while creating embeddings: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating embeddings: {e}")
            raise

    async def async_create_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-ada-002",
    ) -> List[List[float]]:
        """
        Async version of create_embeddings.
        """
        try:
            response = await self.async_client.embeddings.create(
                model=model,
                input=texts,
            )
            
            # Update usage statistics
            if hasattr(response, "usage") and response.usage:
                self._update_usage_stats(response.usage.model_dump(), model)
            
            # Extract embeddings in order
            embeddings = [item.embedding for item in response.data]
            
            logger.info(f"Created {len(embeddings)} embeddings using {model}")
            return embeddings
            
        except RateLimitError as e:
            logger.warning(f"Rate limit hit while creating embeddings, retrying... Error: {e}")
            raise
        except APIError as e:
            logger.error(f"OpenAI API error while creating embeddings: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating embeddings: {e}")
            raise

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        return {
            "total_tokens": self.total_tokens_used,
            "total_cost": round(self.total_cost, 4),
        }

    def reset_usage_stats(self):
        """Reset usage statistics."""
        self.total_tokens_used = 0
        self.total_cost = 0.0


# Global client instance
_openai_client: Optional[OpenAIClientWrapper] = None


def get_openai_client() -> OpenAIClientWrapper:
    """Get or create the global OpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClientWrapper()
    return _openai_client
