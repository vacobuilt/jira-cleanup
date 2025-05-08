"""
Domain service interfaces for Jira Cleanup.

This package contains interfaces for domain services that encapsulate
business operations that may have different implementations.
"""

from jira_cleanup.src.domain.services.interfaces.llm_service import LlmService
from jira_cleanup.src.domain.services.interfaces.prompt_service import PromptService

__all__ = [
    'LlmService',
    'PromptService'
]
