"""
LangChain LLM Factory for Multi-Provider Support.

This module provides a factory pattern for creating LangChain LLM instances
for different providers. Starts with Ollama support following KISS principles.
"""

import logging
from typing import Dict, Any, List, Optional
from langchain_core.language_models.base import BaseLanguageModel

# Import LangChain provider modules with proper error handling
try:
    from langchain_ollama import OllamaLLM
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    OllamaLLM = None

logger = logging.getLogger(__name__)


class LangChainFactoryError(Exception):
    """Exception raised by LangChain factory operations."""
    pass


class LangChainFactory:
    """Factory for creating LangChain LLM instances."""
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Get list of available LLM providers.
        
        Returns:
            List of provider names that are available (dependencies installed)
        """
        available = []
        
        if OLLAMA_AVAILABLE:
            available.append('ollama')
        
        # Future providers will be added here as they're implemented
        # if OPENAI_AVAILABLE:
        #     available.append('openai')
        
        return available
    
    @classmethod
    def validate_provider_config(cls, provider: str, config: Dict[str, Any]) -> bool:
        """
        Validate provider-specific configuration.
        
        Args:
            provider: Provider name (e.g., 'ollama')
            config: Provider configuration dictionary
            
        Returns:
            True if configuration is valid, False otherwise
        """
        if provider == 'ollama':
            return cls._validate_ollama_config(config)
        else:
            logger.error(f"Unsupported provider: {provider}")
            return False
    
    @classmethod
    def create_llm(cls, provider: str, model: str, config: Dict[str, Any]) -> BaseLanguageModel:
        """
        Create LangChain LLM instance for specified provider.
        
        Args:
            provider: Provider name (currently only 'ollama' supported)
            model: Model name (e.g., 'llama3.2:latest')
            config: Provider-specific configuration
            
        Returns:
            LangChain LLM instance
            
        Raises:
            LangChainFactoryError: If provider is unsupported or configuration is invalid
        """
        if not cls.validate_provider_config(provider, config):
            raise LangChainFactoryError(f"Invalid configuration for provider '{provider}'")
        
        try:
            if provider == 'ollama':
                return cls._create_ollama_llm(model, config)
            else:
                raise LangChainFactoryError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            logger.error(f"Failed to create LLM for provider '{provider}': {e}")
            raise LangChainFactoryError(f"Failed to create LLM: {e}") from e
    
    @classmethod
    def _validate_ollama_config(cls, config: Dict[str, Any]) -> bool:
        """Validate Ollama-specific configuration."""
        if not OLLAMA_AVAILABLE:
            logger.error("Ollama provider not available - dependency not installed")
            return False
        
        base_url = config.get('base_url', 'http://localhost:11434')
        if not isinstance(base_url, str):
            logger.error("Ollama base_url must be a string")
            return False
        
        return True
    
    @classmethod
    def _create_ollama_llm(cls, model: str, config: Dict[str, Any]) -> BaseLanguageModel:
        """Create Ollama LLM instance."""
        if not OLLAMA_AVAILABLE or OllamaLLM is None:
            raise LangChainFactoryError("Ollama provider not available - dependency not installed")
        
        base_url = config.get('base_url', 'http://localhost:11434')
        temperature = config.get('temperature', 0.7)
        
        logger.info(f"Creating Ollama LLM: model={model}, base_url={base_url}")
        
        # Create OllamaLLM with minimal required parameters
        return OllamaLLM(
            model=model,
            base_url=base_url,
            temperature=temperature,
        )


# Convenience functions for direct use
def create_llm(provider: str, model: str, config: Dict[str, Any]) -> BaseLanguageModel:
    """
    Create LangChain LLM instance for specified provider.
    
    Convenience function that delegates to LangChainFactory.create_llm().
    
    Args:
        provider: Provider name (currently only 'ollama' supported)
        model: Model name (e.g., 'llama3.2:latest')
        config: Provider-specific configuration
        
    Returns:
        LangChain LLM instance
    """
    return LangChainFactory.create_llm(provider, model, config)


def get_available_providers() -> List[str]:
    """
    Get list of available LLM providers.
    
    Convenience function that delegates to LangChainFactory.get_available_providers().
    
    Returns:
        List of provider names that are available
    """
    return LangChainFactory.get_available_providers()


def validate_provider_config(provider: str, config: Dict[str, Any]) -> bool:
    """
    Validate provider-specific configuration.
    
    Convenience function that delegates to LangChainFactory.validate_provider_config().
    
    Args:
        provider: Provider name
        config: Provider configuration dictionary
        
    Returns:
        True if configuration is valid, False otherwise
    """
    return LangChainFactory.validate_provider_config(provider, config)
