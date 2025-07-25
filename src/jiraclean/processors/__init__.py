"""
Ticket processors for Jira Cleanup.

This package contains processor implementations that define
what happens to tickets after they are selected by iterators.
"""

from .base import TicketProcessor
from .generic import GenericTicketProcessor

__all__ = [
    'TicketProcessor',
    'GenericTicketProcessor'
]
