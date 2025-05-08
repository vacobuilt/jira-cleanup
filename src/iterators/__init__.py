"""
Ticket iteration utilities for Jira Cleanup.

This package contains the iterators that yield Jira tickets
for processing, implementing various selection strategies.
"""

from jira_cleanup.src.iterators.base import TicketIterator

__all__ = ['TicketIterator']
