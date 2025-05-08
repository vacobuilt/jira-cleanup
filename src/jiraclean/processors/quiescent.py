"""
Quiescent ticket processor implementation.

This module provides a processor that analyzes tickets for quiescence
using LLM assessment and takes appropriate actions.
"""

import logging
from typing import Dict, Any, List, Optional

from jiraclean.processors.base import TicketProcessor
from jiraclean.jirautil import JiraClient
from jiraclean.llm import assess_ticket, AssessmentResult

logger = logging.getLogger('jira_cleanup.processors.quiescent')


class QuiescentTicketProcessor(TicketProcessor):
    """
    Processor that detects and responds to quiescent tickets.
    
    This processor uses LLM assessment to determine if a ticket is quiescent,
    and takes action based on the assessment (e.g., adding a comment).
    """
    
    def __init__(self, 
                jira_client: JiraClient,
                llm_model: str = "llama3.2:latest",
                ollama_url: str = "http://localhost:11434"):
        """
        Initialize the quiescent ticket processor.
        
        Args:
            jira_client: JiraClient instance for Jira API access
            llm_model: LLM model to use for assessment
            ollama_url: URL for Ollama API
        """
        super().__init__()
        self.jira_client = jira_client
        self.llm_model = llm_model
        self.ollama_url = ollama_url
        
        # Additional statistics specific to quiescent detection
        self._stats.update({
            'quiescent': 0,
            'non_quiescent': 0,
            'assessment_failures': 0,
            'comments_added': 0
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
                    result['actions'].append({
                        'type': 'comment',
                        'description': 'Would add quiescent ticket comment (dry run)',
                        'success': True,
                        'details': {
                            'comment_body': assessment.planned_comment[:100] + '...',  # Truncate for logging
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
