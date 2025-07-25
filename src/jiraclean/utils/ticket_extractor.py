"""
Unified ticket data extraction utilities.

This module provides a single source of truth for extracting and formatting
ticket data from Jira's raw API responses, eliminating duplication across
the codebase.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class TicketDataExtractor:
    """
    Unified ticket data extractor for consistent field access across the application.
    
    This class provides a single source of truth for extracting ticket data
    from Jira's raw API responses, eliminating the scattered extraction logic
    that was duplicated across multiple files.
    """
    
    def __init__(self, raw_data: Dict[str, Any]):
        """
        Initialize the extractor with raw Jira ticket data.
        
        Args:
            raw_data: Raw ticket data from Jira API
        """
        self.raw_data = raw_data
        self.fields = raw_data.get('fields', {})
    
    @property
    def key(self) -> str:
        """Get the ticket key (e.g., 'PROJ-123')."""
        return self.raw_data.get('key', 'UNKNOWN')
    
    @property
    def summary(self) -> str:
        """Get the ticket summary/title."""
        return self.fields.get('summary', 'No summary available')
    
    @property
    def description(self) -> str:
        """Get the ticket description."""
        return self.fields.get('description', '')
    
    @property
    def status(self) -> str:
        """Get the ticket status name."""
        return self._safe_get_name(self.fields.get('status'))
    
    @property
    def issue_type(self) -> str:
        """Get the issue type name."""
        return self._safe_get_name(self.fields.get('issuetype'))
    
    @property
    def priority(self) -> str:
        """Get the priority name."""
        return self._safe_get_name(self.fields.get('priority'))
    
    @property
    def project_key(self) -> str:
        """Get the project key."""
        project = self.fields.get('project', {})
        if isinstance(project, dict):
            return project.get('key', 'Unknown')
        return str(project) if project else 'Unknown'
    
    @property
    def created_date(self) -> str:
        """Get the creation date."""
        return self.fields.get('created', 'Unknown')
    
    @property
    def updated_date(self) -> str:
        """Get the last updated date."""
        return self.fields.get('updated', 'Unknown')
    
    @property
    def assignee(self) -> Dict[str, str]:
        """Get assignee information."""
        return self._extract_user_data(self.fields.get('assignee'))
    
    @property
    def reporter(self) -> Dict[str, str]:
        """Get reporter information."""
        return self._extract_user_data(self.fields.get('reporter'))
    
    @property
    def creator(self) -> Dict[str, str]:
        """Get creator information."""
        return self._extract_user_data(self.fields.get('creator'))
    
    @property
    def labels(self) -> List[str]:
        """Get ticket labels."""
        return self.fields.get('labels', [])
    
    @property
    def components(self) -> List[str]:
        """Get ticket components."""
        components = self.fields.get('components', [])
        if isinstance(components, list):
            return [c.get('name', str(c)) for c in components if c]
        return []
    
    @property
    def comments(self) -> List[Dict[str, Any]]:
        """Get ticket comments with metadata."""
        comments = []
        comment_data = self.fields.get('comment', {})
        
        if isinstance(comment_data, dict) and 'comments' in comment_data:
            for comment in comment_data['comments']:
                comments.append({
                    'id': comment.get('id', 'Unknown'),
                    'author': self._extract_user_data(comment.get('author')),
                    'created': comment.get('created', 'Unknown'),
                    'updated': comment.get('updated', 'Unknown'),
                    'body': comment.get('body', ''),
                    'is_system_comment': self._is_system_comment(comment.get('body', ''))
                })
        
        return comments
    
    @property
    def has_system_comment(self) -> bool:
        """Check if ticket has any system-generated comments."""
        return any(c.get('is_system_comment', False) for c in self.comments)
    
    @property
    def changelog(self) -> List[Dict[str, Any]]:
        """Get ticket changelog entries."""
        changelog_items = []
        changelog_data = self.raw_data.get('changelog', {})
        
        if isinstance(changelog_data, dict) and 'histories' in changelog_data:
            for history in changelog_data['histories']:
                for item in history.get('items', []):
                    changelog_items.append({
                        'date': history.get('created', 'Unknown'),
                        'author': self._extract_user_data(history.get('author')),
                        'field': item.get('field', 'Unknown'),
                        'from_value': item.get('fromString', ''),
                        'to_value': item.get('toString', '')
                    })
        
        return changelog_items
    
    def get_user_field(self, field_name: str) -> Dict[str, str]:
        """
        Get a user field by name.
        
        Args:
            field_name: Name of the user field (e.g., 'assignee', 'reporter')
            
        Returns:
            User data dictionary
        """
        user_data = self.fields.get(field_name)
        return self._extract_user_data(user_data)
    
    def get_custom_field(self, field_id: str) -> Any:
        """
        Get a custom field value by ID.
        
        Args:
            field_id: Custom field ID (e.g., 'customfield_10001')
            
        Returns:
            Custom field value or None
        """
        return self.fields.get(field_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a standardized dictionary format.
        
        Returns:
            Dictionary with all standard ticket fields
        """
        return {
            'key': self.key,
            'summary': self.summary,
            'description': self.description,
            'status': self.status,
            'issue_type': self.issue_type,
            'priority': self.priority,
            'project': self.project_key,
            'created_date': self.created_date,
            'updated_date': self.updated_date,
            'assignee': self.assignee,
            'reporter': self.reporter,
            'creator': self.creator,
            'labels': self.labels,
            'components': self.components,
            'comments': self.comments,
            'has_system_comment': self.has_system_comment,
            'changelog': self.changelog
        }
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        """
        Convert to a dictionary optimized for YAML serialization.
        
        Returns:
            Dictionary formatted for YAML output
        """
        return {
            'key': self.key,
            'summary': self.summary,
            'description': self.description,
            'status': self.status,
            'issue_type': self.issue_type,
            'project': self.project_key,
            'created_date': self.created_date,
            'updated_date': self.updated_date,
            'users': {
                'creator': self.creator.get('display_name', ''),
                'reporter': self.reporter.get('display_name', ''),
                'assignee': self.assignee.get('display_name', '') or 'Unassigned'
            },
            'comments': self.comments,
            'has_system_comment': self.has_system_comment,
            'changelog': self.changelog,
            'labels': self.labels,
            'components': self.components
        }
    
    def to_ui_dict(self) -> Dict[str, str]:
        """
        Convert to a dictionary optimized for UI display.
        
        Returns:
            Dictionary formatted for UI components
        """
        return {
            'key': self.key,
            'type': self.issue_type,
            'status': self.status,
            'summary': self.summary,
            'priority': self.priority,
            'assignee': self.assignee.get('display_name', 'Unassigned'),
            'reporter': self.reporter.get('display_name', 'Unknown'),
            'created': self.created_date,
            'updated': self.updated_date
        }
    
    def _safe_get_name(self, field_data: Any) -> str:
        """
        Safely extract name from Jira field data.
        
        Args:
            field_data: Field data that may be dict, string, or None
            
        Returns:
            Field name or 'Unknown'
        """
        if isinstance(field_data, dict):
            return field_data.get('name', 'Unknown')
        return str(field_data) if field_data else 'Unknown'
    
    def _extract_user_data(self, user_data: Any) -> Dict[str, str]:
        """
        Extract standardized user information.
        
        Args:
            user_data: User data from Jira (can be dict, string, or None)
            
        Returns:
            Standardized user data dictionary
        """
        if not user_data:
            return {
                'display_name': '',
                'email': '',
                'username': '',
                'account_id': ''
            }
        
        if isinstance(user_data, dict):
            return {
                'display_name': user_data.get('displayName', ''),
                'email': user_data.get('emailAddress', ''),
                'username': user_data.get('name', ''),
                'account_id': user_data.get('accountId', '')
            }
        
        # If it's a string, assume it's a display name
        return {
            'display_name': str(user_data),
            'email': '',
            'username': '',
            'account_id': ''
        }
    
    def _is_system_comment(self, comment_body: str) -> bool:
        """
        Check if a comment is system-generated.
        
        Args:
            comment_body: Comment text
            
        Returns:
            True if comment appears to be system-generated
        """
        system_markers = [
            '[Quiescent Ticket System]',
            '[AUTOMATED QUIESCENCE ASSESSMENT]',
            '[JIRA GOVERNANCE SYSTEM]'
        ]
        
        return any(marker in comment_body for marker in system_markers)


def format_user_for_display(user_data: Dict[str, str], default: str = "Unknown") -> str:
    """
    Format user data for display purposes.
    
    Args:
        user_data: User data dictionary from TicketDataExtractor
        default: Default value if no user data available
        
    Returns:
        Formatted user string for display
    """
    if not user_data or not any(user_data.values()):
        return default
    
    # Priority order: display_name > email > username
    display_name = user_data.get('display_name', '').strip()
    email = user_data.get('email', '').strip()
    username = user_data.get('username', '').strip()
    
    if display_name:
        return display_name
    elif email:
        return email
    elif username:
        return username
    else:
        return default


def format_user_for_ui(user_data: Dict[str, str]) -> str:
    """
    Format user data specifically for UI display (returns 'Unassigned' for empty).
    
    Args:
        user_data: User data dictionary from TicketDataExtractor
        
    Returns:
        Formatted user string for UI
    """
    return format_user_for_display(user_data, "Unassigned")


def format_user_for_yaml(user_data: Dict[str, str]) -> str:
    """
    Format user data specifically for YAML output (returns empty string for empty).
    
    Args:
        user_data: User data dictionary from TicketDataExtractor
        
    Returns:
        Formatted user string for YAML
    """
    return format_user_for_display(user_data, "")
