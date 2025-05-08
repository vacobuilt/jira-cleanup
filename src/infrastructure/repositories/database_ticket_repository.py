"""
Database ticket repository implementation.

This module contains an implementation of the ticket repository interface
that uses a database to retrieve ticket information.
"""

import logging
import sqlalchemy as sa
from sqlalchemy import sql
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any

from jira_cleanup.src.domain.entities.ticket import Ticket, User, Comment, ChangeLogItem
from jira_cleanup.src.domain.repositories.ticket_repository import TicketRepository


logger = logging.getLogger('jira_cleanup.infrastructure.repositories.database_ticket_repository')


class DatabaseTicketRepository(TicketRepository):
    """
    Implementation of the ticket repository using a database.
    
    This repository uses SQLAlchemy to query a database for Jira ticket
    information. It's primarily used for finding candidate tickets
    that need assessment.
    """
    
    def __init__(self, engine: sa.engine.Engine):
        """
        Initialize the database ticket repository.
        
        Args:
            engine: SQLAlchemy database engine
        """
        self.engine = engine
    
    def find_by_key(self, ticket_key: str) -> Optional[Ticket]:
        """
        Find a ticket by its key.
        
        Args:
            ticket_key: The unique key of the ticket
            
        Returns:
            The ticket if found, None otherwise
        """
        conn = self.engine.connect()
        with conn.begin():
            query = sql.text("""
                SELECT 
                    issue_key, 
                    summary,
                    status,
                    updated_date,
                    created_date,
                    issue_type,
                    description,
                    project_key
                FROM jira.jira_issues
                WHERE issue_key = :ticket_key
            """)
            
            result = conn.execute(query, {'ticket_key': ticket_key})
            row = result.fetchone()
            
            if not row:
                return None
            
            # Convert row to dict
            ticket_data = dict(row._mapping)
            
            # Get comments for the ticket
            comments_query = sql.text("""
                SELECT 
                    id,
                    body,
                    author,
                    created_date,
                    updated_date
                FROM jira.jira_comments
                WHERE issue_key = :ticket_key
                ORDER BY created_date ASC
            """)
            
            comments_result = conn.execute(comments_query, {'ticket_key': ticket_key})
            comments_data = []
            
            for comment_row in comments_result:
                comment_dict = dict(comment_row._mapping)
                comments_data.append(comment_dict)
            
            # Get changelog for the ticket
            changelog_query = sql.text("""
                SELECT 
                    field,
                    from_value,
                    to_value,
                    author,
                    change_date
                FROM jira.jira_changelog
                WHERE issue_key = :ticket_key
                ORDER BY change_date ASC
            """)
            
            changelog_result = conn.execute(changelog_query, {'ticket_key': ticket_key})
            changelog_data = []
            
            for change_row in changelog_result:
                change_dict = dict(change_row._mapping)
                changelog_data.append(change_dict)
            
            # Add comments and changelog to ticket data
            ticket_data['comments'] = comments_data
            ticket_data['changelog'] = changelog_data
            
            # Create and return ticket entity
            return self._create_ticket_from_data(ticket_data)
    
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
        """
        # Set default values
        if exclude_statuses is None:
            exclude_statuses = ['Closed', 'Done', 'Resolved', 'Completed']
        
        # Calculate threshold date if needed
        threshold_date = None
        if only_stale:
            threshold_date = datetime.now(timezone.utc) - timedelta(days=stale_threshold_days)
        
        conn = self.engine.connect()
        with conn.begin():
            # Construct the NOT IN clause manually for compatibility
            status_conditions = " AND ".join([f"status != '{status}'" for status in exclude_statuses])
            
            # Base query
            query_text = f"""
                SELECT 
                    issue_key, 
                    summary,
                    status,
                    updated_date,
                    created_date,
                    issue_type,
                    description,
                    project_key
                FROM jira.jira_issues
                WHERE 
                    issue_key LIKE :project_pattern
                    AND {status_conditions}
            """
            
            # Add staleness condition if needed
            if only_stale and threshold_date:
                query_text += " AND updated_date < :threshold_date"
                
            # Add ordering and limit
            query_text += """
                ORDER BY updated_date ASC
                LIMIT :max_tickets
            """
            
            # Create the query
            query = sql.text(query_text)
            
            # Prepare parameters
            params = {
                'project_pattern': f"{project_key}-%",
                'max_tickets': max_tickets
            }
            
            if only_stale and threshold_date:
                params['threshold_date'] = threshold_date
            
            # Execute the query
            result = conn.execute(query, params)
            
            # Process results
            candidates = []
            for row in result:
                # Convert row to dict
                ticket_data = dict(row._mapping)
                
                # Get comments and changelog (simplified for candidates)
                ticket_data['comments'] = []
                ticket_data['changelog'] = []
                
                # Create ticket entity
                ticket = self._create_ticket_from_data(ticket_data)
                candidates.append(ticket)
        
        return candidates
    
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
        """
        conn = self.engine.connect()
        with conn.begin():
            # Build query conditions
            conditions = []
            params = {}
            
            if project_key:
                conditions.append("issue_key LIKE :project_pattern")
                params['project_pattern'] = f"{project_key}-%"
            
            if status:
                conditions.append("status = :status")
                params['status'] = status
            
            if issue_type:
                conditions.append("issue_type = :issue_type")
                params['issue_type'] = issue_type
            
            if updated_before:
                conditions.append("updated_date < :updated_before")
                params['updated_before'] = updated_before
            
            if updated_after:
                conditions.append("updated_date > :updated_after")
                params['updated_after'] = updated_after
            
            if created_before:
                conditions.append("created_date < :created_before")
                params['created_before'] = created_before
            
            if created_after:
                conditions.append("created_date > :created_after")
                params['created_after'] = created_after
            
            if assignee:
                conditions.append("assignee = :assignee")
                params['assignee'] = assignee
            
            # Build WHERE clause
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # Build query
            query_text = f"""
                SELECT 
                    issue_key, 
                    summary,
                    status,
                    updated_date,
                    created_date,
                    issue_type,
                    description,
                    project_key
                FROM jira.jira_issues
                WHERE {where_clause}
                ORDER BY updated_date DESC
                LIMIT :max_results
            """
            
            # Add max results parameter
            params['max_results'] = max_results
            
            # Execute query
            query = sql.text(query_text)
            result = conn.execute(query, params)
            
            # Process results
            tickets = []
            for row in result:
                # Convert row to dict
                ticket_data = dict(row._mapping)
                
                # Get comments and changelog (simplified for search results)
                ticket_data['comments'] = []
                ticket_data['changelog'] = []
                
                # Create ticket entity
                ticket = self._create_ticket_from_data(ticket_data)
                tickets.append(ticket)
        
        return tickets
    
    def save(self, ticket: Ticket) -> Ticket:
        """
        Save changes to a ticket.
        
        Note: This method is not fully implemented for the database repository
        as it's primarily used for reading tickets. Updates should be made
        directly to Jira.
        
        Args:
            ticket: The ticket to save
            
        Returns:
            The updated ticket
            
        Raises:
            NotImplementedError: This method is not implemented for database repository
        """
        raise NotImplementedError(
            "Database repository does not support saving tickets. "
            "Use JiraTicketRepository for modifications."
        )
    
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
        """
        conn = self.engine.connect()
        with conn.begin():
            # Build query conditions
            conditions = []
            params = {}
            
            if project_key:
                conditions.append("issue_key LIKE :project_pattern")
                params['project_pattern'] = f"{project_key}-%"
            
            if status:
                conditions.append("status = :status")
                params['status'] = status
            
            if issue_type:
                conditions.append("issue_type = :issue_type")
                params['issue_type'] = issue_type
            
            # Build WHERE clause
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # Build query
            query_text = f"""
                SELECT COUNT(*) as count
                FROM jira.jira_issues
                WHERE {where_clause}
            """
            
            # Execute query
            query = sql.text(query_text)
            result = conn.execute(query, params)
            row = result.fetchone()
            
            if row:
                return row.count
            
            return 0
    
    def _create_ticket_from_data(self, data: Dict[str, Any]) -> Ticket:
        """
        Create a Ticket entity from database data.
        
        Args:
            data: Dictionary with ticket data from database
            
        Returns:
            Ticket entity
        """
        # Create user objects
        assignee = User(display_name=data.get('assignee', 'Unassigned')) if data.get('assignee') else None
        reporter = User(display_name=data.get('reporter', 'Unknown')) if data.get('reporter') else None
        creator = User(display_name=data.get('creator', 'Unknown')) if data.get('creator') else None
        
        # Process comments
        comments = []
        for comment_data in data.get('comments', []):
            author = User(display_name=comment_data.get('author', 'Unknown'))
            comment = Comment(
                id=str(comment_data.get('id', '')),
                body=comment_data.get('body', ''),
                author=author,
                created_date=comment_data.get('created_date', datetime.now()),
                updated_date=comment_data.get('updated_date', datetime.now())
            )
            comments.append(comment)
        
        # Process changelog
        changelog = []
        for change_data in data.get('changelog', []):
            author = User(display_name=change_data.get('author', 'Unknown'))
            change = ChangeLogItem(
                field=change_data.get('field', ''),
                from_value=change_data.get('from_value', ''),
                to_value=change_data.get('to_value', ''),
                author=author,
                date=change_data.get('change_date', datetime.now())
            )
            changelog.append(change)
        
        # Create and return ticket
        return Ticket(
            key=data.get('issue_key', ''),
            summary=data.get('summary', ''),
            status=data.get('status', ''),
            issue_type=data.get('issue_type', ''),
            created_date=data.get('created_date', datetime.now()),
            updated_date=data.get('updated_date', datetime.now()),
            description=data.get('description', ''),
            project_key=data.get('project_key', ''),
            assignee=assignee,
            reporter=reporter,
            creator=creator,
            comments=comments,
            changelog=changelog
        )
