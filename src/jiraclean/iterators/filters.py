"""
Ticket filtering definitions for iterators.

This module provides filter interfaces and implementations for filtering tickets
before they are sent to the LLM for assessment.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set


class TicketFilter(ABC):
    """Abstract base class for all ticket filters."""
    
    @abstractmethod
    def passes(self, ticket_data: Dict[str, Any]) -> bool:
        """
        Determine if a ticket passes this filter.
        
        Args:
            ticket_data: Complete ticket data dictionary
            
        Returns:
            True if the ticket passes the filter, False otherwise
        """
        pass


class MinimumAgeFilter(TicketFilter):
    """Filter out tickets that are too new."""
    
    def __init__(self, min_days: int = 14):
        """
        Initialize with minimum age in days.
        
        Args:
            min_days: Minimum age in days for a ticket to pass
        """
        self.min_days = min_days
    
    def passes(self, ticket_data: Dict[str, Any]) -> bool:
        """
        Check if the ticket is older than the minimum age.
        
        Args:
            ticket_data: Complete ticket data dictionary
            
        Returns:
            True if the ticket is older than min_days, False otherwise
        """
        # Get created date from ticket
        created_str = ticket_data.get('fields', {}).get('created')
        if not created_str:
            # If no creation date found, conservatively return True
            return True
        
        try:
            # Parse the date (typically in ISO format with timezone)
            created_date = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            
            # Check if ticket is older than min_days
            min_age_date = datetime.now(created_date.tzinfo) - timedelta(days=self.min_days)
            return created_date <= min_age_date
        except (ValueError, TypeError):
            # If date parsing fails, conservatively return True
            return True


class RecentActivityFilter(TicketFilter):
    """Filter out tickets with recent activity."""
    
    def __init__(self, min_inactive_days: int = 7):
        """
        Initialize with minimum inactive days.
        
        Args:
            min_inactive_days: Minimum days without activity to pass
        """
        self.min_inactive_days = min_inactive_days
    
    def passes(self, ticket_data: Dict[str, Any]) -> bool:
        """
        Check if the ticket has had no activity for min_inactive_days.
        
        Args:
            ticket_data: Complete ticket data dictionary
            
        Returns:
            True if the ticket has no recent activity, False otherwise
        """
        # Get updated date from ticket
        updated_str = ticket_data.get('fields', {}).get('updated')
        if not updated_str:
            # If no update date found, conservatively return True
            return True
        
        try:
            # Parse the date (typically in ISO format with timezone)
            updated_date = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
            
            # Check if ticket has been inactive for min_inactive_days
            min_inactive_date = datetime.now(updated_date.tzinfo) - timedelta(days=self.min_inactive_days)
            return updated_date <= min_inactive_date
        except (ValueError, TypeError):
            # If date parsing fails, conservatively return True
            return True


class StatusFilter(TicketFilter):
    """Filter tickets based on status."""
    
    def __init__(self, excluded_statuses: Optional[List[str]] = None, 
                 included_statuses: Optional[List[str]] = None):
        """
        Initialize with status exclusion/inclusion lists.
        
        Args:
            excluded_statuses: List of statuses to exclude
            included_statuses: List of statuses to include (takes precedence if both provided)
        """
        self.excluded_statuses = set(excluded_statuses or [])
        self.included_statuses = set(included_statuses or [])
    
    def passes(self, ticket_data: Dict[str, Any]) -> bool:
        """
        Check if the ticket status passes the filter.
        
        Args:
            ticket_data: Complete ticket data dictionary
            
        Returns:
            True if the ticket status passes, False otherwise
        """
        # Extract status name from the ticket
        status_name = ticket_data.get('fields', {}).get('status', {}).get('name')
        if not status_name:
            # If no status found, conservatively return True
            return True
        
        # If we have included statuses, ticket must match one of them
        if self.included_statuses:
            return status_name in self.included_statuses
        
        # Otherwise, ticket must not match any excluded status
        return status_name not in self.excluded_statuses


class CompositeFilter(TicketFilter):
    """Combines multiple filters with AND logic."""
    
    def __init__(self, filters: List[TicketFilter]):
        """
        Initialize with a list of filters.
        
        Args:
            filters: List of filters to apply
        """
        self.filters = filters
    
    def passes(self, ticket_data: Dict[str, Any]) -> bool:
        """
        Check if the ticket passes all filters.
        
        Args:
            ticket_data: Complete ticket data dictionary
            
        Returns:
            True if the ticket passes all filters, False otherwise
        """
        return all(f.passes(ticket_data) for f in self.filters)


# Factory function to create default quiescence pre-filter
def create_quiescence_prefilter(
    min_age_days: int = 14,
    min_inactive_days: int = 7,
    excluded_statuses: Optional[List[str]] = None
) -> TicketFilter:
    """
    Create a standard pre-filter for quiescence checks.
    
    This creates a composite filter that combines:
    - Minimum age (ticket must be older than X days)
    - Recent activity (ticket must have no activity in last X days)
    - Status (ticket must not have excluded statuses)
    
    Args:
        min_age_days: Minimum ticket age in days
        min_inactive_days: Minimum days without activity
        excluded_statuses: Statuses to exclude
        
    Returns:
        A CompositeFilter with all the specified filters
    """
    excluded_statuses = excluded_statuses or ["Closed", "Done", "Resolved"]
    
    return CompositeFilter([
        MinimumAgeFilter(min_age_days),
        RecentActivityFilter(min_inactive_days),
        StatusFilter(excluded_statuses=excluded_statuses)
    ])
