"""
Ticket processors for Jira Cleanup.

This package contains processor implementations that define
what happens to tickets after they are selected by iterators.
"""

from .base import TicketProcessor
from .quiescent import QuiescentTicketProcessor

__all__ = [
    'TicketProcessor',
    'QuiescentTicketProcessor'
]
