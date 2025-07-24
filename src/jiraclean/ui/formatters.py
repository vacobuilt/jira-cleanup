"""
Formatting functions for tickets, assessments, and other data structures.
"""

from typing import Dict, Any, Optional
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.console import Group

from jiraclean.ui.console import console


def format_ticket(ticket_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Format ticket data for display, extracting and cleaning key fields.
    
    Args:
        ticket_data: Raw ticket data from Jira
        
    Returns:
        Dictionary with formatted ticket fields
    """
    return {
        'key': ticket_data.get('key', 'UNKNOWN'),
        'type': ticket_data.get('issuetype', {}).get('name', 'Unknown') if isinstance(ticket_data.get('issuetype'), dict) else str(ticket_data.get('type', 'Unknown')),
        'status': ticket_data.get('status', {}).get('name', 'Unknown') if isinstance(ticket_data.get('status'), dict) else str(ticket_data.get('status', 'Unknown')),
        'summary': ticket_data.get('summary', 'No summary available'),
        'priority': ticket_data.get('priority', {}).get('name', 'Unknown') if isinstance(ticket_data.get('priority'), dict) else str(ticket_data.get('priority', 'Unknown')),
        'assignee': _format_user(ticket_data.get('assignee')),
        'reporter': _format_user(ticket_data.get('reporter')),
        'created': ticket_data.get('created', 'Unknown'),
        'updated': ticket_data.get('updated', 'Unknown')
    }


def format_assessment(assessment: Dict[str, Any]) -> Panel:
    """
    Format LLM assessment data into a Rich panel for display.
    
    Args:
        assessment: Assessment data from LLM
        
    Returns:
        Rich Panel with formatted assessment
    """
    is_quiescent = assessment.get('is_quiescent', False)
    justification = assessment.get('justification', 'No assessment available')
    responsible_party = assessment.get('responsible_party', 'Unknown')
    suggested_action = assessment.get('suggested_action', 'None')
    suggested_deadline = assessment.get('suggested_deadline', 'None')
    planned_comment = assessment.get('planned_comment', 'No comment planned')
    
    # Create assessment table
    table = Table.grid(padding=1)
    table.add_column(style="bold", justify="right", width=15)
    table.add_column(justify="left")
    
    # Style based on assessment result
    assessment_style = "assessment.quiescent" if is_quiescent else "assessment.active"
    assessment_text = "🟡 QUIESCENT" if is_quiescent else "🟢 ACTIVE"
    
    table.add_row("Status:", Text(assessment_text, style=assessment_style))
    table.add_row("Reason:", Text(justification, style="italic"))
    table.add_row("Responsible:", responsible_party)
    table.add_row("Suggested Action:", suggested_action)
    table.add_row("Deadline:", suggested_deadline)
    
    # Add comment section if available
    if planned_comment and planned_comment != 'No comment planned':
        table.add_row("", "")  # Spacer
        table.add_row("Planned Comment:", "")
        # Wrap long comments
        comment_text = Text(planned_comment, style="dim")
        table.add_row("", comment_text)
    
    border_style = "yellow" if is_quiescent else "green"
    title = "🤖 LLM Assessment"
    
    return Panel(
        table,
        title=title,
        border_style=border_style,
        padding=(1, 2)
    )


def format_error(error_message: str, context: Optional[str] = None) -> Panel:
    """
    Format error messages for display.
    
    Args:
        error_message: The error message
        context: Optional context information
        
    Returns:
        Rich Panel with formatted error
    """
    content = Text(error_message, style="error")
    
    if context:
        content = Group(
            Text(error_message, style="error"),
            Text(""),  # Spacer
            Text(f"Context: {context}", style="dim")
        )
    
    return Panel(
        content,
        title="❌ Error",
        border_style="red",
        padding=(1, 2)
    )


def format_dry_run_action(action: str, ticket_key: str) -> Text:
    """
    Format a dry run action for display.
    
    Args:
        action: Description of the action that would be taken
        ticket_key: The ticket key
        
    Returns:
        Formatted text for the action
    """
    return Text(f"[WOULD {action.upper()}] {ticket_key}", style="dry_run")


def format_production_action(action: str, ticket_key: str, success: bool = True) -> Text:
    """
    Format a production action for display.
    
    Args:
        action: Description of the action taken
        ticket_key: The ticket key
        success: Whether the action was successful
        
    Returns:
        Formatted text for the action
    """
    if success:
        return Text(f"[{action.upper()}] {ticket_key}", style="success")
    else:
        return Text(f"[FAILED {action.upper()}] {ticket_key}", style="error")


def format_ticket_summary(ticket_count: int, project: str) -> Text:
    """
    Format a summary of tickets being processed.
    
    Args:
        ticket_count: Number of tickets
        project: Project key
        
    Returns:
        Formatted summary text
    """
    return Text(f"Processing {ticket_count} tickets from project {project}", style="info")


def _format_user(user_data: Any) -> str:
    """
    Format user data (assignee/reporter) for display.
    
    Args:
        user_data: User data from Jira (can be dict, string, or None)
        
    Returns:
        Formatted user string
    """
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
        else:
            return "Unknown User"
    
    return str(user_data)


def format_processing_header(project: str, dry_run: bool, llm_enabled: bool, max_tickets: int) -> Panel:
    """
    Format the processing header with key information.
    
    Args:
        project: Project key
        dry_run: Whether in dry run mode
        llm_enabled: Whether LLM assessment is enabled
        max_tickets: Maximum number of tickets to process
        
    Returns:
        Rich Panel with processing information
    """
    mode_text = "🔍 DRY RUN MODE" if dry_run else "⚠️  PRODUCTION MODE"
    mode_style = "dry_run" if dry_run else "production"
    
    llm_text = "✅ LLM Assessment" if llm_enabled else "❌ No LLM Assessment"
    llm_style = "success" if llm_enabled else "warning"
    
    content = Table.grid(padding=1)
    content.add_column(style="bold", justify="right", width=15)
    content.add_column(justify="left")
    
    content.add_row("Mode:", Text(mode_text, style=mode_style))
    content.add_row("Project:", Text(project, style="ticket.key"))
    content.add_row("Max Tickets:", str(max_tickets))
    content.add_row("LLM:", Text(llm_text, style=llm_style))
    
    border_style = "yellow" if dry_run else "red"
    
    return Panel(
        content,
        title="🚀 Jira Cleanup Processing",
        border_style=border_style,
        padding=(1, 2)
    )
