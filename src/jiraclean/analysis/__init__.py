"""
Analysis module for ticket assessment and business logic.

This module contains pure business logic for analyzing tickets,
separated from LLM communication concerns. It provides multiple
analyzer types through a pluggable architecture.
"""

from .base import BaseTicketAnalyzer
from .ticket_analyzer import QuiescentAnalyzer, AnalysisError
from .quality_analyzer import TicketQualityAnalyzer
from jiraclean.llm.langchain_service import LangChainLLMService
from typing import Dict, Type

# Registry of available analyzers
ANALYZER_REGISTRY: Dict[str, Type[BaseTicketAnalyzer]] = {
    'quiescent': QuiescentAnalyzer,
    'ticket_quality': TicketQualityAnalyzer,
}

# Default analyzer type
DEFAULT_ANALYZER = 'quiescent'


def create_analyzer(analyzer_type: str, llm_service: LangChainLLMService) -> BaseTicketAnalyzer:
    """
    Create an analyzer instance of the specified type.
    
    Args:
        analyzer_type: Type of analyzer to create ('quiescent', 'ticket_quality')
        llm_service: LangChain LLM service for communication
        
    Returns:
        Configured analyzer instance
        
    Raises:
        ValueError: If analyzer type is not supported
    """
    if analyzer_type not in ANALYZER_REGISTRY:
        available = ', '.join(ANALYZER_REGISTRY.keys())
        raise ValueError(f"Unsupported analyzer type '{analyzer_type}'. Available: {available}")
    
    analyzer_class = ANALYZER_REGISTRY[analyzer_type]
    return analyzer_class(llm_service)


def get_available_analyzers() -> Dict[str, str]:
    """
    Get a dictionary of available analyzer types and their descriptions.
    
    Returns:
        Dictionary mapping analyzer type to description
    """
    return {
        'quiescent': 'Detects stalled or inactive tickets requiring intervention',
        'ticket_quality': 'Assesses ticket quality, completeness, and adherence to standards',
    }


def get_default_analyzer_type() -> str:
    """
    Get the default analyzer type.
    
    Returns:
        Default analyzer type string
    """
    return DEFAULT_ANALYZER


# Backward compatibility - keep TicketAnalyzer as alias for QuiescentAnalyzer
TicketAnalyzer = QuiescentAnalyzer

__all__ = [
    'BaseTicketAnalyzer',
    'QuiescentAnalyzer', 
    'TicketQualityAnalyzer',
    'TicketAnalyzer',  # Backward compatibility
    'AnalysisError',
    'create_analyzer',
    'get_available_analyzers',
    'get_default_analyzer_type',
    'ANALYZER_REGISTRY',
    'DEFAULT_ANALYZER'
]
