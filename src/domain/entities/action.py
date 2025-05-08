"""
Action recommendation entity for Jira Cleanup.

This module defines the ActionRecommendation domain entity, which represents
the actions that should be taken based on ticket assessment.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, Any, Optional, List


class ActionType(Enum):
    """Enumeration of possible action types."""
    
    COMMENT = auto()
    STATUS_TRANSITION = auto()
    ASSIGNMENT = auto()
    PRIORITY_CHANGE = auto()
    LABEL_UPDATE = auto()
    CLOSE = auto()
    NOTIFICATION = auto()
    NO_ACTION = auto()
    
    def __str__(self) -> str:
        """Convert enum to string, removing the class prefix."""
        return self.name.lower().replace('_', ' ')


class ActionStatus(Enum):
    """Enumeration of action statuses."""
    
    PENDING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()
    
    def __str__(self) -> str:
        """Convert enum to string."""
        return self.name.lower()


@dataclass
class ActionRecommendation:
    """
    Value object representing a recommended action to take on a ticket.
    
    This class encapsulates an action that should be taken as a result
    of ticket assessment, such as adding a comment or changing status.
    """
    
    ticket_key: str
    type: ActionType
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    status: ActionStatus = ActionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    @property
    def is_pending(self) -> bool:
        """Check if the action is still pending."""
        return self.status == ActionStatus.PENDING
    
    @property
    def is_completed(self) -> bool:
        """Check if the action has been completed successfully."""
        return self.status == ActionStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if the action has failed."""
        return self.status == ActionStatus.FAILED
    
    @property
    def comment_text(self) -> Optional[str]:
        """Get the comment text if this is a comment action."""
        if self.type == ActionType.COMMENT:
            return self.details.get('comment_text')
        return None
    
    @property
    def target_status(self) -> Optional[str]:
        """Get the target status if this is a status transition action."""
        if self.type == ActionType.STATUS_TRANSITION:
            return self.details.get('target_status')
        return None
    
    @property
    def assignee(self) -> Optional[str]:
        """Get the assignee if this is an assignment action."""
        if self.type == ActionType.ASSIGNMENT:
            return self.details.get('assignee')
        return None
    
    def mark_completed(self) -> None:
        """Mark this action as completed."""
        self.status = ActionStatus.COMPLETED
        self.executed_at = datetime.now()
    
    def mark_failed(self, error_message: str) -> None:
        """
        Mark this action as failed.
        
        Args:
            error_message: Description of what went wrong
        """
        self.status = ActionStatus.FAILED
        self.error_message = error_message
        self.executed_at = datetime.now()
    
    def mark_skipped(self, reason: str) -> None:
        """
        Mark this action as skipped.
        
        Args:
            reason: Reason for skipping
        """
        self.status = ActionStatus.SKIPPED
        self.error_message = reason
        self.executed_at = datetime.now()
    
    @classmethod
    def create_comment_action(cls, ticket_key: str, comment_text: str) -> 'ActionRecommendation':
        """
        Factory method to create a comment action.
        
        Args:
            ticket_key: Key of the ticket to comment on
            comment_text: Text of the comment to add
            
        Returns:
            ActionRecommendation for adding a comment
        """
        return cls(
            ticket_key=ticket_key,
            type=ActionType.COMMENT,
            description=f"Add comment to {ticket_key}",
            details={
                'comment_text': comment_text
            }
        )
    
    @classmethod
    def create_transition_action(cls, ticket_key: str, target_status: str) -> 'ActionRecommendation':
        """
        Factory method to create a status transition action.
        
        Args:
            ticket_key: Key of the ticket to transition
            target_status: Status to transition to
            
        Returns:
            ActionRecommendation for changing ticket status
        """
        return cls(
            ticket_key=ticket_key,
            type=ActionType.STATUS_TRANSITION,
            description=f"Transition {ticket_key} to {target_status}",
            details={
                'target_status': target_status
            }
        )
    
    @classmethod
    def create_assignment_action(cls, ticket_key: str, assignee: str) -> 'ActionRecommendation':
        """
        Factory method to create an assignment action.
        
        Args:
            ticket_key: Key of the ticket to assign
            assignee: Username to assign the ticket to
            
        Returns:
            ActionRecommendation for assigning a ticket
        """
        return cls(
            ticket_key=ticket_key,
            type=ActionType.ASSIGNMENT,
            description=f"Assign {ticket_key} to {assignee}",
            details={
                'assignee': assignee
            }
        )
    
    @classmethod
    def create_no_action(cls, ticket_key: str, reason: str) -> 'ActionRecommendation':
        """
        Factory method to create a no-action recommendation.
        
        Args:
            ticket_key: Key of the ticket
            reason: Reason no action is needed
            
        Returns:
            ActionRecommendation indicating no action needed
        """
        return cls(
            ticket_key=ticket_key,
            type=ActionType.NO_ACTION,
            description=f"No action needed for {ticket_key}",
            details={
                'reason': reason
            }
        )
    
    @classmethod
    def from_assessment(cls, ticket_key: str, assessment) -> List['ActionRecommendation']:
        """
        Create action recommendations based on a ticket assessment.
        
        Args:
            ticket_key: Key of the ticket
            assessment: Assessment result
            
        Returns:
            List of ActionRecommendation objects
        """
        actions = []
        
        # Always add a comment if the ticket is quiescent
        if assessment.is_quiescent and assessment.planned_comment:
            actions.append(cls.create_comment_action(
                ticket_key=ticket_key,
                comment_text=assessment.planned_comment
            ))
        
        # Create a no-action recommendation if not quiescent
        if not assessment.is_quiescent:
            actions.append(cls.create_no_action(
                ticket_key=ticket_key,
                reason=assessment.justification
            ))
        
        return actions
