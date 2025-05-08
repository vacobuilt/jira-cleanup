"""
Formatting utilities for Jira Cleanup.

This module provides functions for formatting and transforming data
for different purposes within the application.
"""

import yaml
from typing import Dict, Any, Optional, List, Union


def format_ticket_as_yaml(ticket_data: Dict[str, Any]) -> str:
    """
    Format ticket data as YAML for LLM prompt.
    
    Args:
        ticket_data: Dictionary with ticket information
        
    Returns:
        YAML-formatted string
    """
    # Clean up any problematic values that might cause YAML serialization issues
    clean_data = {}
    
    # Extract key fields from the Jira raw data format
    if 'key' in ticket_data:
        clean_data['key'] = ticket_data['key']
    elif 'id' in ticket_data:
        clean_data['key'] = ticket_data['id']
    
    # Extract fields
    fields = ticket_data.get('fields', {})
    
    # Basic ticket information
    clean_data['summary'] = fields.get('summary', 'No summary')
    clean_data['description'] = fields.get('description', '')
    
    # Status information
    status = fields.get('status', {})
    clean_data['status'] = status.get('name', 'Unknown') if isinstance(status, dict) else str(status)
    
    # Issue type
    issue_type = fields.get('issuetype', {})
    clean_data['issue_type'] = issue_type.get('name', 'Unknown') if isinstance(issue_type, dict) else str(issue_type)
    
    # Project information
    project = fields.get('project', {})
    clean_data['project'] = project.get('key', 'Unknown') if isinstance(project, dict) else str(project)
    
    # Dates
    clean_data['created_date'] = fields.get('created', 'Unknown')
    clean_data['updated_date'] = fields.get('updated', 'Unknown')
    
    # User information
    clean_data['users'] = {
        'creator': get_user_display_name(fields.get('creator')),
        'reporter': get_user_display_name(fields.get('reporter')),
        'assignee': get_user_display_name(fields.get('assignee')) or 'Unassigned'
    }
    
    # Comments
    comments = []
    if 'comment' in fields and 'comments' in fields['comment']:
        for comment in fields['comment']['comments']:
            comments.append({
                'id': comment.get('id', 'Unknown'),
                'author': get_user_display_name(comment.get('author')),
                'created': comment.get('created', 'Unknown'),
                'updated': comment.get('updated', 'Unknown'),
                'body': comment.get('body', ''),
                'is_system_comment': '[Quiescent Ticket System]' in comment.get('body', '')
                or '[AUTOMATED QUIESCENCE ASSESSMENT]' in comment.get('body', '')
                or '[JIRA GOVERNANCE SYSTEM]' in comment.get('body', '')
            })
    
    clean_data['comments'] = comments
    clean_data['has_system_comment'] = any(c.get('is_system_comment', False) for c in comments)
    
    # Try to get changelog info if available
    if 'changelog' in ticket_data and 'histories' in ticket_data['changelog']:
        changelog_items = []
        for history in ticket_data['changelog']['histories']:
            for item in history.get('items', []):
                changelog_items.append({
                    'date': history.get('created', 'Unknown'),
                    'author': get_user_display_name(history.get('author')),
                    'field': item.get('field', 'Unknown'),
                    'from_value': item.get('fromString', ''),
                    'to_value': item.get('toString', '')
                })
        clean_data['changelog'] = changelog_items
    
    # Labels and components
    clean_data['labels'] = fields.get('labels', [])
    components = fields.get('components', [])
    clean_data['components'] = [c.get('name', str(c)) for c in components] if isinstance(components, list) else []
    
    # Convert to YAML
    return yaml.dump(clean_data, default_flow_style=False, sort_keys=False)


def get_user_display_name(user_data: Optional[Dict[str, Any]]) -> str:
    """
    Extract user display name from user data.
    
    Args:
        user_data: User data dictionary from Jira
        
    Returns:
        Display name or empty string
    """
    if not user_data:
        return ''
    
    if isinstance(user_data, dict):
        return user_data.get('displayName', user_data.get('name', 'Unknown'))
    
    return str(user_data)
