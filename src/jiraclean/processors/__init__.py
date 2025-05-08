"""
Ticket processor implementations for Jira Cleanup.

This package provides various processor implementations for handling different 
types of ticket processing logic, such as quiescence assessment.
"""

from .base import TicketProcessor
from .quiescent import QuiescentTicketProcessor

__all__ = ['TicketProcessor', 'QuiescentTicketProcessor']
