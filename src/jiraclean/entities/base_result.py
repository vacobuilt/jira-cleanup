"""
Base interface for all analysis results.

This module defines the common interface that all analysis result types
must implement, enabling the framework to work generically with any
analyzer type.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseResult(ABC):
    """Base interface for all analysis results."""
    
    @abstractmethod
    def needs_action(self) -> bool:
        """
        Determine if this result requires action to be taken.
        
        Returns:
            True if action should be taken based on this result
        """
        pass
    
    @abstractmethod
    def get_planned_comment(self) -> str:
        """
        Get the comment that should be added to the ticket.
        
        Returns:
            Comment text to add to the ticket
        """
        pass
    
    @abstractmethod
    def get_responsible_party(self) -> str:
        """
        Get the party responsible for addressing this result.
        
        Returns:
            Name or identifier of responsible party
        """
        pass
    
    @abstractmethod
    def get_suggested_action(self) -> str:
        """
        Get the suggested action for this result.
        
        Returns:
            Description of suggested action
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary for serialization.
        
        Returns:
            Dictionary representation of the result
        """
        pass
