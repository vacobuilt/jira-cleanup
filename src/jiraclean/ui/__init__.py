"""
UI module for Jira Cleanup.

This module provides Rich-based user interface components for beautiful
terminal output, including ticket formatting, progress indicators, and
interactive elements.
"""

from jiraclean.ui.console import console
from jiraclean.ui.components import TicketCard, StatusIndicator, ProgressTracker
from jiraclean.ui.formatters import format_ticket, format_assessment, format_error

__all__ = [
    'console',
    'TicketCard',
    'StatusIndicator', 
    'ProgressTracker',
    'format_ticket',
    'format_assessment',
    'format_error'
]
