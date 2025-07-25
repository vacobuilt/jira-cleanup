"""
Formatting utilities for Jira Cleanup.

This module provides functions for formatting and transforming data
for different purposes within the application.
"""

import yaml
from typing import Dict, Any, Optional, List, Union

from jiraclean.utils.ticket_extractor import TicketDataExtractor, format_user_for_yaml


def format_ticket_as_yaml(ticket_data: Dict[str, Any]) -> str:
    """
    Format ticket data as YAML for LLM prompt using TicketDataExtractor.
    
    Args:
        ticket_data: Dictionary with ticket information
        
    Returns:
        YAML-formatted string
    """
    extractor = TicketDataExtractor(ticket_data)
    clean_data = extractor.to_yaml_dict()
    
    # Convert to YAML
    return yaml.dump(clean_data, default_flow_style=False, sort_keys=False)


def get_user_display_name(user_data: Optional[Dict[str, Any]]) -> str:
    """
    Extract user display name from user data.
    
    Args:
        user_data: User data dictionary from Jira
        
    Returns:
        Display name or empty string
        
    Note: This function is deprecated. Use TicketDataExtractor and 
    format_user_for_yaml() instead for new code.
    """
    if not user_data:
        return ''
    
    if isinstance(user_data, dict):
        return user_data.get('displayName', user_data.get('name', 'Unknown'))
    
    return str(user_data)
