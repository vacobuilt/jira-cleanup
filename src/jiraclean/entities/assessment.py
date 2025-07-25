"""
Assessment result entity.

This module contains the AssessmentResult data structure that is shared
across different layers of the application.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class AssessmentResult:
    """Structure to hold LLM assessment results for a ticket."""
    
    is_quiescent: bool
    justification: str
    responsible_party: str
    suggested_action: str
    suggested_deadline: str
    planned_comment: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssessmentResult':
        """
        Create an AssessmentResult from a dictionary.
        
        Args:
            data: Dictionary with assessment data
            
        Returns:
            AssessmentResult instance
        """
        return cls(
            is_quiescent=data.get('is_quiescent', False),
            justification=data.get('justification', 'No justification provided'),
            responsible_party=data.get('responsible_party', 'Unknown'),
            suggested_action=data.get('suggested_action', 'No action suggested'),
            suggested_deadline=data.get('suggested_deadline', 'No deadline suggested'),
            planned_comment=data.get('planned_comment', 'No comment generated')
        )
    
    @classmethod
    def default(cls) -> 'AssessmentResult':
        """
        Create a default (failed) assessment result.
        
        Returns:
            AssessmentResult instance with default values
        """
        return cls(
            is_quiescent=False,
            justification="Failed to assess ticket",
            responsible_party="Unknown",
            suggested_action="None",
            suggested_deadline="None",
            planned_comment="Failed to generate comment"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert assessment to dictionary.
        
        Returns:
            Dictionary representation of the assessment
        """
        return {
            'is_quiescent': self.is_quiescent,
            'justification': self.justification,
            'responsible_party': self.responsible_party,
            'suggested_action': self.suggested_action,
            'suggested_deadline': self.suggested_deadline,
            'planned_comment': self.planned_comment
        }
