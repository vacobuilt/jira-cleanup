"""
Jira client utilities for the Jira Cleanup tool.

This module provides factory functions for creating Jira clients,
both real and dry-run variants.
"""

from typing import Optional

from .client import JiraClient
from .dry_run_client import DryRunJiraClient


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
