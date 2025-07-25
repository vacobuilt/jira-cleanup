"""
LLM integration utilities for Jira Cleanup.

This package handles the interaction with LLM services for
ticket analysis and assessment using the new clean architecture.
"""

from jiraclean.entities import AssessmentResult
from .langchain_service import create_langchain_service, LangChainLLMService

__all__ = [
    'AssessmentResult',
    'create_langchain_service', 
    'LangChainLLMService'
]
