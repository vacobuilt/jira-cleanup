"""
Custom exceptions for Jira operations.

This module defines a hierarchy of custom exceptions for Jira
operations, allowing for more specific error handling.
"""

class JiraClientError(Exception):
    """Base class for all Jira client errors."""
    pass


class JiraConnectionError(JiraClientError):
    """Error connecting to the Jira server."""
    pass


class JiraAuthenticationError(JiraClientError):
    """Authentication failed."""
    pass


class JiraPermissionError(JiraClientError):
    """Permission denied for the requested operation."""
    pass


class JiraNotFoundError(JiraClientError):
    """Requested resource was not found."""
    pass


class JiraRateLimitError(JiraClientError):
    """Rate limit exceeded."""
    pass


class JiraOperationError(JiraClientError):
    """General error during Jira operation."""
    pass
