"""
Generic ticket processor implementation.

This module provides a processor that works with any analyzer and formatter,
making the processing framework completely agnostic to analysis types.
"""

import logging
from typing import Dict, Any, List, Optional

from jiraclean.processors.base import TicketProcessor
from jiraclean.jirautil import JiraClient
from jiraclean.iterators.project import ProjectTicketIterator
from jiraclean.analysis.base import BaseTicketAnalyzer
from jiraclean.ui.formatters.base_formatter import BaseFormatter

logger = logging.getLogger('jiraclean.processors.generic')


class GenericTicketProcessor(TicketProcessor):
    """
    Generic processor that works with any analyzer and formatter.
    
    This processor is completely agnostic to analysis types and delegates
    all analysis-specific logic to the analyzer and formatter components.
    """
    
    def __init__(self, 
                jira_client: JiraClient,
                analyzer: BaseTicketAnalyzer,
                formatter: BaseFormatter):
        """
        Initialize the generic ticket processor.
        
        Args:
            jira_client: JiraClient instance for Jira API access
            analyzer: Analyzer instance for ticket assessment
            formatter: Formatter instance for UI display
        """
        super().__init__()
        self.jira_client = jira_client
        self.analyzer = analyzer
        self.formatter = formatter
        
        # Generic statistics - no analysis-specific fields
        self._stats.update({
            'needs_action': 0,
            'no_action_needed': 0,
            'assessment_failures': 0,
            'comments_added': 0,
            'prefiltered': 0
        })
    
    def process(self, 
                ticket_key: str, 
                ticket_data: Optional[Dict[str, Any]] = None, 
                dry_run: bool = True) -> Dict[str, Any]:
        """
        Process a single ticket using the configured analyzer and formatter.
        
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
            
            # Analyze the ticket using the injected analyzer
            analysis_result = self.analyzer.analyze(ticket_data)
            
            # Use formatter to determine status and log appropriately
            status_text = self.formatter.get_status_text(analysis_result)
            logger.info(f"Ticket {ticket_key} analysis: {status_text} - {analysis_result.justification}")
            
            # Update statistics based on result
            if analysis_result.needs_action():
                self._stats['needs_action'] += 1
            else:
                self._stats['no_action_needed'] += 1
            
            # Take action if needed
            if analysis_result.needs_action():
                comment = analysis_result.get_planned_comment()
                
                if not dry_run:
                    try:
                        comment_result = self.jira_client.add_comment(ticket_key, comment)
                        self._stats['comments_added'] += 1
                        
                        result['actions'].append({
                            'type': 'comment',
                            'description': f'Added {self.analyzer.get_analyzer_type()} comment',
                            'success': True,
                            'details': {
                                'comment_id': comment_result.get('id'),
                                'comment_body': comment[:100] + '...'
                            }
                        })
                    except Exception as e:
                        logger.error(f"Error adding comment to {ticket_key}: {str(e)}")
                        result['actions'].append({
                            'type': 'comment',
                            'description': f'Failed to add {self.analyzer.get_analyzer_type()} comment',
                            'success': False,
                            'details': {'error': str(e)}
                        })
                else:
                    # Dry run mode
                    self.jira_client.add_comment(ticket_key, comment)
                    result['actions'].append({
                        'type': 'comment',
                        'description': f'Would add {self.analyzer.get_analyzer_type()} comment (dry run)',
                        'success': True,
                        'details': {'dry_run': True}
                    })
            
            result['success'] = True
            result['message'] = f"Ticket {ticket_key} processed successfully"
            result['analysis_result'] = analysis_result.to_dict()
            
        except Exception as e:
            logger.error(f"Error processing ticket {ticket_key}: {str(e)}")
            self._stats['assessment_failures'] += 1
            result['success'] = False
            result['message'] = f"Error processing ticket: {str(e)}"
        
        self._update_stats(result)
        return result
    
    def process_project(self, 
                      project_key: str, 
                      max_tickets: Optional[int] = None, 
                      statuses_to_exclude: Optional[List[str]] = None,
                      dry_run: bool = True,
                      skip_prefilter: bool = False) -> Dict[str, Any]:
        """
        Process all tickets in a project using the configured analyzer.
        
        Args:
            project_key: The Jira project key
            max_tickets: Maximum number of tickets to process
            statuses_to_exclude: List of statuses to exclude
            dry_run: If True, only simulate actions without making changes
            skip_prefilter: If True, skip pre-filtering
            
        Returns:
            Dictionary with processing results
        """
        # Use default statuses if not provided
        statuses_to_exclude = statuses_to_exclude or ["Closed", "Done", "Resolved"]
        
        # Create project iterator - let analyzer determine filtering
        iterator = ProjectTicketIterator(
            jira_client=self.jira_client,
            project_key=project_key,
            statuses_to_exclude=statuses_to_exclude,
            max_results=max_tickets,
            # Generic processor doesn't assume specific filtering
            use_default_quiescence_filter=False,
        )
        
        results = {
            'project_key': project_key,
            'tickets_processed': 0,
            'tickets_prefiltered': 0,
            'tickets_needing_action': 0,
            'tickets_with_actions': 0,
            'processing_errors': 0,
            'results': []
        }
        
        try:
            # Iterate through tickets
            for ticket_key in iterator:
                # Get full ticket data
                ticket_data = iterator.get_ticket_data(ticket_key)
                
                # Process the individual ticket
                ticket_result = self.process(ticket_key, ticket_data, dry_run)
                
                # Update statistics
                results['tickets_processed'] += 1
                if ticket_result.get('success', False):
                    analysis_result = ticket_result.get('analysis_result', {})
                    if analysis_result and hasattr(analysis_result, 'needs_action'):
                        if analysis_result.needs_action():
                            results['tickets_needing_action'] += 1
                            if ticket_result.get('actions'):
                                results['tickets_with_actions'] += 1
                else:
                    results['processing_errors'] += 1
                
                # Add to results list
                results['results'].append(ticket_result)
                
                # Update progress every 10 tickets
                if results['tickets_processed'] % 10 == 0:
                    logger.info(f"Processed {results['tickets_processed']} tickets in {project_key}")
            
            return results
        except Exception as e:
            logger.error(f"Error processing project {project_key}: {str(e)}")
            results['error'] = str(e)
            return results
    
    def get_formatter(self) -> BaseFormatter:
        """Get the formatter for UI display."""
        return self.formatter
    
    def get_analyzer_type(self) -> str:
        """Get the analyzer type for logging and display."""
        return self.analyzer.get_analyzer_type()
    
    def describe_action(self, ticket_key: str, ticket_data: Dict[str, Any]) -> str:
        """
        Describe the action that would be taken for a ticket.
        
        Args:
            ticket_key: The Jira issue key
            ticket_data: The ticket data dictionary
            
        Returns:
            Human-readable description of the action
        """
        try:
            # Get assessment using the injected analyzer
            analysis_result = self.analyzer.analyze(ticket_data)
            
            if analysis_result.needs_action():
                status_text = self.formatter.get_status_text(analysis_result)
                return f"Would comment on ticket {ticket_key} as {status_text}: {analysis_result.justification}"
            else:
                status_text = self.formatter.get_status_text(analysis_result)
                return f"Would skip ticket {ticket_key} ({status_text}): {analysis_result.justification}"
        except Exception as e:
            return f"Unable to assess ticket {ticket_key}: {str(e)}"
