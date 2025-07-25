"""
Base classes for ticket analysis.

This module provides abstract base classes for different types of ticket analyzers,
enabling a pluggable architecture for various analysis strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from jiraclean.entities.base_result import BaseResult
from jiraclean.llm.langchain_service import LangChainLLMService


class BaseTicketAnalyzer(ABC):
    """
    Abstract base class for ticket analyzers.
    
    This class defines the interface that all ticket analyzers must implement,
    enabling a pluggable architecture for different analysis strategies.
    """
    
    def __init__(self, llm_service: LangChainLLMService):
        """
        Initialize the analyzer with an LLM service.
        
        Args:
            llm_service: LangChain LLM service for communication
        """
        self.llm_service = llm_service
    
    @abstractmethod
    def analyze(self, ticket_data: Dict[str, Any], **kwargs) -> BaseResult:
        """
        Analyze a ticket and return assessment results.
        
        Args:
            ticket_data: Dictionary with ticket information
            **kwargs: Additional analyzer-specific parameters
            
        Returns:
            BaseResult with analysis findings
            
        Raises:
            AnalysisError: If analysis fails
        """
        pass
    
    @abstractmethod
    def get_analyzer_type(self) -> str:
        """
        Get the type identifier for this analyzer.
        
        Returns:
            String identifier for the analyzer type
        """
        pass
    
    @abstractmethod
    def get_default_template(self) -> str:
        """
        Get the default prompt template name for this analyzer.
        
        Returns:
            Template name to use for analysis
        """
        pass
    
    def validate_ticket_data(self, ticket_data: Dict[str, Any]) -> bool:
        """
        Validate that ticket data contains required fields.
        
        Args:
            ticket_data: Dictionary with ticket information
            
        Returns:
            True if ticket data is valid, False otherwise
        """
        required_fields = ['key', 'fields']
        return all(field in ticket_data for field in required_fields)
