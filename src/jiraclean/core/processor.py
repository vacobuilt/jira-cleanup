"""
Core ticket processing logic with Rich output formatting.

This module contains the main business logic extracted from the old CLI,
enhanced with Rich formatting for beautiful output.
"""

import logging
from typing import Dict, Any, Optional, Iterator
from dataclasses import dataclass

from jiraclean.ui.console import console
from jiraclean.ui.components import TicketCard, StatusIndicator, ProgressTracker, create_summary_table
from jiraclean.ui.formatters import format_processing_header, format_assessment, format_error
from jiraclean.iterators.project import ProjectTicketIterator
from jiraclean.processors.quiescent import QuiescentTicketProcessor
from jiraclean.llm import AssessmentResult

logger = logging.getLogger('jiraclean.core')


@dataclass
class ProcessingConfig:
    """Configuration for ticket processing."""
    project: str
    max_tickets: int
    dry_run: bool
    llm_enabled: bool
    llm_model: Optional[str] = None
    ollama_url: Optional[str] = None


@dataclass
class ProcessingStats:
    """Statistics from ticket processing."""
    processed: int = 0
    actioned: int = 0
    quiescent: int = 0
    non_quiescent: int = 0
    errors: int = 0
    skipped: int = 0


class TicketProcessor:
    """
    Core ticket processor with Rich output formatting.
    
    This class handles the main ticket processing logic with beautiful
    Rich-formatted output, progress tracking, and error handling.
    """
    
    def __init__(self, jira_client, config: ProcessingConfig):
        """
        Initialize the ticket processor.
        
        Args:
            jira_client: Configured Jira client instance
            config: Processing configuration
        """
        self.jira_client = jira_client
        self.config = config
        self.stats = ProcessingStats()
        
        # Create LLM processor if enabled
        self.llm_processor = None
        if config.llm_enabled:
            # Use defaults if not provided
            llm_model = config.llm_model or "llama3.2:latest"
            ollama_url = config.ollama_url or "http://localhost:11434"
            
            self.llm_processor = QuiescentTicketProcessor(
                jira_client=jira_client,
                llm_model=llm_model,
                ollama_url=ollama_url
            )
    
    def process_tickets(self) -> ProcessingStats:
        """
        Process tickets with Rich output formatting.
        
        Returns:
            Processing statistics
        """
        # Display processing header
        header = format_processing_header(
            project=self.config.project,
            dry_run=self.config.dry_run,
            llm_enabled=self.config.llm_enabled,
            max_tickets=self.config.max_tickets
        )
        console.print(header)
        console.print()
        
        # Create ticket iterator
        iterator = ProjectTicketIterator(
            jira_client=self.jira_client,
            project_key=self.config.project,
            max_results=self.config.max_tickets
        )
        
        # Set up progress tracking
        progress = ProgressTracker("Processing tickets")
        
        try:
            # Get ticket count for progress bar
            ticket_list = list(iterator)
            total_tickets = len(ticket_list)
            
            if total_tickets == 0:
                console.print(StatusIndicator.warning(
                    f"No matching tickets found for project {self.config.project}"
                ))
                return self.stats
            
            progress.start(total=total_tickets)
            
            # Process each ticket
            for ticket_key in ticket_list:
                try:
                    self._process_single_ticket(ticket_key, progress)
                except Exception as e:
                    self.stats.errors += 1
                    error_panel = format_error(
                        f"Error processing ticket {ticket_key}: {str(e)}",
                        "Check Jira connectivity and ticket permissions"
                    )
                    console.print(error_panel)
                    logger.error(f"Error processing {ticket_key}: {e}")
                
                progress.update(1)
            
            progress.stop()
            
            # Display summary
            self._display_summary()
            
        except Exception as e:
            progress.stop()
            error_panel = format_error(
                f"Fatal error during processing: {str(e)}",
                "Check configuration and try again"
            )
            console.print(error_panel)
            logger.error(f"Fatal processing error: {e}")
            self.stats.errors += 1
        
        return self.stats
    
    def _process_single_ticket(self, ticket_key: str, progress: ProgressTracker) -> None:
        """
        Process a single ticket with Rich formatting.
        
        Args:
            ticket_key: The Jira issue key
            progress: Progress tracker for updates
        """
        progress.update(description=f"Processing {ticket_key}")
        
        # Get ticket data
        ticket_data = self.jira_client.get_issue(ticket_key)
        self.stats.processed += 1
        
        # Format ticket data for display
        formatted_ticket = self._format_ticket_data(ticket_data)
        
        # Process with LLM if enabled
        assessment = None
        if self.llm_processor:
            try:
                result = self.llm_processor.process(
                    ticket_key, 
                    ticket_data, 
                    dry_run=self.config.dry_run
                )
                
                if result['success'] and 'assessment' in result:
                    assessment = AssessmentResult.from_dict(result['assessment'])
                    
                    # Update statistics
                    if assessment.is_quiescent:
                        self.stats.quiescent += 1
                    else:
                        self.stats.non_quiescent += 1
                    
                    # Count actions taken
                    if result['actions']:
                        self.stats.actioned += 1
                else:
                    self.stats.errors += 1
                    console.print(StatusIndicator.error(
                        f"LLM processing failed for {ticket_key}: {result['message']}"
                    ))
                    
            except Exception as e:
                self.stats.errors += 1
                console.print(StatusIndicator.error(
                    f"LLM error for {ticket_key}: {str(e)}"
                ))
                logger.error(f"LLM processing error for {ticket_key}: {e}")
        
        # Display ticket card with assessment
        ticket_card = TicketCard.create(formatted_ticket, assessment.to_dict() if assessment else None)
        console.print(ticket_card)
        
        # Display assessment details if available
        if assessment and self.config.dry_run:
            assessment_panel = format_assessment(assessment.to_dict())
            console.print(assessment_panel)
        
        console.print()  # Add spacing between tickets
    
    def _format_ticket_data(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format raw ticket data for display.
        
        Args:
            ticket_data: Raw ticket data from Jira
            
        Returns:
            Formatted ticket data
        """
        fields = ticket_data.get('fields', {})
        
        return {
            'key': ticket_data.get('key', 'UNKNOWN'),
            'type': self._safe_get_name(fields.get('issuetype')),
            'status': self._safe_get_name(fields.get('status')),
            'priority': self._safe_get_name(fields.get('priority')),
            'summary': fields.get('summary', 'No summary available'),
            'assignee': self._format_user(fields.get('assignee')),
            'reporter': self._format_user(fields.get('reporter')),
            'created': fields.get('created', 'Unknown'),
            'updated': fields.get('updated', 'Unknown')
        }
    
    def _safe_get_name(self, field_data: Any) -> str:
        """Safely extract name from Jira field data."""
        if isinstance(field_data, dict):
            return field_data.get('name', 'Unknown')
        return str(field_data) if field_data else 'Unknown'
    
    def _format_user(self, user_data: Any) -> str:
        """Format user data for display."""
        if not user_data:
            return "Unassigned"
        
        if isinstance(user_data, dict):
            display_name = user_data.get('displayName')
            email = user_data.get('emailAddress')
            name = user_data.get('name')
            
            if display_name:
                return display_name
            elif email:
                return email
            elif name:
                return name
        
        return str(user_data)
    
    def _display_summary(self) -> None:
        """Display processing summary with Rich formatting."""
        console.print()
        console.print(StatusIndicator.success("Processing completed!"))
        console.print()
        
        # Create summary table
        summary_table = create_summary_table({
            'processed': self.stats.processed,
            'actioned': self.stats.actioned,
            'quiescent': self.stats.quiescent,
            'non_quiescent': self.stats.non_quiescent,
            'errors': self.stats.errors,
            'skipped': self.stats.skipped
        })
        
        console.print(summary_table)
        
        # Display processor stats if available
        if self.llm_processor and hasattr(self.llm_processor, 'stats'):
            console.print()
            console.print(StatusIndicator.info("LLM Processor Statistics:"))
            for key, value in self.llm_processor.stats.items():
                console.print(f"  {key}: {value}")


def setup_templates(install_templates: bool = False, force: bool = False) -> int:
    """
    Set up template configuration with Rich output.
    
    Args:
        install_templates: Whether to install default templates
        force: Whether to force overwrite existing templates
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    from jiraclean.prompts.registry import PromptRegistry
    
    try:
        if install_templates:
            console.print(StatusIndicator.info(
                "Installing default templates to ~/.config/jiraclean/templates/"
            ))
            
            installed_files = PromptRegistry.install_default_templates(force=force)
            
            if installed_files:
                console.print(StatusIndicator.success(
                    f"Successfully installed {len(installed_files)} template(s)"
                ))
                for path in installed_files:
                    console.print(f"  • {path}")
            else:
                console.print(StatusIndicator.warning("No templates were installed"))
            
            console.print()
            console.print("You can edit these templates to customize the LLM prompts.")
            console.print("Templates are loaded in order of precedence:")
            console.print("  1. User templates (~/.config/jiraclean/templates/)")
            console.print("  2. System templates (/etc/jiraclean/templates/) - if available")
            console.print("  3. Built-in templates (package defaults)")
        else:
            console.print(StatusIndicator.info("Use --install-templates to set up default templates"))
            return 1
        
        return 0
    except Exception as e:
        error_panel = format_error(f"Error setting up templates: {str(e)}")
        console.print(error_panel)
        logger.error(f"Template setup error: {e}")
        return 1
