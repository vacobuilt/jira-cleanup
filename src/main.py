#!/usr/bin/env python3
"""
Command-line interface for Jira Cleanup.

This module serves as the entry point for the Jira Cleanup tool,
providing command-line options for running ticket governance tasks.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Import utilities
from utils.config import (
    load_environment_config,
    validate_config,
    setup_argument_parser
)

# Import core components
from jirautil import create_jira_client
from iterators.project import ProjectTicketIterator
from processors.quiescent import QuiescentTicketProcessor
from llm import AssessmentResult

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('jira_cleanup')


def display_assessment(ticket_key: str, assessment: AssessmentResult) -> None:
    """
    Display assessment results in a readable format.
    
    Args:
        ticket_key: The Jira issue key
        assessment: LLM assessment result
    """
    print("\n=== LLM ASSESSMENT RESULTS ===")
    print(f"Ticket: {ticket_key}")
    print(f"Is Quiescent: {assessment.is_quiescent}")
    print(f"Justification: {assessment.justification}")
    print(f"Responsible Party: {assessment.responsible_party}")
    print(f"Suggested Action: {assessment.suggested_action}")
    print(f"Suggested Deadline: {assessment.suggested_deadline}")
    
    # Display the planned comment
    print("\n--- PLANNED COMMENT ---")
    print(f"{assessment.planned_comment}")
    print("=" * 50)


def process_tickets(jira_client, args) -> int:
    """
    Process tickets according to command-line arguments.
    
    Args:
        jira_client: Configured Jira client instance
        args: Parsed command-line arguments
        
    Returns:
        Count of processed tickets
    """
    # Create ticket iterator
    iterator = ProjectTicketIterator(
        jira_client=jira_client,
        project_key=args.project,
        max_results=args.max_tickets
    )
    
    # Create processor if using LLM assessment
    processor = None
    if not args.no_llm:
        processor = QuiescentTicketProcessor(
            jira_client=jira_client,
            llm_model=args.llm_model,
            ollama_url=args.ollama_url
        )
    
    # Print header
    print(f"\nProcessing tickets for project {args.project}")
    print(f"LLM assessment: {'Enabled' if not args.no_llm else 'Disabled'}")
    print(f"Dry run mode: {args.dry_run}")
    print("-" * 50)
    
    # Process tickets
    ticket_count = 0
    
    for ticket_key in iterator:
        ticket_count += 1
        ticket_data = jira_client.get_issue(ticket_key)
        
        # Extract useful info
        summary = ticket_data.get('fields', {}).get('summary', 'No summary available')
        status = ticket_data.get('fields', {}).get('status', {}).get('name', 'Unknown')
        issue_type = ticket_data.get('fields', {}).get('issuetype', {}).get('name', 'Unknown')
        
        print(f"\nTicket {ticket_count}: {ticket_key}")
        print(f"  Type: {issue_type}")
        print(f"  Status: {status}")
        print(f"  Summary: {summary}")
        
        # Process with LLM if enabled
        if processor:
            result = processor.process(ticket_key, ticket_data, dry_run=args.dry_run)
            
            # Display assessment result
            if result['success'] and 'assessment' in result:
                assessment = AssessmentResult.from_dict(result['assessment'])
                
                if args.dry_run:
                    display_assessment(ticket_key, assessment)
                else:
                    # In non-dry-run mode, just show a summary
                    print(f"  Assessment: {'Quiescent' if assessment.is_quiescent else 'Not quiescent'}")
                    if assessment.is_quiescent:
                        print(f"  Action: Comment added")
                
                # Show actions taken
                if result['actions']:
                    for action in result['actions']:
                        print(f"  {action['description']}")
            else:
                print(f"  Error: {result['message']}")
        else:
            # Simple mode without LLM
            print("  No LLM assessment performed (--no-llm specified)")
        
        print("-" * 50)
    
    # Print summary
    if ticket_count == 0:
        print(f"No matching tickets found for project {args.project}")
    else:
        print(f"\nProcessed {ticket_count} tickets from project {args.project}")
        
        # Print processor stats if available
        if processor:
            print("\nProcessor statistics:")
            for key, value in processor.stats.items():
                print(f"  {key}: {value}")
    
    return ticket_count


def show_version() -> None:
    """Display version information and exit."""
    from src import __version__
    print(f"Jira Cleanup v{__version__}")
    sys.exit(0)


def main() -> int:
    """
    Main entry point for Jira Cleanup.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Load configuration from .env and environment variables
    config = load_environment_config()
    
    # Setup argument parser
    parser = setup_argument_parser(config)
    args = parser.parse_args()
    
    # Load specific .env file if provided
    if args.env_file:
        # Reload config with the specified env file
        config = load_environment_config(args.env_file)
    
    # Show version if requested
    if args.version:
        show_version()
    
    # Set log level from args
    log_level = getattr(logging, args.log_level, logging.INFO)
    logger.setLevel(log_level)
    
    # Update config with CLI args
    config['defaults']['project'] = args.project
    config['defaults']['dry_run'] = args.dry_run
    config['defaults']['llm_model'] = args.llm_model
    config['defaults']['ollama_url'] = args.ollama_url
    
    # Handle conflicting LLM options
    if args.no_llm:
        args.with_llm = False
    
    # Validate combined configuration
    if not validate_config(config, args):
        parser.print_help()
        return 1
    
    # Log configuration
    logger.info(f"Starting Jira Cleanup for project {args.project}")
    logger.info(f"Dry run mode: {args.dry_run}")
    logger.info(f"LLM assessment: {'Enabled' if not args.no_llm else 'Disabled'}")
    
    try:
        # Create Jira client using the factory function
        jira_client = create_jira_client(
            url=config['jira']['url'],
            auth_method=config['jira']['auth_method'],
            username=config['jira']['username'],
            token=config['jira']['token'],
            dry_run=args.dry_run  # This determines which client type is created
        )
        
        # Process tickets
        processed_count = process_tickets(jira_client, args)
        logger.info(f"Processed {processed_count} tickets")
        
        return 0
    except Exception as e:
        logger.error(f"Error processing tickets: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
