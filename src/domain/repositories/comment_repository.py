"""
Comment repository interface.

This module defines the repository interface for adding and accessing
comments on tickets, following the Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any

from jira_cleanup.src.domain.entities.action import ActionRecommendation


class CommentRepository(ABC):
    """
    Abstract repository interface for ticket comment operations.
    
    This interface defines the operations that any comment data provider
    must implement, allowing the domain layer to remain independent of
    specific data storage implementations.
    """
    
    @abstractmethod
    def add_comment(self, ticket_key: str, comment_text: str) -> Dict[str, Any]:
        """
        Add a comment to a ticket.
        
        Args:
            ticket_key: The key of the ticket to comment on
            comment_text: The text of the comment to add
            
        Returns:
            Dictionary with information about the created comment
            
        Raises:
            TicketNotFoundError: If the ticket doesn't exist
            CommentAddError: If the comment couldn't be added
        """
        pass
    
    @abstractmethod
    def get_comments(self, ticket_key: str) -> List[Dict[str, Any]]:
        """
        Get all comments for a ticket.
        
        Args:
            ticket_key: The key of the ticket
            
        Returns:
            List of comments, each as a dictionary
            
        Raises:
            TicketNotFoundError: If the ticket doesn't exist
        """
        pass
    
    @abstractmethod
    def has_recent_system_comment(
        self,
        ticket_key: str,
        days: int = 7,
        system_markers: Optional[List[str]] = None
    ) -> bool:
        """
        Check if a ticket has a recent system-generated comment.
        
        Args:
            ticket_key: The key of the ticket
            days: The number of days to check for recent comments
            system_markers: Optional list of markers that identify system comments
            
        Returns:
            True if a recent system comment exists, False otherwise
            
        Raises:
            TicketNotFoundError: If the ticket doesn't exist
        """
        pass
    
    @abstractmethod
    def execute_comment_action(self, action: ActionRecommendation) -> Dict[str, Any]:
        """
        Execute a comment action recommendation.
        
        This method is used to apply an action that was recommended 
        by the assessment process.
        
        Args:
            action: The action recommendation to execute
            
        Returns:
            Dictionary with information about the execution result
            
        Raises:
            InvalidActionError: If the action type is not a comment action
            TicketNotFoundError: If the ticket doesn't exist
            CommentAddError: If the comment couldn't be added
        """
        pass
