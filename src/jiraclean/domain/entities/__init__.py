"""
Domain entities for Jira Cleanup.

This package contains the core business objects that represent
the essential concepts in the problem domain.
"""

from jira_cleanup.src.domain.entities.ticket import Ticket
from jira_cleanup.src.domain.entities.assessment import Assessment
from jira_cleanup.src.domain.entities.action import ActionRecommendation

__all__ = [
    'Ticket',
    'Assessment',
    'ActionRecommendation'
]
