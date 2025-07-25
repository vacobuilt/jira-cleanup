"""
Clean LLM Assessment Module.

This module provides a clean interface for ticket assessment,
using the new TicketAnalyzer architecture with dependency injection.
"""

# Re-export AssessmentResult from the analysis module for convenience
from jiraclean.analysis.ticket_analyzer import AssessmentResult

# Export the main class for external use
__all__ = ['AssessmentResult']
