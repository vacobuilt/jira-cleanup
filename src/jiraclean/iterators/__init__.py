"""
Ticket iterator implementations for Jira Cleanup.

This package provides various iterator implementations for iterating through
Jira tickets based on different selection criteria.
"""

from .base import TicketIterator
from .project import ProjectTicketIterator

__all__ = ['TicketIterator', 'ProjectTicketIterator']
