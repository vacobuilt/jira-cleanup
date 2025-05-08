"""
Repository interfaces for Jira Cleanup.

This package contains repository interfaces that define how the domain layer
interacts with data sources, following the Dependency Inversion Principle.
"""

from jira_cleanup.src.domain.repositories.ticket_repository import TicketRepository
from jira_cleanup.src.domain.repositories.comment_repository import CommentRepository

__all__ = [
    'TicketRepository',
    'CommentRepository'
]
