"""
Concrete Jira client implementation.

This module provides the actual implementation of the Jira client
using the jira library, wrapping the functionality needed for the
Jira Cleanup tool.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Union, cast

# Import jira - required dependency even in dry run mode
try:
    from jira import JIRA
    from jira.exceptions import JIRAError
except ImportError:
    raise ImportError(
        "The 'jira' package is required but not installed. "
        "Please install it using 'pip install jira' before running this application. "
        "Even in dry-run mode, the JIRA API is needed to read ticket information."
    )

from .exceptions import (
    JiraAuthenticationError,
    JiraConnectionError,
    JiraNotFoundError,
    JiraPermissionError,
    JiraRateLimitError,
    JiraOperationError
)

logger = logging.getLogger('jiraclean.jirautil')


class JiraClient:
    """
    Concrete Jira client implementation using the jira library.
    
    This class handles all interactions with the Jira API, including
    authentication, error handling, and rate limiting.
    """
    
    def __init__(self, 
                url: str, 
                auth_method: str = 'token', 
                username: Optional[str] = None,
                token: Optional[str] = None,
                max_retries: int = 3,
                retry_delay: float = 2.0):
        """
        Initialize the Jira client.
        
        Args:
            url: Jira server URL
            auth_method: Authentication method ('token', 'basic', or 'oauth')
            username: Jira username (required for 'token' and 'basic' auth)
            token: API token (required for 'token' auth)
            max_retries: Maximum number of retries for failed requests
            retry_delay: Base delay between retries (seconds)
        
        Raises:
            JiraAuthenticationError: If authentication fails
            JiraConnectionError: If connection to Jira fails
        """
        self.url = url
        self.auth_method = auth_method
        self.username = username
        self.token = token
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = self._create_client()
    
    def _create_client(self) -> JIRA:
        """
        Create and return a JIRA client instance.
        
        Returns:
            Configured JIRA client
            
        Raises:
            JiraAuthenticationError: If authentication fails
            JiraConnectionError: If connection to Jira fails
        """
        try:
            if self.auth_method == 'token':
                if not self.username or not self.token:
                    raise JiraAuthenticationError("Username and token required for token authentication")
                return JIRA(self.url, basic_auth=(self.username, self.token))
            elif self.auth_method == 'basic':
                if not self.username or not self.token:
                    raise JiraAuthenticationError("Username and password required for basic authentication")
                return JIRA(self.url, basic_auth=(self.username, self.token))
            elif self.auth_method == 'oauth':
                # OAuth implementation would go here
                raise NotImplementedError("OAuth authentication not yet implemented")
            else:
                raise ValueError(f"Unsupported authentication method: {self.auth_method}")
        except JIRAError as e:
            if e.status_code == 401:
                raise JiraAuthenticationError(f"Authentication failed: {str(e)}")
            elif e.status_code == 404:
                raise JiraConnectionError(f"Invalid Jira URL: {self.url}")
            else:
                raise JiraConnectionError(f"Failed to connect to Jira: {str(e)}")
        except Exception as e:
            raise JiraConnectionError(f"Unexpected error connecting to Jira: {str(e)}")
    
    def _handle_jira_error(self, error: JIRAError) -> None:
        """
        Handle JIRAError and raise appropriate custom exception.
        
        Args:
            error: The JIRAError to handle
            
        Raises:
            JiraNotFoundError: If resource not found (404)
            JiraAuthenticationError: If authentication fails (401)
            JiraPermissionError: If permission denied (403)
            JiraRateLimitError: If rate limited (429)
            JiraOperationError: For other Jira errors
        """
        if error.status_code == 404:
            raise JiraNotFoundError(f"Resource not found: {error.text}")
        elif error.status_code == 401:
            raise JiraAuthenticationError(f"Authentication failed: {error.text}")
        elif error.status_code == 403:
            raise JiraPermissionError(f"Permission denied: {error.text}")
        elif error.status_code == 429:
            raise JiraRateLimitError(f"Rate limit exceeded: {error.text}")
        else:
            raise JiraOperationError(f"Jira operation failed: {error.text}")
    
    def _with_retry(self, func, *args, **kwargs):
        """
        Wrapper to retry Jira operations with exponential backoff.
        
        Args:
            func: Function to call
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result of the function call
            
        Raises:
            Various JiraClientError subclasses depending on the error
        """
        retry_count = 0
        last_exception = None
        
        while retry_count < self.max_retries:
            try:
                return func(*args, **kwargs)
            except JiraRateLimitError as e:
                # Always retry rate limit errors with backoff
                last_exception = e
                retry_count += 1
                wait_time = self.retry_delay * (2 ** retry_count)
                logger.warning(f"Rate limited by Jira, retrying in {wait_time:.2f}s (attempt {retry_count}/{self.max_retries})")
                time.sleep(wait_time)
            except (JiraConnectionError, JiraOperationError) as e:
                # Retry on connection errors and general operations errors
                last_exception = e
                retry_count += 1
                wait_time = self.retry_delay * (2 ** retry_count)
                logger.warning(f"Jira operation failed, retrying in {wait_time:.2f}s (attempt {retry_count}/{self.max_retries}): {str(e)}")
                time.sleep(wait_time)
            except (JiraAuthenticationError, JiraPermissionError, JiraNotFoundError) as e:
                # Don't retry auth, permission or not found errors
                raise e
            except Exception as e:
                # Unexpected errors
                logger.error(f"Unexpected error in Jira operation: {str(e)}")
                raise JiraOperationError(f"Unexpected error: {str(e)}")
        
        # If we got here, we ran out of retries
        if last_exception:
            logger.error(f"Failed after {self.max_retries} retries: {str(last_exception)}")
            raise last_exception
        else:
            raise JiraOperationError(f"Failed after {self.max_retries} retries")
    
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
        try:
            issue = self._with_retry(
                self.client.issue,
                issue_key,
                fields=fields
            )
            
            # Convert to dictionary
            if issue is None:
                # Fallback for type checking
                return {'key': issue_key, 'fields': {}}
            
            if hasattr(issue, 'raw'):
                return issue.raw
            else:
                # Create a dictionary with key attributes if raw not available
                return {
                    'key': getattr(issue, 'key', issue_key),
                    'fields': {
                        'summary': getattr(getattr(issue, 'fields', {}), 'summary', 'Unknown'),
                        'description': getattr(getattr(issue, 'fields', {}), 'description', ''),
                        'status': {
                            'name': getattr(getattr(getattr(issue, 'fields', {}), 'status', {}), 'name', 'Unknown')
                        },
                        'issuetype': {
                            'name': getattr(getattr(getattr(issue, 'fields', {}), 'issuetype', {}), 'name', 'Unknown')
                        }
                    }
                }
                
        except JIRAError as e:
            self._handle_jira_error(e)
            # This line is only reached if _handle_jira_error doesn't raise an exception
            # which should never happen, but needed for type checking
            return {'key': issue_key, 'fields': {}, 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error getting issue {issue_key}: {str(e)}")
            raise JiraOperationError(f"Failed to get issue {issue_key}: {str(e)}")
    
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
        try:
            issues = self._with_retry(
                self.client.search_issues,
                jql,
                startAt=start_at,
                maxResults=max_results,
                fields=fields
            )
            
            # Handle empty results
            if issues is None:
                return []
            
            # Convert to list of dictionaries
            result = []
            try:
                for issue in issues:
                    if hasattr(issue, 'raw'):
                        result.append(issue.raw)
                    else:
                        # Create a dictionary with key attributes if raw not available
                        result.append({
                            'key': getattr(issue, 'key', 'unknown'),
                            'fields': {
                                'summary': getattr(getattr(issue, 'fields', {}), 'summary', 'Unknown'),
                                'status': {
                                    'name': getattr(getattr(getattr(issue, 'fields', {}), 'status', {}), 'name', 'Unknown')
                                }
                            }
                        })
            except Exception as e:
                # If we can't iterate, return an empty list
                logger.warning(f"Could not iterate through search results: {str(e)}")
                return []
            
            return result
                
        except JIRAError as e:
            self._handle_jira_error(e)
            return []  # Needed for type checking, won't be reached in practice
        except Exception as e:
            logger.error(f"Unexpected error searching issues: {str(e)}")
            raise JiraOperationError(f"Failed to search issues: {str(e)}")
    
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
        try:
            comment = self._with_retry(
                self.client.add_comment,
                issue_key,
                body
            )
            
            # Handle None case (for type checking)
            if comment is None:
                return {
                    'id': 'unknown',
                    'body': body,
                    'author': {
                        'name': self.username if self.username else 'unknown',
                        'displayName': self.username if self.username else 'unknown'
                    },
                    'created': 'unknown',
                    'updated': 'unknown'
                }
            
            # Convert to dictionary
            return {
                'id': getattr(comment, 'id', 'unknown'),
                'body': getattr(comment, 'body', body),
                'author': {
                    'name': getattr(getattr(comment, 'author', {}), 'name', 'unknown'),
                    'displayName': getattr(getattr(comment, 'author', {}), 'displayName', 'unknown')
                },
                'created': getattr(comment, 'created', 'unknown'),
                'updated': getattr(comment, 'updated', 'unknown')
            }
                
        except JIRAError as e:
            self._handle_jira_error(e)
            # This will never be reached in practice, but needed for type checking
            return {'id': 'error', 'body': body, 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error adding comment to {issue_key}: {str(e)}")
            raise JiraOperationError(f"Failed to add comment to {issue_key}: {str(e)}")
    
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
        try:
            # Prepare transition data
            data: Dict[str, Any] = {
                'transition': {'id': transition_id}
            }
            
            if comment:
                # Using Any type to avoid type checker issues with complex nested dictionaries
                update_data: Dict[str, Any] = {
                    'comment': [{'add': {'body': comment}}]
                }
                data['update'] = update_data
                
            if fields:
                data['fields'] = fields
            
            self._with_retry(
                self.client.transition_issue,
                issue_key,
                data
            )
                
        except JIRAError as e:
            self._handle_jira_error(e)
        except Exception as e:
            logger.error(f"Unexpected error transitioning {issue_key}: {str(e)}")
            raise JiraOperationError(f"Failed to transition {issue_key}: {str(e)}")
    
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
        try:
            transitions = self._with_retry(
                self.client.transitions,
                issue_key
            )
            
            # Handle empty results
            if transitions is None:
                return []
            
            # Convert to list of dictionaries
            result = []
            try:
                for t in transitions:
                    if isinstance(t, dict):
                        result.append({
                            'id': t.get('id', 'unknown'),
                            'name': t.get('name', 'unknown'),
                            'to_status': t.get('to', {}).get('name', 'unknown')
                        })
                    else:
                        # Handle non-dict objects if they somehow appear
                        result.append({
                            'id': 'unknown',
                            'name': str(t),
                            'to_status': 'unknown'
                        })
            except Exception as e:
                logger.warning(f"Error processing transitions: {str(e)}")
                return []
            
            return result
                
        except JIRAError as e:
            self._handle_jira_error(e)
            return []  # For type checking
        except Exception as e:
            logger.error(f"Unexpected error getting transitions for {issue_key}: {str(e)}")
            raise JiraOperationError(f"Failed to get transitions for {issue_key}: {str(e)}")
    
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
        try:
            self._with_retry(
                self.client.assign_issue,
                issue_key,
                assignee
            )
                
        except JIRAError as e:
            self._handle_jira_error(e)
        except Exception as e:
            logger.error(f"Unexpected error assigning {issue_key}: {str(e)}")
            raise JiraOperationError(f"Failed to assign {issue_key}: {str(e)}")
