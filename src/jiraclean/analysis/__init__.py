"""
Analysis module for ticket assessment and business logic.

This module contains pure business logic for analyzing tickets,
separated from LLM communication concerns.
"""

from .ticket_analyzer import TicketAnalyzer, AnalysisError

__all__ = ['TicketAnalyzer', 'AnalysisError']
