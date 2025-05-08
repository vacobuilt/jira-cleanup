"""
Comment generation domain service.

This module contains the domain service responsible for generating comments
based on assessment results.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Set

from jira_cleanup.src.domain.entities.ticket import Ticket, User
from jira_cleanup.src.domain.entities.assessment import Assessment


class CommentGenerator:
    """
    Domain service for generating ticket comments.
    
    This service encapsulates the logic for creating well-formatted comments
    based on assessment results and domain rules.
    """
    
    def __init__(self, system_marker: str = "[AUTOMATED QUIESCENCE ASSESSMENT]"):
        """
        Initialize the comment generator.
        
        Args:
            system_marker: Marker to identify system-generated comments
        """
        self.system_marker = system_marker
    
    def generate_quiescence_comment(
        self, 
        ticket: Ticket, 
        assessment: Assessment,
        include_closing_warning: bool = True
    ) -> str:
        """
        Generate a comment for a quiescent ticket.
        
        Args:
            ticket: The ticket to generate a comment for
            assessment: Assessment results for the ticket
            include_closing_warning: Whether to include a closing warning if appropriate
            
        Returns:
            Formatted comment text
        """
        # Start with the system marker
        comment_lines = [self.system_marker]
        comment_lines.append("")
        
        # Add mentions for the responsible party and other relevant users
        mentions = self._generate_mentions(ticket, assessment.responsible_party)
        if mentions:
            comment_lines.append(mentions)
            comment_lines.append("")
        
        # Add the main message
        comment_lines.append(assessment.justification)
        comment_lines.append("")
        
        # Add suggested action
        comment_lines.append(f"**Suggested Action**: {assessment.suggested_action}")
        
        # Add deadline
        if assessment.suggested_deadline:
            comment_lines.append(f"**Suggested Deadline**: {assessment.suggested_deadline}")
        
        # Add closing warning if appropriate
        if include_closing_warning and self._should_add_closing_warning(ticket, assessment):
            comment_lines.append("")
            deadline_date = self._format_deadline_date(assessment)
            comment_lines.append(f"**Note**: If no action is taken by {deadline_date}, this ticket may be closed.")
        
        # Return the formatted comment
        return "\n".join(comment_lines)
    
    def _generate_mentions(self, ticket: Ticket, responsible_party: str) -> str:
        """
        Generate appropriate user mentions for the comment.
        
        Args:
            ticket: The ticket to generate mentions for
            responsible_party: The responsible party from the assessment
            
        Returns:
            Formatted mention string
        """
        mentions = []
        
        # Add mention for responsible party if it's a username
        if responsible_party and responsible_party.lower() != "unknown":
            mentions.append(self._format_mention(responsible_party))
        
        # Add mention for assignee if different from responsible party
        if ticket.assignee and str(ticket.assignee) != responsible_party:
            mentions.append(self._format_mention(ticket.assignee))
        
        # Add mention for reporter if different from both
        if ticket.reporter and str(ticket.reporter) not in [responsible_party, str(ticket.assignee) if ticket.assignee else ""]:
            mentions.append(self._format_mention(ticket.reporter))
        
        # Return formatted mentions
        if mentions:
            return f"Hi {', '.join(mentions)},"
        
        return ""
    
    def _format_mention(self, user: User) -> str:
        """
        Format a Jira user mention.
        
        Args:
            user: User to mention
            
        Returns:
            Formatted mention string
        """
        if isinstance(user, str):
            # Handle case where responsible_party is a string
            return f"[~{user}]"
            
        # For User objects, prefer account ID if available (Jira Cloud)
        if user.account_id:
            return f"[~accountId:{user.account_id}]"
        elif user.username:
            return f"[~{user.username}]"
        else:
            # Fallback to display name without mention if no identifiers
            return user.display_name
    
    def _should_add_closing_warning(self, ticket: Ticket, assessment: Assessment) -> bool:
        """
        Determine if a closing warning should be included.
        
        Args:
            ticket: The ticket
            assessment: Assessment results
            
        Returns:
            True if closing warning should be included, False otherwise
        """
        # Add warning if ticket is very old (3+ months)
        if ticket.days_since_update >= 90:
            return True
        
        # Add warning if assessment indicates it's needed
        if assessment.is_warning_needed:
            return True
        
        return False
    
    def _format_deadline_date(self, assessment: Assessment) -> str:
        """
        Format the deadline date for the closing warning.
        
        Args:
            assessment: Assessment results with deadline info
            
        Returns:
            Formatted date string
        """
        # Try to get deadline from assessment
        deadline_date = assessment.deadline_date
        
        # If not available, default to 2 weeks
        if not deadline_date:
            deadline_date = datetime.now() + timedelta(days=14)
        
        # Format as a date string
        return deadline_date.strftime("%Y-%m-%d")
