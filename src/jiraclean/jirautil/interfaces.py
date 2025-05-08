"""
Interfaces for Jira client implementations.

This module defines the abstract base classes that all Jira
client implementations must adhere to, ensuring consistent
behavior across different implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class JiraClientInterface(ABC):
    """
    Interface for Jira client implementations.
    
    This abstract base class defines the required methods that
    all Jira client implementations must provide.
    """
    
    @abstractmethod
    def get_issue(self, issue_key: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Retrieve a single Jira issue by key.
        
        Args:
            issue_key: The Jira issue key (e.g., 'PROJ-123')
            fields: Optional list of fields to include (None for all fields)
            
        Returns:
            Dict containing issue data
            
        Raises:
            JiraNotFoundError: If the issue doesn't exist
            JiraAuthenticationError: If authentication fails
            JiraConnectionError: If connection to Jira fails
        """
        pass
    
    @abstractmethod
    def search_issues(self, 
                     jql: str, 
                     start_at: int = 0, 
                     max_results: int = 50, 
                     fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for issues using JQL.
        
        Args:
            jql: JQL query string
            start_at: Index of first result (for pagination)
            max_results: Maximum results to return
            fields: List of fields to include (None for all fields)
            
        Returns:
            List of matching issue dictionaries
            
        Raises:
            JiraAuthenticationError: If authentication fails
            JiraConnectionError: If connection to Jira fails
            JiraOperationError: If the JQL is invalid
        """
        pass
    
    @abstractmethod
    def add_comment(self, issue_key: str, body: str) -> Dict[str, Any]:
        """
        Add a comment to an issue.
        
        Args:
            issue_key: The Jira issue key
            body: Comment text (may include Jira markup)
            
        Returns:
            Dict containing the created comment data
            
        Raises:
            JiraNotFoundError: If the issue doesn't exist
            JiraAuthenticationError: If authentication fails
            JiraPermissionError: If user lacks permission
        """
        pass
    
    @abstractmethod
    def transition_issue(self, 
                        issue_key: str, 
                        transition_id: str, 
                        comment: Optional[str] = None,
                        fields: Optional[Dict[str, Any]] = None) -> None:
        """
        Transition an issue to a new status.
        
        Args:
            issue_key: The Jira issue key
            transition_id: ID of the transition to perform
            comment: Optional comment to add with the transition
            fields: Optional fields to update during transition
            
        Raises:
            JiraNotFoundError: If the issue doesn't exist
            JiraAuthenticationError: If authentication fails
            JiraPermissionError: If user lacks permission
        """
        pass
    
    @abstractmethod
    def get_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get available transitions for an issue.
        
        Args:
            issue_key: The Jira issue key
            
        Returns:
            List of available transitions
            
        Raises:
            JiraNotFoundError: If the issue doesn't exist
            JiraAuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    def assign_issue(self, issue_key: str, assignee: Optional[str]) -> None:
        """
        Assign an issue to a user.
        
        Args:
            issue_key: The Jira issue key
            assignee: Username to assign to, or None to unassign
            
        Raises:
            JiraNotFoundError: If the issue doesn't exist
            JiraAuthenticationError: If authentication fails
            JiraPermissionError: If user lacks permission
        """
        pass
