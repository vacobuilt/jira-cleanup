"""
Quiescence evaluation domain service.

This module contains the domain service responsible for evaluating whether a ticket
is quiescent based on business rules.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any, Optional

from jiraclean.domain.entities.ticket import Ticket


@dataclass
class QuiescenceRule:
    """Value object representing a rule for evaluating ticket quiescence."""
    
    name: str
    description: str
    weight: float = 1.0
    
    def evaluate(self, ticket: Ticket) -> Tuple[bool, str]:
        """
        Evaluate the rule for a given ticket.
        
        Args:
            ticket: The ticket to evaluate
            
        Returns:
            Tuple of (passed, reason)
        """
        raise NotImplementedError("Rule evaluation must be implemented by subclasses")


@dataclass
class StaleTicketRule(QuiescenceRule):
    """Rule that checks if a ticket hasn't been updated in a while."""
    
    threshold_days: int = 14
    
    def evaluate(self, ticket: Ticket) -> Tuple[bool, str]:
        """Check if ticket is stale based on the threshold."""
        is_stale = ticket.days_since_update >= self.threshold_days
        
        if is_stale:
            return True, f"Ticket has not been updated in {ticket.days_since_update} days (threshold: {self.threshold_days})"
        else:
            return False, f"Ticket was updated {ticket.days_since_update} days ago, which is within the {self.threshold_days} day threshold"


@dataclass
class NoRecentActivityRule(QuiescenceRule):
    """Rule that checks if there's been no recent activity on a ticket."""
    
    threshold_days: int = 7
    
    def evaluate(self, ticket: Ticket) -> Tuple[bool, str]:
        """Check if there's been recent activity."""
        has_activity = ticket.has_recent_activity(self.threshold_days)
        
        if not has_activity:
            return True, f"No activity on this ticket in the last {self.threshold_days} days"
        else:
            return False, f"Ticket has had activity within the last {self.threshold_days} days"


@dataclass
class UnresolvedQuestionsRule(QuiescenceRule):
    """Rule that checks if a ticket has unanswered questions."""
    
    question_indicators: List[str] = field(default_factory=lambda: [
        "?", "question", "can you", "could you", "would you", "will you", 
        "please clarify", "please explain", "what is", "how to"
    ])
    
    def evaluate(self, ticket: Ticket) -> Tuple[bool, str]:
        """Check for unanswered questions in comments."""
        # Skip if no comments
        if not ticket.comments:
            return False, "No comments to check for questions"
        
        # Sort comments by date
        sorted_comments = sorted(ticket.comments, key=lambda c: c.created_date)
        
        # Check if the last comment contains a question
        last_comment = sorted_comments[-1]
        
        # Check if the last comment has question indicators
        has_question = any(indicator in last_comment.body.lower() for indicator in self.question_indicators)
        
        if has_question:
            return True, f"Last comment from {last_comment.author} appears to contain unanswered questions"
        
        return False, "No unanswered questions detected in the latest comments"


@dataclass
class OpenWithoutAssigneeRule(QuiescenceRule):
    """Rule that checks if an open ticket doesn't have an assignee."""
    
    def evaluate(self, ticket: Ticket) -> Tuple[bool, str]:
        """Check if the ticket is open but unassigned."""
        if ticket.is_closed():
            return False, "Ticket is closed, so assignee status is not relevant"
        
        if not ticket.is_assigned():
            return True, "Ticket is open but has no assignee"
        
        return False, f"Ticket is assigned to {ticket.assignee}"


@dataclass
class AgedTicketRule(QuiescenceRule):
    """Rule that checks if a ticket is very old."""
    
    age_threshold_days: int = 90  # 3 months
    
    def evaluate(self, ticket: Ticket) -> Tuple[bool, str]:
        """Check if the ticket is very old."""
        is_old = ticket.days_since_creation >= self.age_threshold_days
        
        if is_old and not ticket.is_closed():
            return True, f"Ticket is {ticket.days_since_creation} days old and still open"
        
        return False, f"Ticket age ({ticket.days_since_creation} days) doesn't indicate quiescence"


class QuiescenceEvaluator:
    """
    Domain service for evaluating ticket quiescence.
    
    This service applies a set of business rules to determine if a ticket
    is quiescent and provides detailed explanations.
    """
    
    def __init__(self, rules: Optional[List[QuiescenceRule]] = None):
        """
        Initialize with rules for quiescence evaluation.
        
        Args:
            rules: Optional list of rules to apply, defaults to standard rules
        """
        self.rules = rules or self._default_rules()
    
    def _default_rules(self) -> List[QuiescenceRule]:
        """Create the default set of quiescence rules."""
        return [
            StaleTicketRule(
                name="stale_ticket",
                description="Ticket hasn't been updated recently",
                threshold_days=14
            ),
            NoRecentActivityRule(
                name="no_recent_activity",
                description="No recent comments or changes",
                threshold_days=7
            ),
            UnresolvedQuestionsRule(
                name="unresolved_questions",
                description="Last comment has unanswered questions"
            ),
            OpenWithoutAssigneeRule(
                name="unassigned_ticket",
                description="Ticket is open but not assigned to anyone"
            ),
            AgedTicketRule(
                name="aged_ticket",
                description="Ticket is very old and still open",
                age_threshold_days=90
            )
        ]
    
    def evaluate(self, ticket: Ticket) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Evaluate if a ticket is quiescent based on business rules.
        
        Args:
            ticket: The ticket to evaluate
            
        Returns:
            Tuple of (is_quiescent, justification, details)
        """
        # Skip closed tickets
        if ticket.is_closed():
            return False, "Ticket is closed", []
        
        # Evaluate each rule and collect results
        results = []
        quiescent_indicators = 0
        
        for rule in self.rules:
            passed, reason = rule.evaluate(ticket)
            
            results.append({
                'rule': rule.name,
                'description': rule.description,
                'passed': passed,
                'reason': reason
            })
            
            if passed:
                quiescent_indicators += 1
        
        # Determine quiescence based on results
        is_quiescent = quiescent_indicators >= 2  # At least two rules must indicate quiescence
        
        # Generate justification
        if is_quiescent:
            # Collect reasons from passing rules
            passing_reasons = [r['reason'] for r in results if r['passed']]
            justification = "Ticket appears quiescent because: " + "; ".join(passing_reasons)
        else:
            # If only one or zero rules passed, explain why it's not quiescent
            if quiescent_indicators == 0:
                justification = "Ticket shows no signs of being quiescent"
            else:
                # Show the one passing rule but explain it's not enough
                passing_rule = next((r for r in results if r['passed']), None)
                if passing_rule:
                    justification = f"Ticket has one quiescence indicator ({passing_rule['reason']}), but this alone is insufficient"
                else:
                    justification = "Ticket has insufficient quiescence indicators"
        
        return is_quiescent, justification, results
