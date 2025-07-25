"""
Shared entities for the jiraclean application.

This module contains data structures that are shared across
different layers of the application to avoid circular imports.
"""

from jiraclean.entities.base_result import BaseResult
from jiraclean.entities.quiescent_result import QuiescentResult
from jiraclean.entities.quality_result import QualityResult

__all__ = ['BaseResult', 'QuiescentResult', 'QualityResult']
