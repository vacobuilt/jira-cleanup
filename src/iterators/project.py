"""
Project-based ticket iterator.

This module provides an iterator that yields tickets from a specific Jira project,
handling pagination and filtering automatically.
"""

from typing import List, Dict, Any, Optional

from .base import TicketIterator
from jirautil.client import JiraClient


class ProjectTicketIterator(TicketIterator):
    """
    Iterator that yields all tickets from a specific Jira project.
    
    This iterator handles pagination internally, fetching tickets in batches
    for efficient API usage.
    """
    
    def __init__(self, 
                jira_client: JiraClient, 
                project_key: str,
                batch_size: int = 50,
                statuses_to_exclude: Optional[List[str]] = None,
                max_results: Optional[int] = None):
        """
        Initialize project iterator.
        
        Args:
            jira_client: Jira client implementation
            project_key: The project key to fetch tickets from
            batch_size: Number of tickets to fetch per API call
            statuses_to_exclude: List of statuses to exclude (defaults to ["Closed", "Done"])
            max_results: Maximum total number of tickets to return (None for all)
        """
        self.jira_client = jira_client
        self.project_key = project_key
        self.batch_size = batch_size
        self.statuses_to_exclude = statuses_to_exclude or ["Closed", "Done", "Resolved"]
        self.max_results = max_results
        
        # Iterator state
        self.start_at = 0
        self.current_batch: List[str] = []
        self._total: Optional[int] = None
        self._processed = 0
        
    def __iter__(self) -> 'ProjectTicketIterator':
        """Return self as iterator."""
        return self
    
    def __next__(self) -> str:
        """
        Return the next ticket key.
        
        Returns:
            A Jira issue key (e.g., 'PROJ-123')
            
        Raises:
            StopIteration: When no more tickets are available
        """
        # Check if we've hit max results
        if self.max_results is not None and self._processed >= self.max_results:
            raise StopIteration
        
        # Fetch more if current batch is empty
        if not self.current_batch:
            self._fetch_next_batch()
            
            if not self.current_batch:
                raise StopIteration
        
        # Get next ticket key and update counters
        ticket_key = self.current_batch.pop(0)
        self._processed += 1
        return ticket_key
    
    def _build_jql(self) -> str:
        """
        Build JQL query for the project.
        
        Returns:
            JQL query string
        """
        query_parts = [f'project = "{self.project_key}"']
        
        if self.statuses_to_exclude:
            status_clause = " AND ".join([f'status != "{status}"' for status in self.statuses_to_exclude])
            query_parts.append(f"({status_clause})")
        
        return " AND ".join(query_parts)
    
    def _fetch_next_batch(self) -> None:
        """
        Fetch the next batch of tickets from Jira.
        
        This method updates:
        - current_batch with next batch of tickets
        - start_at for pagination
        - _total if not already set
        """
        # Build JQL query
        jql = self._build_jql()
        
        # Calculate how many tickets to fetch in this batch
        fetch_count = self.batch_size
        if self.max_results is not None:
            remaining = self.max_results - self._processed
            fetch_count = min(fetch_count, remaining)
            
            # Don't make a request if we've already reached the limit
            if fetch_count <= 0:
                self.current_batch = []
                return
        
        # Get results
        results = self.jira_client.search_issues(
            jql=jql,
            start_at=self.start_at,
            max_results=fetch_count,
            fields=["key"]  # Only need keys for the iterator
        )
        
        # Update state
        self.start_at += len(results)
        self.current_batch = [issue.get("key") for issue in results]
        
        # Get total if not already set
        if self._total is None and hasattr(results, "total"):
            self._total = getattr(results, "total", len(results))
    
    @property
    def total_tickets(self) -> Optional[int]:
        """
        Get the total number of tickets that match the criteria, if known.
        
        Returns:
            Total number of tickets or None if unknown
        """
        if self._total is None:
            return None
            
        if self.max_results is not None:
            return min(self._total, self.max_results)
            
        return self._total
    
    def reset(self) -> None:
        """
        Reset the iterator to start from the beginning.
        
        This allows reusing the same iterator instance for multiple passes.
        """
        self.start_at = 0
        self.current_batch = []
        self._processed = 0
        # Don't reset _total as we already know it
    
    @property
    def processed_count(self) -> int:
        """
        Get the number of tickets that have been yielded so far.
        
        Returns:
            Count of processed tickets
        """
        return self._processed
