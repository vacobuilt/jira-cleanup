"""
Dry-run Jira client implementation.

This module provides a non-destructive Jira client that simulates 
write operations without making actual changes to Jira.
"""

import logging
from typing import Dict, List, Any, Optional, Union

from .client import JiraClient

logger = logging.getLogger('jira_cleanup.jirautil.dry_run')


class DryRunJiraClient(JiraClient):
    """
    Dry-run Jira client that simulates write operations.
    
    This client has identical read behavior to the standard JiraClient
    but doesn't perform actual write operations to Jira. Instead, it logs
    what would have been done.
    """
    
    def __init__(self, 
                url: str, 
                auth_method: str = 'token', 
                username: Optional[str] = None,
                token: Optional[str] = None,
                max_retries: int = 3,
                retry_delay: float = 2.0):
        """
        Initialize the dry-run Jira client.
        
        Args:
            url: Jira server URL
            auth_method: Authentication method ('token', 'basic', or 'oauth')
            username: Jira username (required for 'token' and 'basic' auth)
            token: API token (required for 'token' auth)
            max_retries: Maximum number of retries for failed requests
            retry_delay: Base delay between retries (seconds)
        """
        super().__init__(url, auth_method, username, token, max_retries, retry_delay)
        logger.info("Initializing Jira client in DRY RUN mode - no changes will be made to Jira")
    
    def add_comment(self, issue_key: str, body: str) -> Dict[str, Any]:
        """
        Simulate adding a comment to an issue.
        
        Args:
            issue_key: The Jira issue key
            body: Comment text (may include Jira markup)
            
        Returns:
            Simulated comment data dictionary
        """
        logger.info(f"DRY RUN: Would add comment to {issue_key}")
        logger.info(f"DRY RUN: Comment text: {body}")
        
        # Create a simulated response
        return {
            'id': 'dry-run-comment-id',
            'body': body,
            'author': {
                'name': self.username,
                'displayName': self.username
            },
            'created': 'now',
            'updated': 'now'
        }
    
    def transition_issue(self, 
                        issue_key: str, 
                        transition_id: str, 
                        comment: Optional[str] = None,
                        fields: Optional[Dict[str, Any]] = None) -> None:
        """
        Simulate transitioning an issue to a new status.
        
        Args:
            issue_key: The Jira issue key
            transition_id: ID of the transition to perform
            comment: Optional comment to add with the transition
            fields: Optional fields to update during transition
        """
        # Get transition name for better logging
        transition_name = "Unknown"
        try:
            transitions = self.get_transitions(issue_key)
            for t in transitions:
                if t['id'] == transition_id:
                    transition_name = t['name']
                    break
        except Exception:
            # If we can't get the transition name, just use the ID
            pass
        
        logger.info(f"DRY RUN: Would transition {issue_key} to {transition_name} (id: {transition_id})")
        
        if comment:
            logger.info(f"DRY RUN: With transition comment: {comment}")
        
        if fields:
            logger.info(f"DRY RUN: Would update fields: {fields}")
    
    def assign_issue(self, issue_key: str, assignee: Optional[str]) -> None:
        """
        Simulate assigning an issue to a user.
        
        Args:
            issue_key: The Jira issue key
            assignee: Username to assign to, or None to unassign
        """
        if assignee:
            logger.info(f"DRY RUN: Would assign {issue_key} to {assignee}")
        else:
            logger.info(f"DRY RUN: Would unassign {issue_key}")


def create_jira_client(
    url: str,
    auth_method: str = 'token',
    username: Optional[str] = None,
    token: Optional[str] = None,
    dry_run: bool = True,
    max_retries: int = 3,
    retry_delay: float = 2.0
) -> Union[JiraClient, DryRunJiraClient]:
    """
    Factory function to create the appropriate Jira client.
    
    Args:
        url: Jira server URL
        auth_method: Authentication method ('token', 'basic', or 'oauth')
        username: Jira username (required for 'token' and 'basic' auth)
        token: API token (required for 'token' auth)
        dry_run: If True, create a DryRunJiraClient, otherwise a real JiraClient
        max_retries: Maximum number of retries for failed requests
        retry_delay: Base delay between retries (seconds)
    
    Returns:
        JiraClient or DryRunJiraClient instance
    """
    if dry_run:
        return DryRunJiraClient(
            url=url,
            auth_method=auth_method,
            username=username,
            token=token,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
    else:
        return JiraClient(
            url=url,
            auth_method=auth_method,
            username=username,
            token=token,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
