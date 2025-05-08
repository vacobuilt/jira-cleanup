"""
LLM-based processing for Jira Cleanup.

This package provides modules for using LLMs to assess tickets
and generate responses.
"""

from .assessment import AssessmentResult, assess_ticket

__all__ = ['AssessmentResult', 'assess_ticket']
