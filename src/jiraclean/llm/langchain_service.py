"""
LangChain Service Wrapper.

This module provides a unified interface for LLM calls using LangChain,
maintaining the same API as the current implementation while enabling
multi-provider support.
"""

import logging
from typing import Dict, Any, Optional
from langchain_core.language_models.base import BaseLanguageModel

from .langchain_factory import create_llm, LangChainFactoryError

logger = logging.getLogger(__name__)


class LangChainServiceError(Exception):
    """Exception raised by LangChain service operations."""
    pass


class LangChainLLMService:
    """
    LangChain-based LLM service that maintains compatibility with existing API.
    
    This service wraps LangChain LLM instances and provides the same interface
    as the current HTTP-based implementation, enabling seamless migration.
    """
    
    def __init__(self, provider: str, model: str, config: Dict[str, Any]):
        """
        Initialize LangChain LLM service.
        
        Args:
            provider: LLM provider name (e.g., 'ollama')
            model: Model name (e.g., 'llama3.2:latest')
            config: Provider-specific configuration
            
        Raises:
            LangChainServiceError: If LLM creation fails
        """
        self.provider = provider
        self.model = model
        self.config = config
        
        try:
            self.llm = create_llm(provider, model, config)
            logger.info(f"LangChain LLM service initialized: {provider}/{model}")
        except LangChainFactoryError as e:
            logger.error(f"Failed to initialize LangChain LLM service: {e}")
            raise LangChainServiceError(f"Failed to initialize LLM service: {e}") from e
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate response from LLM using the provided prompt.
        
        This method maintains the same API as the current implementation,
        ensuring seamless migration from HTTP-based calls.
        
        Args:
            prompt: Input prompt for the LLM
            
        Returns:
            Generated response text
            
        Raises:
            LangChainServiceError: If response generation fails
        """
        try:
            logger.debug(f"Generating response with {self.provider}/{self.model}")
            
            # Use LangChain's invoke method for response generation
            response = self.llm.invoke(prompt)
            
            # Handle different response types from different LLM providers
            if isinstance(response, str):
                return response
            elif hasattr(response, 'content'):
                # Chat models return AIMessage objects with content
                return response.content
            else:
                # Fallback: convert to string
                return str(response)
                
        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            raise LangChainServiceError(f"Failed to generate response: {e}") from e
    
    def validate_connection(self) -> bool:
        """
        Test LLM connection with a simple prompt.
        
        Returns:
            True if connection is working, False otherwise
        """
        try:
            test_prompt = "Hello"
            response = self.generate_response(test_prompt)
            
            # Check if we got a reasonable response
            if response and len(response.strip()) > 0:
                logger.info(f"LLM connection validated: {self.provider}/{self.model}")
                return True
            else:
                logger.warning(f"LLM connection test returned empty response")
                return False
                
        except Exception as e:
            logger.error(f"LLM connection validation failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the current LLM provider and configuration.
        
        Returns:
            Dictionary with provider information
        """
        return {
            'provider': self.provider,
            'model': self.model,
            'config': {k: v for k, v in self.config.items() if k != 'api_key'},  # Exclude sensitive data
            'llm_type': type(self.llm).__name__
        }


def create_langchain_service(provider: str, model: str, config: Dict[str, Any]) -> LangChainLLMService:
    """
    Create LangChain LLM service instance.
    
    Convenience function for creating LangChain service instances.
    
    Args:
        provider: LLM provider name (e.g., 'ollama')
        model: Model name (e.g., 'llama3.2:latest')
        config: Provider-specific configuration
        
    Returns:
        LangChain LLM service instance
        
    Raises:
        LangChainServiceError: If service creation fails
    """
    return LangChainLLMService(provider, model, config)
