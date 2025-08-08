"""LM Studio provider for LangChain integration."""

from langchain_openai import ChatOpenAI
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class LMStudioProvider:
    """Provider for LM Studio local models using OpenAI-compatible API."""
    
    def __init__(self, base_url: str, model_name: str, temperature: float = 0.7, max_tokens: int = 2000):
        """
        Initialize LM Studio provider.
        
        Args:
            base_url: LM Studio server URL (default: http://localhost:1234/v1)
            model_name: Name of the local model
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.base_url = base_url
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._llm = None
    
    def get_llm(self) -> ChatOpenAI:
        """Get or create the LLM instance."""
        if self._llm is None:
            try:
                self._llm = ChatOpenAI(
                    base_url=self.base_url,
                    api_key="lm-studio",  # LM Studio doesn't require a real API key
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                logger.info(f"Initialized LM Studio provider with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize LM Studio provider: {e}")
                raise
        
        return self._llm
    
    def test_connection(self) -> bool:
        """Test connection to LM Studio server."""
        try:
            llm = self.get_llm()
            # Try a simple test message
            response = llm.invoke("Hello")
            logger.info("LM Studio connection test successful")
            return True
        except Exception as e:
            logger.error(f"LM Studio connection test failed: {e}")
            return False
    
    def get_provider_info(self) -> dict:
        """Get provider information."""
        return {
            "name": "LM Studio",
            "base_url": self.base_url,
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
