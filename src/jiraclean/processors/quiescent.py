"""
Quiescent ticket processor implementation.

This module provides a processor that analyzes tickets for quiescence
using pre-filtering and LLM assessment to take appropriate actions.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from jiraclean.processors.base import TicketProcessor
from jiraclean.jirautil import JiraClient
from jiraclean.iterators.project import ProjectTicketIterator
from jiraclean.iterators.filters import create_quiescence_prefilter
from jiraclean.llm import assess_ticket, AssessmentResult

logger = logging.getLogger('jiraclean.processors.quiescent')


class QuiescentTicketProcessor(TicketProcessor):
    """
    Processor that detects and responds to quiescent tickets.
    
    This processor uses pre-filtering and LLM assessment to determine if a ticket 
    is quiescent, and takes action based on the assessment (e.g., adding a comment).
    """
    
    def __init__(self, 
                jira_client: JiraClient,
                llm_model: str = "llama3.2:latest",
                ollama_url: str = "http://localhost:11434",
                min_age_days: int = 14,
                min_inactive_days: int = 7):
        """
        Initialize the quiescent ticket processor.
        
        Args:
            jira_client: JiraClient instance for Jira API access
            llm_model: LLM model to use for assessment
            ollama_url: URL for Ollama API
            min_age_days: Minimum age in days for a ticket to be considered quiescent
            min_inactive_days: Minimum number of days without activity
        """
        super().__init__()
        self.jira_client = jira_client
        self.llm_model = llm_model
        self.ollama_url = ollama_url
        self.min_age_days = min_age_days
        self.min_inactive_days = min_inactive_days
        
        # Additional statistics specific to quiescent detection
        self._stats.update({
            'quiescent': 0,
            'non_quiescent': 0,
            'assessment_failures': 0,
            'comments_added': 0,
            'prefiltered': 0
        })
    
    def process(self, 
                ticket_key: str, 
                ticket_data: Optional[Dict[str, Any]] = None, 
                dry_run: bool = True) -> Dict[str, Any]:
        """
        Process a single ticket.
        
        Args:
            ticket_key: The Jira issue key
            ticket_data: Optional ticket data (fetched if not provided)
            dry_run: If True, only simulate actions without making changes
            
        Returns:
            Result dictionary with action information
        """
        result = {
            'ticket_key': ticket_key,
            'actions': [],
            'success': False,
            'message': ''
        }
        
        try:
            # Fetch ticket data if not provided
            if ticket_data is None:
                ticket_data = self.jira_client.get_issue(ticket_key, fields=None)
            
            # Assess the ticket for quiescence
            assessment = assess_ticket(
                ticket_data, 
                model=self.llm_model,
                ollama_url=self.ollama_url
            )
            
            # Log the assessment
            if assessment.is_quiescent:
                logger.info(f"Ticket {ticket_key} is quiescent: {assessment.justification}")
                self._stats['quiescent'] += 1
            else:
                logger.info(f"Ticket {ticket_key} is not quiescent: {assessment.justification}")
                self._stats['non_quiescent'] += 1
            
            # Take action if quiescent
            if assessment.is_quiescent:
                # Add comment if not in dry run mode
                if not dry_run:
                    try:
                        comment_result = self.jira_client.add_comment(
                            ticket_key, 
                            assessment.planned_comment
                        )
                        
                        self._stats['comments_added'] += 1
                        
                        result['actions'].append({
                            'type': 'comment',
                            'description': 'Added quiescent ticket comment',
                            'success': True,
                            'details': {
                                'comment_id': comment_result.get('id'),
                                'comment_body': assessment.planned_comment[:100] + '...'  # Truncate for logging
                            }
                        })
                    except Exception as e:
                        logger.error(f"Error adding comment to {ticket_key}: {str(e)}")
                        result['actions'].append({
                            'type': 'comment',
                            'description': 'Failed to add quiescent ticket comment',
                            'success': False,
                            'details': {
                                'error': str(e)
                            }
                        })
                else:
                    # In dry run mode, just log the planned action
                    # The actual comment content will be printed by the DryRunJiraClient
                    self.jira_client.add_comment(ticket_key, assessment.planned_comment)
                    
                    result['actions'].append({
                        'type': 'comment',
                        'description': 'Would add quiescent ticket comment (dry run)',
                        'success': True,
                        'details': {
                            'dry_run': True
                        }
                    })
            
            result['success'] = True
            result['message'] = f"Ticket {ticket_key} processed successfully"
            result['assessment'] = assessment.to_dict()
            
        except Exception as e:
            logger.error(f"Error processing ticket {ticket_key}: {str(e)}")
            self._stats['assessment_failures'] += 1
            result['success'] = False
            result['message'] = f"Error processing ticket: {str(e)}"
        
        # Update overall statistics
        self._update_stats(result)
        return result
    
    def process_project(self, 
                      project_key: str, 
                      max_tickets: Optional[int] = None, 
                      statuses_to_exclude: Optional[List[str]] = None,
                      dry_run: bool = True,
                      skip_prefilter: bool = False) -> Dict[str, Any]:
        """
        Process all tickets in a project that meet the quiescence criteria.
        
        This method creates a ProjectTicketIterator with pre-filtering for basic
        quiescence criteria (age, recent activity, status), then processes each
        ticket that passes the filter with the LLM for a more detailed assessment.
        
        Args:
            project_key: The Jira project key
            max_tickets: Maximum number of tickets to process
            statuses_to_exclude: List of statuses to exclude
            dry_run: If True, only simulate actions without making changes
            skip_prefilter: If True, skip pre-filtering and process all tickets
            
        Returns:
            Dictionary with processing results
        """
        # Use default statuses if not provided
        statuses_to_exclude = statuses_to_exclude or ["Closed", "Done", "Resolved"]
        
        # Create project iterator with pre-filtering
        iterator = ProjectTicketIterator(
            jira_client=self.jira_client,
            project_key=project_key,
            statuses_to_exclude=statuses_to_exclude,
            max_results=max_tickets,
            # Only apply pre-filter if not explicitly skipped
            use_default_quiescence_filter=not skip_prefilter,
        )
        
        results = {
            'project_key': project_key,
            'tickets_processed': 0,
            'tickets_prefiltered': 0,
            'tickets_quiescent': 0,
            'tickets_with_actions': 0,
            'processing_errors': 0,
            'results': []
        }
        
        # Start processing tickets
        start_processed = self._stats['processed']
        
        try:
            # Iterate through tickets that pass pre-filtering
            for ticket_key in iterator:
                # Get full ticket data if iterator doesn't already have it cached
                ticket_data = iterator.get_ticket_data(ticket_key)
                
                # Process the individual ticket
                ticket_result = self.process(ticket_key, ticket_data, dry_run)
                
                # Update statistics
                results['tickets_processed'] += 1
                if ticket_result.get('success', False):
                    if ticket_result.get('assessment', {}).get('is_quiescent', False):
                        results['tickets_quiescent'] += 1
                        if ticket_result.get('actions'):
                            results['tickets_with_actions'] += 1
                else:
                    results['processing_errors'] += 1
                
                # Add to results list
                results['results'].append(ticket_result)
                
                # Update progress every 10 tickets
                if results['tickets_processed'] % 10 == 0:
                    logger.info(f"Processed {results['tickets_processed']} tickets in {project_key}")
            
            # Update final statistics
            if iterator.has_filter:
                results['tickets_prefiltered'] = iterator.filtered_count
                self._stats['prefiltered'] += iterator.filtered_count
                
                logger.info(f"Pre-filtering stats: {iterator.filtered_count} tickets filtered out, " 
                           f"{results['tickets_processed']} passed through to LLM")
            
            return results
        except Exception as e:
            logger.error(f"Error processing project {project_key}: {str(e)}")
            # Add the error to results
            results['error'] = str(e)
            return results
    
    def describe_action(self, ticket_key: str, ticket_data: Dict[str, Any]) -> str:
        """
        Describe the action that would be taken for a ticket.
        
        Args:
            ticket_key: The Jira issue key
            ticket_data: The ticket data dictionary
            
        Returns:
            Human-readable description of the action
        """
        # First check basic criteria using the prefilter
        prefilter = create_quiescence_prefilter(
            min_age_days=self.min_age_days,
            min_inactive_days=self.min_inactive_days
        )
        
        if not prefilter.passes(ticket_data):
            return f"Would skip ticket {ticket_key} (fails basic quiescence criteria)"
        
        # If it passes the prefilter, do the LLM assessment
        try:
            # Get a quick assessment
            assessment = assess_ticket(
                ticket_data, 
                model=self.llm_model,
                ollama_url=self.ollama_url
            )
            
            if assessment.is_quiescent:
                return f"Would comment on ticket {ticket_key} as quiescent: {assessment.justification}"
            else:
                return f"Would skip ticket {ticket_key} (not quiescent): {assessment.justification}"
        except Exception as e:
            return f"Unable to assess ticket {ticket_key}: {str(e)}"
