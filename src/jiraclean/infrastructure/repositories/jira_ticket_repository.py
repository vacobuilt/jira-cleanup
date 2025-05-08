"""
Jira ticket repository implementation.

This module contains an implementation of the ticket repository interface
that uses the Jira API to retrieve and manipulate ticket information.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Set

from jira import JIRA, Issue
from jira.exceptions import JIRAError

from jiraclean.domain.entities.ticket import Ticket, User, Comment, ChangeLogItem
from jiraclean.domain.repositories.ticket_repository import TicketRepository


logger = logging.getLogger('jiraclean.infrastructure.repositories.jira_ticket_repository')


class JiraTicketRepository(TicketRepository):
    """
    Implementation of the ticket repository using the Jira API.
    
    This repository uses the Jira Python library to interact with
    the Jira API for retrieving and updating tickets.
    """
    
    def __init__(self, jira_client: JIRA):
        """
        Initialize the Jira ticket repository.
        
        Args:
            jira_client: JIRA client instance
        """
        self.jira_client = jira_client
    
    def find_by_key(self, ticket_key: str) -> Optional[Ticket]:
        """
        Find a ticket by its key.
        
        Args:
            ticket_key: The unique key of the ticket
            
        Returns:
            The ticket if found, None otherwise
            
        Raises:
            JiraError: If there's an error with the Jira API
        """
        try:
            # Get issue with changelog to track historical changes
            issue = self.jira_client.issue(ticket_key, expand='changelog')
            return self._convert_issue_to_ticket(issue)
        except JIRAError as e:
            if e.status_code == 404:
                # Issue not found
                return None
            # Other error
            logger.error(f"Error retrieving ticket {ticket_key}: {str(e)}")
            raise
    
    def find_candidates(
        self,
        project_key: str,
        max_tickets: int = 50,
        exclude_statuses: Optional[List[str]] = None,
        only_stale: bool = True,
        stale_threshold_days: int = 14
    ) -> List[Ticket]:
        """
        Find candidate tickets for assessment.
        
        Args:
            project_key: The project key to search within
            max_tickets: Maximum number of tickets to return
            exclude_statuses: Statuses to exclude from search
            only_stale: Whether to only include stale tickets
            stale_threshold_days: Days threshold for staleness
            
        Returns:
            List of candidate tickets
            
        Raises:
            JiraError: If there's an error with the Jira API
        """
        # Set default values
        if exclude_statuses is None:
            exclude_statuses = ['Closed', 'Done', 'Resolved', 'Completed']
        
        # Build JQL query
        jql_parts = [f"project = {project_key}"]
        
        # Add status conditions
        if exclude_statuses:
            excluded_status_list = ", ".join([f'"{status}"' for status in exclude_statuses])
            jql_parts.append(f"status NOT IN ({excluded_status_list})")
        
        # Add staleness condition if needed
        if only_stale:
            threshold_date = (datetime.now(timezone.utc) - timedelta(days=stale_threshold_days)).strftime("%Y-%m-%d")
            jql_parts.append(f"updated <= {threshold_date}")
        
        # Combine JQL parts
        jql = " AND ".join(jql_parts)
        
        # Add ordering
        jql += " ORDER BY updated ASC"
        
        try:
            # Query using JQL
            logger.debug(f"Executing JQL query: {jql}")
            issues = self.jira_client.search_issues(jql, maxResults=max_tickets)
            
            # Convert issues to tickets
            tickets = []
            for issue in issues:
                ticket = self._convert_issue_to_ticket(issue)
                tickets.append(ticket)
            
            return tickets
        except JIRAError as e:
            logger.error(f"Error finding candidate tickets: {str(e)}")
            raise
    
    def find_by_criteria(
        self,
        project_key: Optional[str] = None,
        status: Optional[str] = None,
        issue_type: Optional[str] = None,
        updated_before: Optional[datetime] = None,
        updated_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        created_after: Optional[datetime] = None,
        assignee: Optional[str] = None,
        labels: Optional[List[str]] = None,
        max_results: int = 50
    ) -> List[Ticket]:
        """
        Find tickets matching specific criteria.
        
        Args:
            project_key: Optional project key to filter by
            status: Optional status to filter by
            issue_type: Optional issue type to filter by
            updated_before: Filter tickets updated before this time
            updated_after: Filter tickets updated after this time
            created_before: Filter tickets created before this time
            created_after: Filter tickets created after this time
            assignee: Optional assignee username to filter by
            labels: Optional list of labels to filter by
            max_results: Maximum number of results to return
            
        Returns:
            List of matching tickets
            
        Raises:
            JiraError: If there's an error with the Jira API
        """
        # Build JQL query
        jql_parts = []
        
        # Add project condition
        if project_key:
            jql_parts.append(f"project = {project_key}")
        
        # Add status condition
        if status:
            jql_parts.append(f'status = "{status}"')
        
        # Add issue type condition
        if issue_type:
            jql_parts.append(f'issuetype = "{issue_type}"')
        
        # Add date conditions
        if updated_before:
            date_str = updated_before.strftime("%Y-%m-%d")
            jql_parts.append(f'updated <= "{date_str}"')
        
        if updated_after:
            date_str = updated_after.strftime("%Y-%m-%d")
            jql_parts.append(f'updated >= "{date_str}"')
        
        if created_before:
            date_str = created_before.strftime("%Y-%m-%d")
            jql_parts.append(f'created <= "{date_str}"')
        
        if created_after:
            date_str = created_after.strftime("%Y-%m-%d")
            jql_parts.append(f'created >= "{date_str}"')
        
        # Add assignee condition
        if assignee:
            if assignee.lower() == 'unassigned':
                jql_parts.append('assignee is EMPTY')
            else:
                jql_parts.append(f'assignee = "{assignee}"')
        
        # Add labels condition
        if labels:
            label_conditions = " AND ".join([f'labels = "{label}"' for label in labels])
            jql_parts.append(f"({label_conditions})")
        
        # If no conditions, search all
        if not jql_parts:
            jql = "order by updated DESC"
        else:
            # Combine JQL parts
            jql = " AND ".join(jql_parts)
            # Add ordering
            jql += " ORDER BY updated DESC"
        
        try:
            # Query using JQL
            logger.debug(f"Executing JQL query: {jql}")
            issues = self.jira_client.search_issues(jql, maxResults=max_results)
            
            # Convert issues to tickets
            tickets = []
            for issue in issues:
                ticket = self._convert_issue_to_ticket(issue)
                tickets.append(ticket)
            
            return tickets
        except JIRAError as e:
            logger.error(f"Error finding tickets by criteria: {str(e)}")
            raise
    
    def save(self, ticket: Ticket) -> Ticket:
        """
        Save changes to a ticket.
        
        This is not a full implementation, as the Jira API doesn't support
        directly updating a ticket with a complete new state. Instead,
        use specific Jira API methods for changing status, assigning, etc.
        
        Args:
            ticket: The ticket to save
            
        Returns:
            The updated ticket
            
        Raises:
            NotImplementedError: This method is not fully implemented
            ValueError: If the updated ticket cannot be retrieved
        """
        # This is a simplified implementation
        try:
            # Get the Jira issue
            issue = self.jira_client.issue(ticket.key)
            
            # Update fields that can be changed
            update_fields = {}
            
            # Update summary if changed
            if issue.fields.summary != ticket.summary:
                update_fields['summary'] = ticket.summary
            
            # Update description if changed
            if issue.fields.description != ticket.description:
                update_fields['description'] = ticket.description
            
            # If there are fields to update, do it
            if update_fields:
                issue.update(fields=update_fields)
            
            # Get updated ticket
            updated_ticket = self.find_by_key(ticket.key)
            if updated_ticket is None:
                raise ValueError(f"Failed to retrieve updated ticket {ticket.key}")
            return updated_ticket
        except JIRAError as e:
            logger.error(f"Error saving ticket {ticket.key}: {str(e)}")
            raise
    
    def count(
        self,
        project_key: Optional[str] = None,
        status: Optional[str] = None,
        issue_type: Optional[str] = None
    ) -> int:
        """
        Count tickets matching specific criteria.
        
        Args:
            project_key: Optional project key to filter by
            status: Optional status to filter by
            issue_type: Optional issue type to filter by
            
        Returns:
            Count of matching tickets
            
        Raises:
            JiraError: If there's an error with the Jira API
        """
        # Build JQL query
        jql_parts = []
        
        # Add project condition
        if project_key:
            jql_parts.append(f"project = {project_key}")
        
        # Add status condition
        if status:
            jql_parts.append(f'status = "{status}"')
        
        # Add issue type condition
        if issue_type:
            jql_parts.append(f'issuetype = "{issue_type}"')
        
        # If no conditions, count all
        if not jql_parts:
            jql = ""
        else:
            # Combine JQL parts
            jql = " AND ".join(jql_parts)
        
        try:
            # Use Jira API to count
            return self.jira_client.search_issues(jql, maxResults=0).total
        except JIRAError as e:
            logger.error(f"Error counting tickets: {str(e)}")
            raise
    
    def _convert_issue_to_ticket(self, issue: Issue) -> Ticket:
        """
        Convert a Jira issue to our domain Ticket entity.
        
        Args:
            issue: Jira issue object
            
        Returns:
            Ticket entity
        """
        # Extract basic fields
        key = issue.key
        summary = issue.fields.summary
        status = issue.fields.status.name
        issue_type = issue.fields.issuetype.name
        description = issue.fields.description or ""
        project_key = issue.fields.project.key
        workflow_status = getattr(issue.fields.status, 'statusCategory', {}).get('name', 'Unknown')
        
        # Get dates
        created_date = self._parse_jira_date(issue.fields.created)
        updated_date = self._parse_jira_date(issue.fields.updated)
        
        # Extract user information
        assignee = None
        if hasattr(issue.fields, 'assignee') and issue.fields.assignee:
            assignee_data = issue.fields.assignee
            assignee = User(
                display_name=getattr(assignee_data, 'displayName', 'Unknown'),
                username=getattr(assignee_data, 'name', None),
                account_id=getattr(assignee_data, 'accountId', None)
            )
        
        reporter = None
        if hasattr(issue.fields, 'reporter') and issue.fields.reporter:
            reporter_data = issue.fields.reporter
            reporter = User(
                display_name=getattr(reporter_data, 'displayName', 'Unknown'),
                username=getattr(reporter_data, 'name', None),
                account_id=getattr(reporter_data, 'accountId', None)
            )
        
        creator = None
        if hasattr(issue.fields, 'creator') and issue.fields.creator:
            creator_data = issue.fields.creator
            creator = User(
                display_name=getattr(creator_data, 'displayName', 'Unknown'),
                username=getattr(creator_data, 'name', None),
                account_id=getattr(creator_data, 'accountId', None)
            )
        
        # Extract comments
        comments = []
        if hasattr(issue.fields, 'comment') and issue.fields.comment:
            for comment_data in issue.fields.comment.comments:
                author = User(
                    display_name=getattr(comment_data.author, 'displayName', 'Unknown'),
                    username=getattr(comment_data.author, 'name', None),
                    account_id=getattr(comment_data.author, 'accountId', None)
                )
                
                comment = Comment(
                    id=comment_data.id,
                    body=comment_data.body,
                    author=author,
                    created_date=self._parse_jira_date(comment_data.created),
                    updated_date=self._parse_jira_date(comment_data.updated)
                )
                comments.append(comment)
        
        # Extract changelog
        changelog = []
        if hasattr(issue, 'changelog') and issue.changelog:
            for history in issue.changelog.histories:
                for item in history.items:
                    author = User(
                        display_name=getattr(history.author, 'displayName', 'Unknown'),
                        username=getattr(history.author, 'name', None),
                        account_id=getattr(history.author, 'accountId', None)
                    )
                    
                    change = ChangeLogItem(
                        field=item.field,
                        from_value=item.fromString or "",
                        to_value=item.toString or "",
                        author=author,
                        date=self._parse_jira_date(history.created)
                    )
                    changelog.append(change)
        
        # Extract labels
        labels = []
        if hasattr(issue.fields, 'labels'):
            labels = issue.fields.labels
        
        # Extract components
        components = []
        if hasattr(issue.fields, 'components'):
            components = [c.name for c in issue.fields.components]
        
        # Extract watchers - note this may require additional API calls
        watchers = []
        
        # Create and return the ticket
        return Ticket(
            key=key,
            summary=summary,
            status=status,
            issue_type=issue_type,
            description=description,
            project_key=project_key,
            workflow_status=workflow_status,
            created_date=created_date,
            updated_date=updated_date,
            assignee=assignee,
            reporter=reporter,
            creator=creator,
            comments=comments,
            changelog=changelog,
            labels=labels,
            components=components,
            watchers=watchers
        )
    
    def _parse_jira_date(self, date_str: Optional[str]) -> datetime:
        """
        Parse a Jira date string to a datetime object.
        
        Args:
            date_str: Date string from Jira API
            
        Returns:
            Parsed datetime with timezone
        """
        if not date_str:
            return datetime.now(timezone.utc)
            
        try:
            # Jira usually provides ISO-8601 dates
            # Replace Z with +00:00 for better compatibility
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            # Fallback to now if parsing fails
            logger.warning(f"Failed to parse Jira date string: {date_str}")
            return datetime.now(timezone.utc)
