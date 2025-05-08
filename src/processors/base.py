"""
Base ticket processor implementation.

This module provides the abstract base class for all ticket processors,
defining the interface that all concrete processor implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class TicketProcessor(ABC):
    """
    Abstract base class for ticket processors.
    
    Processors define what happens to each ticket in the cleanup process,
    such as commenting, transitioning status, or other actions.
    """
    
    def __init__(self):
        """Initialize the processor with empty stats."""
        self._stats = {
            'processed': 0,
            'actioned': 0,
            'errors': 0,
            'skipped': 0
        }
    
    @abstractmethod
    def process(self, 
                ticket_key: str, 
                ticket_data: Dict[str, Any], 
                dry_run: bool = True) -> Dict[str, Any]:
        """
        Process a single ticket.
        
        Args:
            ticket_key: The Jira issue key
            ticket_data: The ticket data dictionary
            dry_run: If True, only simulate actions without making changes
            
        Returns:
            Result dictionary with action information:
            {
                'ticket_key': str,
                'actions': [
                    {
                        'type': str,  # 'comment', 'transition', 'assign', etc.
                        'description': str,
                        'success': bool,
                        'details': Dict[str, Any]  # action-specific details
                    }
                ],
                'success': bool,
                'message': str
            }
        """
        pass
    
    @abstractmethod
    def describe_action(self, ticket_key: str, ticket_data: Dict[str, Any]) -> str:
        """
        Describe the action that would be taken for a ticket.
        Used for dry runs and logging.
        
        Args:
            ticket_key: The Jira issue key
            ticket_data: The ticket data dictionary
            
        Returns:
            Human-readable description of the action
        """
        pass
    
    @property
    def stats(self) -> Dict[str, int]:
        """
        Get statistics about processed tickets.
        
        Returns:
            Dictionary of counters (e.g., {'processed': 10, 'actioned': 5, 'errors': 2})
        """
        return self._stats.copy()
    
    def _update_stats(self, result: Dict[str, Any]) -> None:
        """
        Update statistics based on processing result.
        
        Args:
            result: The result dictionary from process()
        """
        self._stats['processed'] += 1
        
        if not result.get('success', False):
            self._stats['errors'] += 1
            return
            
        if len(result.get('actions', [])) > 0:
            # Count as actioned if any actions were taken
            actions_taken = any(a.get('success', False) for a in result.get('actions', []))
            if actions_taken:
                self._stats['actioned'] += 1
            else:
                self._stats['skipped'] += 1
        else:
            self._stats['skipped'] += 1
    
    def reset_stats(self) -> None:
        """Reset all statistics counters to zero."""
        for key in self._stats:
            self._stats[key] = 0
