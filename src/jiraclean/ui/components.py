"""
Rich UI components for displaying tickets, progress, and status information.
"""

from typing import Optional, Dict, Any
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
from rich.align import Align
from rich.columns import Columns

from jiraclean.ui.console import console


class TicketCard:
    """Rich component for displaying ticket information in a prominent card format."""
    
    @staticmethod
    def create(ticket_data: Dict[str, Any], assessment: Optional[Dict[str, Any]] = None) -> Panel:
        """
        Create a Rich panel displaying ticket information prominently.
        
        Args:
            ticket_data: Dictionary containing ticket information
            assessment: Optional LLM assessment data
            
        Returns:
            Rich Panel with formatted ticket information
        """
        # Extract ticket information
        key = ticket_data.get('key', 'UNKNOWN')
        ticket_type = ticket_data.get('type', 'Unknown')
        status = ticket_data.get('status', 'Unknown')
        summary = ticket_data.get('summary', 'No summary available')
        priority = ticket_data.get('priority', 'Unknown')
        assignee = ticket_data.get('assignee', 'Unassigned')
        reporter = ticket_data.get('reporter', 'Unknown')
        
        # Create the main ticket information table
        ticket_table = Table.grid(padding=1)
        ticket_table.add_column(style="bold", justify="right", width=12)
        ticket_table.add_column(justify="left")
        
        # Add ticket details
        ticket_table.add_row("Key:", Text(key, style="ticket.key"))
        ticket_table.add_row("Type:", Text(ticket_type, style="ticket.type"))
        ticket_table.add_row("Status:", Text(status, style="ticket.status"))
        ticket_table.add_row("Priority:", Text(priority, style="ticket.priority"))
        ticket_table.add_row("Assignee:", assignee)
        ticket_table.add_row("Reporter:", reporter)
        ticket_table.add_row("Summary:", Text(summary, style="bold"))
        
        # Create assessment section if provided
        content_parts = [ticket_table]
        
        if assessment:
            assessment_table = Table.grid(padding=1)
            assessment_table.add_column(style="bold", justify="right", width=12)
            assessment_table.add_column(justify="left")
            
            is_quiescent = assessment.get('is_quiescent', False)
            justification = assessment.get('justification', 'No assessment available')
            responsible_party = assessment.get('responsible_party', 'Unknown')
            suggested_action = assessment.get('suggested_action', 'None')
            
            # Style based on assessment result
            assessment_style = "assessment.quiescent" if is_quiescent else "assessment.active"
            assessment_text = "QUIESCENT" if is_quiescent else "ACTIVE"
            
            assessment_table.add_row("", "")  # Spacer
            assessment_table.add_row("Assessment:", Text(assessment_text, style=assessment_style))
            assessment_table.add_row("Reason:", Text(justification, style="italic"))
            assessment_table.add_row("Responsible:", responsible_party)
            assessment_table.add_row("Action:", suggested_action)
            
            content_parts.append(assessment_table)
        
        # Combine all content
        content = Columns(content_parts, equal=False, expand=True)
        
        # Create panel with appropriate styling
        title_style = "ticket.key"
        border_style = "blue"
        
        if assessment:
            if assessment.get('is_quiescent'):
                border_style = "yellow"
            elif assessment.get('assessment_failed'):
                border_style = "red"
        
        return Panel(
            content,
            title=f"🎫 Ticket {key}",
            title_align="left",
            border_style=border_style,
            padding=(1, 2)
        )


class StatusIndicator:
    """Component for displaying status indicators with icons and colors."""
    
    @staticmethod
    def success(message: str) -> Text:
        """Create a success status indicator."""
        return Text(f"✅ {message}", style="success")
    
    @staticmethod
    def warning(message: str) -> Text:
        """Create a warning status indicator."""
        return Text(f"⚠️  {message}", style="warning")
    
    @staticmethod
    def error(message: str) -> Text:
        """Create an error status indicator."""
        return Text(f"❌ {message}", style="error")
    
    @staticmethod
    def info(message: str) -> Text:
        """Create an info status indicator."""
        return Text(f"ℹ️  {message}", style="info")
    
    @staticmethod
    def processing(message: str) -> Text:
        """Create a processing status indicator."""
        return Text(f"⚙️  {message}", style="info")


class ProgressTracker:
    """Component for tracking and displaying progress of operations."""
    
    def __init__(self, description: str = "Processing"):
        """Initialize progress tracker."""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        )
        self.task_id = None
        self.description = description
    
    def start(self, total: Optional[int] = None) -> None:
        """Start the progress tracker."""
        self.progress.start()
        self.task_id = self.progress.add_task(self.description, total=total)
    
    def update(self, advance: int = 1, description: Optional[str] = None) -> None:
        """Update progress."""
        if self.task_id is not None:
            if description:
                self.progress.update(self.task_id, advance=advance, description=description)
            else:
                self.progress.update(self.task_id, advance=advance)
    
    def stop(self) -> None:
        """Stop the progress tracker."""
        if self.progress:
            self.progress.stop()


def create_summary_table(stats: Dict[str, Any]) -> Table:
    """Create a summary table for processing statistics."""
    table = Table(title="Processing Summary", show_header=True, header_style="bold magenta")
    
    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Count", justify="right", style="green", width=10)
    table.add_column("Details", style="white")
    
    # Add statistics rows
    table.add_row("Tickets Processed", str(stats.get('processed', 0)), "Total tickets examined")
    table.add_row("Actions Taken", str(stats.get('actioned', 0)), "Comments added or status changes")
    table.add_row("Quiescent Found", str(stats.get('quiescent', 0)), "Tickets identified as inactive")
    table.add_row("Active Tickets", str(stats.get('non_quiescent', 0)), "Tickets with recent activity")
    table.add_row("Errors", str(stats.get('errors', 0)), "Processing failures")
    table.add_row("Skipped", str(stats.get('skipped', 0)), "Tickets not processed")
    
    return table


def create_mode_banner(dry_run: bool, llm_enabled: bool, project: str) -> Panel:
    """Create a banner showing current operation mode."""
    mode_text = "🔍 DRY RUN MODE" if dry_run else "⚠️  PRODUCTION MODE"
    mode_style = "dry_run" if dry_run else "production"
    
    llm_text = "✅ LLM Assessment Enabled" if llm_enabled else "❌ LLM Assessment Disabled"
    llm_style = "success" if llm_enabled else "warning"
    
    content = Table.grid(padding=1)
    content.add_column(justify="center")
    
    content.add_row(Text(mode_text, style=mode_style))
    content.add_row(Text(llm_text, style=llm_style))
    content.add_row(Text(f"📋 Project: {project}", style="info"))
    
    border_style = "yellow" if dry_run else "red"
    
    return Panel(
        Align.center(content),
        title="Operation Mode",
        border_style=border_style,
        padding=(1, 2)
    )
