"""
Assessment entity for Jira Cleanup.

This module defines the Assessment domain entity, which represents the results of
evaluating a ticket for quiescence using an LLM or other assessment mechanism.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass(frozen=True)
class Assessment:
    """
    Value object representing the results of a ticket assessment.
    
    This is immutable (frozen) as it represents the outcome of an evaluation
    at a specific point in time.
    """
    
    is_quiescent: bool
    justification: str
    responsible_party: str
    suggested_action: str
    suggested_deadline: str
    planned_comment: str
    assessment_date: datetime = None
    
    def __post_init__(self):
        """Initialize any derived properties after construction."""
        # Set assessment date to current time if not provided
        if self.assessment_date is None:
            # Use object.__setattr__ since this is a frozen dataclass
            object.__setattr__(self, 'assessment_date', datetime.now())
    
    @property
    def deadline_date(self) -> Optional[datetime]:
        """
        Calculate the actual deadline date based on the suggested deadline.
        
        Returns:
            Datetime object representing the deadline, or None if not parseable
        """
        try:
            # Try to handle common deadline formats
            if 'day' in self.suggested_deadline.lower() or 'week' in self.suggested_deadline.lower():
                # Parse "X days" or "X weeks"
                parts = self.suggested_deadline.lower().split()
                if len(parts) >= 2:
                    try:
                        value = int(parts[0])
                        unit = parts[1]
                        
                        if 'day' in unit:
                            return self.assessment_date + timedelta(days=value)
                        elif 'week' in unit:
                            return self.assessment_date + timedelta(weeks=value)
                        elif 'month' in unit:
                            # Approximate months as 30 days
                            return self.assessment_date + timedelta(days=value * 30)
                    except (ValueError, IndexError):
                        pass
            
            # Try to parse as a date string
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
                try:
                    return datetime.strptime(self.suggested_deadline, fmt)
                except ValueError:
                    continue
                    
            return None
        except Exception:
            return None
    
    @property
    def is_warning_needed(self) -> bool:
        """
        Determine if a closing warning is needed based on assessment.
        
        Returns:
            True if a closing warning should be included, False otherwise
        """
        return 'may be closed' in self.planned_comment.lower() or 'will be closed' in self.planned_comment.lower()
    
    @property
    def is_expired(self) -> bool:
        """
        Check if the assessment is expired and should be refreshed.
        
        An assessment is considered expired after 7 days.
        
        Returns:
            True if the assessment is expired, False otherwise
        """
        age = datetime.now() - self.assessment_date
        return age.days > 7
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Assessment':
        """
        Create an Assessment from a dictionary.
        
        Args:
            data: Dictionary with assessment data
            
        Returns:
            Assessment instance
        """
        return cls(
            is_quiescent=data.get('is_quiescent', False),
            justification=data.get('justification', 'No justification provided'),
            responsible_party=data.get('responsible_party', 'Unknown'),
            suggested_action=data.get('suggested_action', 'No action suggested'),
            suggested_deadline=data.get('suggested_deadline', 'No deadline suggested'),
            planned_comment=data.get('planned_comment', 'No comment generated'),
            assessment_date=data.get('assessment_date', datetime.now())
        )
