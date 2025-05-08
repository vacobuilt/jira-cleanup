"""
Jira API utilities and interfaces for Jira Cleanup.

This package handles the interaction with Jira, abstracting the API
details and providing a clean interface for the rest of the application.
"""

from typing import Optional

from .client import JiraClient
from .dry_run_client import DryRunJiraClient
from .exceptions import (
    JiraClientError,
    JiraAuthenticationError,
    JiraConnectionError,
    JiraNotFoundError,
    JiraPermissionError,
    JiraRateLimitError,
    JiraOperationError
)


def create_jira_client(
    url: str,
    auth_method: str = 'token',
    username: Optional[str] = None,
    token: Optional[str] = None,
    dry_run: bool = False
):
    """
    Factory function to create appropriate Jira client based on configuration.
    
    Args:
        url: Jira server URL
        auth_method: Authentication method ('token', 'basic', or 'oauth')
        username: Jira username
        token: API token or password
        dry_run: Whether to create a dry-run client that doesn't modify Jira
        
    Returns:
        JiraClient or DryRunJiraClient instance
    """
    if dry_run:
        return DryRunJiraClient(
            url=url,
            auth_method=auth_method,
            username=username,
            token=token
        )
    else:
        return JiraClient(
            url=url,
            auth_method=auth_method,
            username=username,
            token=token
        )


__all__ = [
    'JiraClient',
    'DryRunJiraClient',
    'create_jira_client',
    'JiraClientError',
    'JiraAuthenticationError',
    'JiraConnectionError',
    'JiraNotFoundError',
    'JiraPermissionError',
    'JiraRateLimitError',
    'JiraOperationError'
]
