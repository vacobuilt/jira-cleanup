"""
Type conversion utilities for LLM response parsing.

This module provides robust type conversion functions that handle
various LLM output formats (int, float, string) and convert them
to the expected Python types with proper error handling.
"""

from typing import List, Optional, Any


def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """
    Safely convert any value to float.
    
    Handles int, float, and string inputs from LLM responses.
    
    Args:
        value: The value to convert (int, float, string, or other)
        default: Default value to return if conversion fails
        
    Returns:
        float: The converted value or default if conversion fails
    """
    if isinstance(value, (int, float)):
        return float(value)
    elif isinstance(value, str):
        try:
            return float(value.strip())
        except (ValueError, TypeError):
            return default
    else:
        return default


def safe_int_conversion(value: Any, default: int = 0) -> int:
    """
    Safely convert any value to int.
    
    Handles int, float, and string inputs from LLM responses.
    
    Args:
        value: The value to convert (int, float, string, or other)
        default: Default value to return if conversion fails
        
    Returns:
        int: The converted value or default if conversion fails
    """
    if isinstance(value, int):
        return value
    elif isinstance(value, float):
        return int(value)
    elif isinstance(value, str):
        try:
            # Handle both int strings and float strings
            return int(float(value.strip()))
        except (ValueError, TypeError):
            return default
    else:
        return default


def safe_list_conversion(value: Any, default: Optional[List[str]] = None) -> List[str]:
    """
    Safely convert any value to list of strings.
    
    Handles list, string, and other inputs from LLM responses.
    
    Args:
        value: The value to convert (list, string, or other)
        default: Default value to return if conversion fails
        
    Returns:
        List[str]: The converted list or default if conversion fails
    """
    if default is None:
        default = []
    
    if isinstance(value, list):
        # Ensure all items are strings
        return [str(item) for item in value]
    elif isinstance(value, str):
        # If it's a string, split by common delimiters
        if not value.strip():
            return default
        # Try multiple delimiters
        for delimiter in [',', ';', '\n', '|']:
            if delimiter in value:
                return [s.strip() for s in value.split(delimiter) if s.strip()]
        # If no delimiters found, return as single item
        return [value.strip()]
    else:
        return default


def safe_bool_conversion(value: Any, default: bool = False) -> bool:
    """
    Safely convert any value to bool.
    
    Handles bool, string, and other inputs from LLM responses.
    
    Args:
        value: The value to convert (bool, string, or other)
        default: Default value to return if conversion fails
        
    Returns:
        bool: The converted value or default if conversion fails
    """
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        # Handle common string representations of boolean values
        lower_value = value.strip().lower()
        if lower_value in ('true', '1', 'yes', 'on'):
            return True
        elif lower_value in ('false', '0', 'no', 'off'):
            return False
        else:
            return default
    elif isinstance(value, (int, float)):
        return bool(value)
    else:
        return default
