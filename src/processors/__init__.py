"""
Ticket processors for Jira Cleanup.

This package contains processor implementations that define
what happens to tickets after they are selected by iterators.
"""

from jira_cleanup.src.processors.base import TicketProcessor
from jira_cleanup.src.processors.quiescent import QuiescentTicketProcessor

__all__ = [
    'TicketProcessor',
    'QuiescentTicketProcessor'
]
