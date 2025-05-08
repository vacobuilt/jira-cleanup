"""
LLM integration utilities for Jira Cleanup.

This package handles the interaction with LLM services for
ticket analysis and assessment.
"""

from .assessment import AssessmentResult, assess_ticket

__all__ = [
    'AssessmentResult',
    'assess_ticket'
]
