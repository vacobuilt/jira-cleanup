"""
Shared entities for the jiraclean application.

This module contains data structures that are shared across
different layers of the application to avoid circular imports.
"""

from .assessment import AssessmentResult

__all__ = ['AssessmentResult']
