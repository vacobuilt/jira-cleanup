"""
Ticket iteration utilities for Jira Cleanup.

This package contains the iterators that yield Jira tickets
for processing, implementing various selection strategies.
"""

from .base import TicketIterator
from .project import ProjectTicketIterator

__all__ = [
    'TicketIterator',
    'ProjectTicketIterator'
]
