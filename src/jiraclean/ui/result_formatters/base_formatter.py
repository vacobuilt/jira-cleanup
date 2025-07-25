"""
Base formatter interface for analysis results.

This module defines the common interface that all result formatters
must implement, enabling the UI to work generically with any
analyzer type.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from rich.panel import Panel
from rich.table import Table


class BaseFormatter(ABC):
    """Base interface for all result formatters."""
    
    @abstractmethod
    def format_ticket_card(self, ticket_data: Dict[str, Any], result) -> Panel:
        """
        Format a ticket card with analysis result.
        
        Args:
            ticket_data: Dictionary containing ticket information
            result: Analysis result object
            
        Returns:
            Rich Panel with formatted ticket information
        """
        pass
    
    @abstractmethod
    def format_assessment_panel(self, result) -> Panel:
        """
        Format an assessment panel for the result.
        
        Args:
            result: Analysis result object
            
        Returns:
            Rich Panel with formatted assessment information
        """
        pass
    
    @abstractmethod
    def format_summary_stats(self, stats: Dict[str, Any]) -> Table:
        """
        Format summary statistics table.
        
        Args:
            stats: Dictionary containing processing statistics
            
        Returns:
            Rich Table with formatted statistics
        """
        pass
    
    @abstractmethod
    def get_status_text(self, result) -> str:
        """
        Get status text for display (e.g., 'QUIESCENT', 'HIGH_QUALITY').
        
        Args:
            result: Analysis result object
            
        Returns:
            Status text string
        """
        pass
    
    @abstractmethod
    def get_status_style(self, result) -> str:
        """
        Get Rich style for status display.
        
        Args:
            result: Analysis result object
            
        Returns:
            Rich style string
        """
        pass
    
    @abstractmethod
    def get_border_style(self, result) -> str:
        """
        Get Rich border style for panels.
        
        Args:
            result: Analysis result object
            
        Returns:
            Rich border style string
        """
        pass
