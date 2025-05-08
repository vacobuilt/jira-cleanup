"""
Exceptions for the Jira API utilities.

This module defines custom exceptions raised by the Jira client
implementations, allowing for more specific error handling.
"""

class JiraClientError(Exception):
    """Base exception for all Jira client errors."""
    pass


class JiraAuthenticationError(JiraClientError):
    """Raised when authentication to Jira fails."""
    pass


class JiraConnectionError(JiraClientError):
    """Raised when a connection to Jira cannot be established."""
    pass


class JiraNotFoundError(JiraClientError):
    """Raised when a requested resource is not found."""
    pass


class JiraPermissionError(JiraClientError):
    """Raised when the user doesn't have permission for an operation."""
    pass


class JiraRateLimitError(JiraClientError):
    """Raised when Jira API rate limits are exceeded."""
    pass


class JiraOperationError(JiraClientError):
    """Raised when a Jira operation fails for reasons other than the above."""
    pass
