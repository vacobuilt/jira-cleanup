"""
Jira API utilities and interfaces for Jira Cleanup.

This package handles the interaction with Jira, abstracting the API
details and providing a clean interface for the rest of the application.
"""

from jira_cleanup.src.jirautil.client import JiraClient
from jira_cleanup.src.jirautil.dry_run_client import DryRunJiraClient, create_jira_client
from jira_cleanup.src.jirautil.exceptions import (
    JiraClientError,
    JiraAuthenticationError,
    JiraConnectionError,
    JiraNotFoundError,
    JiraPermissionError,
    JiraRateLimitError,
    JiraOperationError
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
