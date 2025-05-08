"""
Jira comment repository implementation.

This module contains an implementation of the comment repository interface
that uses the Jira API to add and retrieve ticket comments.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from jira import JIRA
from jira.exceptions import JIRAError

from jiraclean.domain.entities.action import ActionRecommendation, ActionType
from jiraclean.domain.repositories.comment_repository import CommentRepository


logger = logging.getLogger('jiraclean.infrastructure.repositories.jira_comment_repository')


class InvalidActionError(Exception):
    """Raised when an invalid action is provided to execute."""
    pass


class JiraCommentRepository(CommentRepository):
    """
    Implementation of the comment repository using the Jira API.
    
    This repository handles operations related to Jira ticket comments,
    such as adding comments and checking for system-generated comments.
    """
    
    def __init__(self, jira_client: JIRA):
        """
        Initialize the Jira comment repository.
        
        Args:
            jira_client: JIRA client instance
        """
        self.jira_client = jira_client
    
    def add_comment(self, ticket_key: str, comment_text: str) -> Dict[str, Any]:
        """
        Add a comment to a ticket.
        
        Args:
            ticket_key: The key of the ticket to comment on
            comment_text: The text of the comment to add
            
        Returns:
            Dictionary with information about the created comment
            
        Raises:
            JiraError: If there's an error with the Jira API
        """
        try:
            logger.info(f"Adding comment to ticket {ticket_key}")
            logger.debug(f"Comment text: {comment_text[:100]}..." if len(comment_text) > 100 else comment_text)
            
            # Add the comment using Jira API
            comment = self.jira_client.add_comment(ticket_key, comment_text)
            
            # Convert to a dictionary for the return value
            return {
                'id': comment.id,
                'body': comment.body,
                'author': getattr(comment.author, 'displayName', 'Unknown'),
                'created': comment.created,
                'updated': comment.updated,
                'success': True
            }
        except JIRAError as e:
            # Log the error
            logger.error(f"Error adding comment to ticket {ticket_key}: {str(e)}")
            
            # Raise the error
            raise
    
    def get_comments(self, ticket_key: str) -> List[Dict[str, Any]]:
        """
        Get all comments for a ticket.
        
        Args:
            ticket_key: The key of the ticket
            
        Returns:
            List of comments, each as a dictionary
            
        Raises:
            JiraError: If there's an error with the Jira API
        """
        try:
            # Get the issue with only the comment field expanded
            issue = self.jira_client.issue(ticket_key, fields='comment')
            
            # Extract and convert comments to dictionaries
            comments_data = []
            if hasattr(issue.fields, 'comment') and issue.fields.comment:
                for comment in issue.fields.comment.comments:
                    comment_dict = {
                        'id': comment.id,
                        'body': comment.body,
                        'author': getattr(comment.author, 'displayName', 'Unknown'),
                        'author_username': getattr(comment.author, 'name', None),
                        'author_account_id': getattr(comment.author, 'accountId', None),
                        'created': comment.created,
                        'updated': comment.updated,
                        'is_system_comment': self._is_system_comment(comment.body)
                    }
                    comments_data.append(comment_dict)
            
            return comments_data
        except JIRAError as e:
            # Log the error
            logger.error(f"Error getting comments for ticket {ticket_key}: {str(e)}")
            
            # Raise the error
            raise
    
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
            JiraError: If there's an error with the Jira API
        """
        try:
            # Get all comments for the ticket
            comments = self.get_comments(ticket_key)
            
            # If no system markers provided, use default
            if system_markers is None:
                system_markers = [
                    '[AUTOMATED QUIESCENCE ASSESSMENT]',
                    '[Quiescent Ticket System]',
                    '[JIRA GOVERNANCE SYSTEM]'
                ]
            
            # Calculate the threshold date
            threshold_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Check for recent system comments
            for comment in comments:
                # Check if it's a system comment based on content
                is_system = False
                for marker in system_markers:
                    if marker in comment['body']:
                        is_system = True
                        break
                
                if not is_system:
                    continue
                
                # Parse the creation date
                created_date = self._parse_jira_date(comment['created'])
                
                # Check if it's recent
                if created_date >= threshold_date:
                    return True
            
            # No recent system comments found
            return False
        except JIRAError as e:
            # Log the error
            logger.error(f"Error checking for recent system comments on ticket {ticket_key}: {str(e)}")
            
            # Raise the error
            raise
    
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
            JiraError: If there's an error with the Jira API
        """
        # Validate that this is a comment action
        if action.type != ActionType.COMMENT:
            raise InvalidActionError(f"Cannot execute non-comment action: {action.type}")
        
        # Extract the comment text
        comment_text = action.comment_text
        if not comment_text:
            raise InvalidActionError("Comment action has no comment text")
        
        try:
            # Add the comment
            result = self.add_comment(action.ticket_key, comment_text)
            
            # Mark the action as completed
            action.mark_completed()
            
            # Return the result
            return {
                'action_id': id(action),  # Use object ID as unique identifier
                'ticket_key': action.ticket_key,
                'action_type': str(action.type),
                'status': 'completed',
                'comment_id': result.get('id'),
                'success': True
            }
        except Exception as e:
            # Mark the action as failed
            action.mark_failed(str(e))
            
            # Return failure information
            return {
                'action_id': id(action),
                'ticket_key': action.ticket_key,
                'action_type': str(action.type),
                'status': 'failed',
                'error': str(e),
                'success': False
            }
    
    def _is_system_comment(self, comment_body: str) -> bool:
        """
        Check if a comment is system-generated based on its content.
        
        Args:
            comment_body: The text content of the comment
            
        Returns:
            True if it appears to be a system-generated comment, False otherwise
        """
        system_markers = [
            '[AUTOMATED QUIESCENCE ASSESSMENT]',
            '[Quiescent Ticket System]',
            '[JIRA GOVERNANCE SYSTEM]'
        ]
        
        return any(marker in comment_body for marker in system_markers)
    
    def _parse_jira_date(self, date_str: str) -> datetime:
        """
        Parse a Jira date string to a datetime object.
        
        Args:
            date_str: Date string from Jira API
            
        Returns:
            Parsed datetime with timezone
        """
        if not date_str:
            return datetime.now(timezone.utc)
            
        try:
            # Jira usually provides ISO-8601 dates
            # Replace Z with +00:00 for better compatibility
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            # Fallback to now if parsing fails
            logger.warning(f"Failed to parse Jira date string: {date_str}")
            return datetime.now(timezone.utc)
