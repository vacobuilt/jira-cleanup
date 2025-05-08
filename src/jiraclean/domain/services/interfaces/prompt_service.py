"""
Prompt service interface.

This module defines the interface for prompt services that can be used
to manage and render LLM prompts.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class PromptService(ABC):
    """
    Abstract interface for prompt service operations.
    
    This interface defines the operations that any prompt service provider
    must implement, allowing the application to remain independent of
    specific prompt storage implementations.
    """
    
    @abstractmethod
    def get_prompt(self, prompt_name: str) -> str:
        """
        Get a raw prompt template by name.
        
        Args:
            prompt_name: The name of the prompt to retrieve
            
        Returns:
            The prompt template text
            
        Raises:
            PromptNotFoundError: If the prompt doesn't exist
        """
        pass
    
    @abstractmethod
    def render_prompt(self, prompt_name: str, variables: Dict[str, Any]) -> str:
        """
        Render a prompt template with variables.
        
        Args:
            prompt_name: The name of the prompt to render
            variables: Dictionary of variables to substitute in the template
            
        Returns:
            The rendered prompt text
            
        Raises:
            PromptNotFoundError: If the prompt doesn't exist
            PromptRenderError: If there's an error rendering the prompt
        """
        pass
    
    @abstractmethod
    def list_prompts(self) -> List[str]:
        """
        List all available prompt names.
        
        Returns:
            List of prompt names
        """
        pass
    
    @abstractmethod
    def get_prompt_metadata(self, prompt_name: str) -> Dict[str, Any]:
        """
        Get metadata about a prompt.
        
        Args:
            prompt_name: The name of the prompt
            
        Returns:
            Dictionary of metadata
            
        Raises:
            PromptNotFoundError: If the prompt doesn't exist
        """
        pass
    
    @abstractmethod
    def validate_variables(self, prompt_name: str, variables: Dict[str, Any]) -> List[str]:
        """
        Validate that all required variables for a prompt are provided.
        
        Args:
            prompt_name: The name of the prompt
            variables: Dictionary of provided variables
            
        Returns:
            List of missing variable names (empty if all variables are provided)
            
        Raises:
            PromptNotFoundError: If the prompt doesn't exist
        """
        pass
