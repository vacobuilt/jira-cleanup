"""
Project-based ticket iterator.

This module provides an iterator that yields tickets from a specific Jira project,
handling pagination and filtering automatically.
"""

import logging
from typing import List, Dict, Any, Optional

from jiraclean.iterators.base import TicketIterator
from jiraclean.iterators.filters import TicketFilter, create_quiescence_prefilter
from jiraclean.jirautil.client import JiraClient

logger = logging.getLogger('jiraclean.iterators.project')


class ProjectTicketIterator(TicketIterator):
    """
    Iterator that yields all tickets from a specific Jira project.
    
    This iterator handles pagination internally, fetching tickets in batches
    for efficient API usage. It can also apply filters to the tickets before
    yielding them, allowing for efficient pre-filtering.
    """
    
    def __init__(self, 
                jira_client: JiraClient, 
                project_key: str,
                batch_size: int = 50,
                statuses_to_exclude: Optional[List[str]] = None,
                max_results: Optional[int] = None,
                ticket_filter: Optional[TicketFilter] = None,
                use_default_quiescence_filter: bool = False):
        """
        Initialize project iterator.
        
        Args:
            jira_client: Jira client implementation
            project_key: The project key to fetch tickets from
            batch_size: Number of tickets to fetch per API call
            statuses_to_exclude: List of statuses to exclude (defaults to ["Closed", "Done", "Resolved"])
            max_results: Maximum total number of tickets to return (None for all)
            ticket_filter: Optional filter to apply to tickets before yielding
            use_default_quiescence_filter: Whether to use the default quiescence filter
        """
        self.jira_client = jira_client
        self.project_key = project_key
        self.batch_size = batch_size
        self.statuses_to_exclude = statuses_to_exclude or ["Closed", "Done", "Resolved"]
        self.max_results = max_results
        
        # Set up filters
        if use_default_quiescence_filter:
            self.ticket_filter = create_quiescence_prefilter(
                excluded_statuses=self.statuses_to_exclude
            )
        else:
            self.ticket_filter = ticket_filter
        
        # Statistical tracking
        self._filtered_count = 0
        
        # Iterator state
        self.start_at = 0
        self.current_batch: List[str] = []
        self._processed = 0
        self._pending_tickets: Dict[str, Dict[str, Any]] = {}
        
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
        
        If filtering is enabled, this will fetch full ticket data and apply
        the filter, keeping only tickets that pass the filter.
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
        
        # Determine fields to fetch based on whether filtering is enabled
        fields = None  # Fetch all fields if we have a filter
        if not self.ticket_filter:
            fields = ["key"]  # Only need keys if no filtering
        
        # Get results
        results = self.jira_client.search_issues(
            jql=jql,
            start_at=self.start_at,
            max_results=fetch_count,
            fields=fields
        )
        
        # Update pagination
        self.start_at += len(results)
        
        # Process results, applying filters if enabled
        keys: List[str] = []
        
        for issue in results:
            # Extract key (with fallback for missing keys)
            key = issue.get("key")
            if not isinstance(key, str):
                # Generate a fallback key if missing
                key = f"{self.project_key}-unknown-{len(keys)}"
            
            # Apply filter if enabled
            if self.ticket_filter:
                if self.ticket_filter.passes(issue):
                    keys.append(key)
                    # Store the full issue data for later reference
                    self._pending_tickets[key] = issue
                else:
                    self._filtered_count += 1
                    logger.debug(f"Ticket {key} filtered out by pre-filter")
            else:
                keys.append(key)
        
        # Assign the properly typed list
        self.current_batch = keys
        
        # Log filtering statistics
        if self.ticket_filter and results:
            logger.info(f"Fetched {len(results)} tickets, {len(keys)} passed pre-filters ({self._filtered_count} filtered out so far)")
    
    def get_ticket_data(self, ticket_key: str) -> Dict[str, Any]:
        """
        Get the full data for a ticket that has been yielded.
        
        If the ticket was yielded and its data is available in the pending_tickets
        collection, return that. Otherwise, fetch the ticket data from Jira.
        
        Args:
            ticket_key: The Jira issue key
            
        Returns:
            Full ticket data dictionary
        """
        # First check if we have the data cached
        if ticket_key in self._pending_tickets:
            return self._pending_tickets[ticket_key]
        
        # Otherwise fetch it from Jira
        return self.jira_client.get_issue(ticket_key)
    
    def reset(self) -> None:
        """
        Reset the iterator to start from the beginning.
        
        This allows reusing the same iterator instance for multiple passes.
        """
        self.start_at = 0
        self.current_batch = []
        self._processed = 0
        self._filtered_count = 0
        self._pending_tickets = {}
    
    @property
    def processed_count(self) -> int:
        """
        Get the number of tickets that have been yielded so far.
        
        Returns:
            Count of processed tickets
        """
        return self._processed
        
    @property
    def filtered_count(self) -> int:
        """
        Get the number of tickets that were filtered out.
        
        Returns:
            Count of filtered tickets
        """
        return self._filtered_count
    
    @property
    def has_filter(self) -> bool:
        """
        Check if this iterator has an active filter.
        
        Returns:
            True if a filter is active, False otherwise
        """
        return self.ticket_filter is not None
