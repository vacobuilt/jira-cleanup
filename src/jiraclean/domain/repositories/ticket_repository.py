"""
Ticket repository interface.

This module defines the repository interface for accessing and
manipulating ticket data, following the Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from jiraclean.domain.entities.ticket import Ticket


class TicketRepository(ABC):
    """
    Abstract repository interface for ticket data access.
    
    This interface defines the operations that any ticket data provider
    must implement, allowing the domain layer to remain independent of
    specific data storage implementations.
    """
    
    @abstractmethod
    def find_by_key(self, ticket_key: str) -> Optional[Ticket]:
        """
        Find a ticket by its key.
        
        Args:
            ticket_key: The unique key of the ticket
            
        Returns:
            The ticket if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_candidates(
        self,
        project_key: str,
        max_tickets: int = 50,
        exclude_statuses: Optional[List[str]] = None,
        only_stale: bool = True,
        stale_threshold_days: int = 14
    ) -> List[Ticket]:
        """
        Find candidate tickets for assessment.
        
        Args:
            project_key: The project key to search within
            max_tickets: Maximum number of tickets to return
            exclude_statuses: Statuses to exclude from search
            only_stale: Whether to only include stale tickets
            stale_threshold_days: Days threshold for staleness
            
        Returns:
            List of candidate tickets
        """
        pass
    
    @abstractmethod
    def find_by_criteria(
        self,
        project_key: Optional[str] = None,
        status: Optional[str] = None,
        issue_type: Optional[str] = None,
        updated_before: Optional[datetime] = None,
        updated_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        created_after: Optional[datetime] = None,
        assignee: Optional[str] = None,
        labels: Optional[List[str]] = None,
        max_results: int = 50
    ) -> List[Ticket]:
        """
        Find tickets matching specific criteria.
        
        Args:
            project_key: Optional project key to filter by
            status: Optional status to filter by
            issue_type: Optional issue type to filter by
            updated_before: Filter tickets updated before this time
            updated_after: Filter tickets updated after this time
            created_before: Filter tickets created before this time
            created_after: Filter tickets created after this time
            assignee: Optional assignee username to filter by
            labels: Optional list of labels to filter by
            max_results: Maximum number of results to return
            
        Returns:
            List of matching tickets
        """
        pass
    
    @abstractmethod
    def save(self, ticket: Ticket) -> Ticket:
        """
        Save changes to a ticket.
        
        Args:
            ticket: The ticket to save
            
        Returns:
            The updated ticket
        """
        pass
    
    @abstractmethod
    def count(
        self,
        project_key: Optional[str] = None,
        status: Optional[str] = None,
        issue_type: Optional[str] = None
    ) -> int:
        """
        Count tickets matching specific criteria.
        
        Args:
            project_key: Optional project key to filter by
            status: Optional status to filter by
            issue_type: Optional issue type to filter by
            
        Returns:
            Count of matching tickets
        """
        pass
