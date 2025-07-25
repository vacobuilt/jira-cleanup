"""
Quiescent analysis result entity.

This module contains the QuiescentResult data structure that holds
quiescence-specific assessment information with natural terminology
and fields specific to quiescence analysis.
"""

from dataclasses import dataclass
from typing import Dict, Any
from .base_result import BaseResult


@dataclass
class QuiescentResult(BaseResult):
    """Result structure for quiescence analysis."""
    
    is_quiescent: bool
    staleness_score: float  # 0-10 scale indicating how stale the ticket is
    inactivity_days: int    # Number of days without activity
    justification: str      # Detailed explanation of quiescence assessment
    responsible_party: str  # Person responsible for the ticket
    suggested_action: str   # Recommended action to take
    suggested_deadline: str # When action should be taken
    planned_comment: str    # Comment to add to ticket
    
    def needs_action(self) -> bool:
        """Quiescent tickets need action."""
        return self.is_quiescent
    
    def get_planned_comment(self) -> str:
        """Get the comment for quiescent tickets."""
        return self.planned_comment
    
    def get_responsible_party(self) -> str:
        """Get responsible party."""
        return self.responsible_party
    
    def get_suggested_action(self) -> str:
        """Get suggested action."""
        return self.suggested_action
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'is_quiescent': self.is_quiescent,
            'staleness_score': self.staleness_score,
            'inactivity_days': self.inactivity_days,
            'justification': self.justification,
            'responsible_party': self.responsible_party,
            'suggested_action': self.suggested_action,
            'suggested_deadline': self.suggested_deadline,
            'planned_comment': self.planned_comment
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuiescentResult':
        """Create from dictionary."""
        return cls(
            is_quiescent=data.get('is_quiescent', False),
            staleness_score=data.get('staleness_score', 0.0),
            inactivity_days=data.get('inactivity_days', 0),
            justification=data.get('justification', 'No justification provided'),
            responsible_party=data.get('responsible_party', 'Unknown'),
            suggested_action=data.get('suggested_action', 'No action suggested'),
            suggested_deadline=data.get('suggested_deadline', 'No deadline suggested'),
            planned_comment=data.get('planned_comment', 'No comment generated')
        )
    
    @classmethod
    def default(cls) -> 'QuiescentResult':
        """Create default (failed) result."""
        return cls(
            is_quiescent=False,
            staleness_score=0.0,
            inactivity_days=0,
            justification="Failed to assess ticket",
            responsible_party="Unknown",
            suggested_action="None",
            suggested_deadline="None",
            planned_comment="Failed to generate comment"
        )
