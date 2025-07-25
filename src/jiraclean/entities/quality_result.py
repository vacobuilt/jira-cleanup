"""
Quality analysis result entity.

This module contains the QualityResult data structure that holds
quality-specific assessment information with natural terminology
and fields specific to quality analysis.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from jiraclean.entities.base_result import BaseResult


@dataclass
class QualityResult(BaseResult):
    """Result structure for quality analysis."""
    
    needs_improvement: bool
    quality_score: int  # 1-10 scale indicating ticket quality
    quality_assessment: str  # Detailed explanation of quality assessment
    improvement_suggestions: List[str]  # List of specific improvements needed
    responsible_party: str  # Person responsible for the ticket
    suggested_deadline: str # When improvements should be made
    planned_comment: str    # Comment to add to ticket
    
    def needs_action(self) -> bool:
        """Quality tickets that need improvement require action."""
        return self.needs_improvement
    
    def get_planned_comment(self) -> str:
        """Get the comment for quality tickets."""
        return self.planned_comment
    
    def get_responsible_party(self) -> str:
        """Get responsible party."""
        return self.responsible_party
    
    def get_suggested_action(self) -> str:
        """Get suggested action."""
        if self.improvement_suggestions:
            return f"Improve ticket quality: {', '.join(self.improvement_suggestions[:2])}"
        return "Improve ticket quality"
    
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'needs_improvement': self.needs_improvement,
            'quality_score': self.quality_score,
            'quality_assessment': self.quality_assessment,
            'improvement_suggestions': self.improvement_suggestions,
            'responsible_party': self.responsible_party,
            'suggested_deadline': self.suggested_deadline,
            'planned_comment': self.planned_comment
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QualityResult':
        """Create from dictionary."""
        return cls(
            needs_improvement=data.get('needs_improvement', False),
            quality_score=data.get('quality_score', 5),
            quality_assessment=data.get('quality_assessment', 'No assessment provided'),
            improvement_suggestions=data.get('improvement_suggestions', []),
            responsible_party=data.get('responsible_party', 'Unknown'),
            suggested_deadline=data.get('suggested_deadline', 'No deadline suggested'),
            planned_comment=data.get('planned_comment', 'No comment generated')
        )
    
    @classmethod
    def default(cls) -> 'QualityResult':
        """Create default (failed) result."""
        return cls(
            needs_improvement=False,
            quality_score=0,
            quality_assessment="Failed to assess ticket quality",
            improvement_suggestions=[],
            responsible_party="Unknown",
            suggested_deadline="None",
            planned_comment="Failed to generate comment"
        )
