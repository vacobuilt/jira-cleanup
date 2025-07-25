"""
Quality analysis result formatter.

This module provides the formatter for quality analysis results,
handling all quality-specific UI display logic including colors,
terminology, and layout.
"""

from typing import Dict, Any
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns

from jiraclean.ui.result_formatters.base_formatter import BaseFormatter
from jiraclean.ui.console import console


class QualityFormatter(BaseFormatter):
    """Formatter for quality analysis results."""
    
    def format_ticket_card(self, ticket_data: Dict[str, Any], result) -> Panel:
        """Format ticket card with quality assessment."""
        # Extract ticket information
        key = ticket_data.get('key', 'UNKNOWN')
        ticket_type = ticket_data.get('type', 'Unknown')
        status = ticket_data.get('status', 'Unknown')
        summary = ticket_data.get('summary', 'No summary available')
        priority = ticket_data.get('priority', 'Unknown')
        assignee = ticket_data.get('assignee', 'Unassigned')
        reporter = ticket_data.get('reporter', 'Unknown')
        
        # Create ticket info table
        ticket_table = Table.grid(padding=1)
        ticket_table.add_column(style="bold", justify="right", width=12)
        ticket_table.add_column(justify="left")
        
        ticket_table.add_row("Key:", Text(key, style="ticket.key"))
        ticket_table.add_row("Type:", Text(ticket_type, style="ticket.type"))
        ticket_table.add_row("Status:", Text(status, style="ticket.status"))
        ticket_table.add_row("Priority:", Text(priority, style="ticket.priority"))
        ticket_table.add_row("Assignee:", assignee)
        ticket_table.add_row("Reporter:", reporter)
        ticket_table.add_row("Summary:", Text(summary, style="bold"))
        
        # Create assessment table
        assessment_table = Table.grid(padding=1)
        assessment_table.add_column(style="bold", justify="right", width=12)
        assessment_table.add_column(justify="left")
        
        status_text = self.get_status_text(result)
        status_style = self.get_status_style(result)
        
        assessment_table.add_row("", "")  # Spacer
        assessment_table.add_row("Assessment:", Text(status_text, style=status_style))
        assessment_table.add_row("Quality Score:", f"{result.quality_score}/10")
        assessment_table.add_row("Assessment:", Text(result.quality_assessment, style="italic"))
        assessment_table.add_row("Responsible:", result.responsible_party)
        assessment_table.add_row("Action:", result.get_suggested_action())
        
        # Add improvement suggestions if any
        if result.improvement_suggestions:
            suggestions_text = ", ".join(result.improvement_suggestions[:3])  # Show first 3
            if len(result.improvement_suggestions) > 3:
                suggestions_text += f" (+{len(result.improvement_suggestions) - 3} more)"
            assessment_table.add_row("Improvements:", suggestions_text)
        
        content = Columns([ticket_table, assessment_table], equal=False, expand=True)
        border_style = self.get_border_style(result)
        
        return Panel(
            content,
            title=f"🎫 Ticket {key}",
            title_align="left",
            border_style=border_style,
            padding=(1, 2)
        )
    
    def format_assessment_panel(self, result) -> Panel:
        """Format detailed assessment panel."""
        content = Table.grid(padding=1)
        content.add_column(style="bold", justify="right", width=15)
        content.add_column(justify="left")
        
        status_text = self.get_status_text(result)
        status_style = self.get_status_style(result)
        
        content.add_row("Status:", Text(status_text, style=status_style))
        content.add_row("Quality Score:", f"{result.quality_score}/10")
        content.add_row("Assessment:", Text(result.quality_assessment, style="italic"))
        content.add_row("Responsible:", result.responsible_party)
        content.add_row("Suggested Action:", result.get_suggested_action())
        content.add_row("Deadline:", result.suggested_deadline)
        
        # Show all improvement suggestions
        if result.improvement_suggestions:
            content.add_row("", "")
            content.add_row("Improvements Needed:", "")
            for i, suggestion in enumerate(result.improvement_suggestions, 1):
                content.add_row("", f"{i}. {suggestion}")
        
        content.add_row("", "")
        content.add_row("Planned Comment:", "")
        content.add_row("", Text(result.planned_comment, style="dim"))
        
        border_style = self.get_border_style(result)
        
        return Panel(
            content,
            title="🤖 Quality Assessment",
            border_style=border_style,
            padding=(1, 2)
        )
    
    def format_summary_stats(self, stats: Dict[str, Any]) -> Table:
        """Format quality-specific summary statistics."""
        table = Table(title="Processing Summary", show_header=True, header_style="bold magenta")
        
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Count", justify="right", style="green", width=10)
        table.add_column("Details", style="white")
        
        table.add_row("Tickets Processed", str(stats.get('processed', 0)), "Total tickets examined")
        table.add_row("Actions Taken", str(stats.get('actioned', 0)), "Comments added or improvements suggested")
        table.add_row("Needs Improvement", str(stats.get('needs_improvement', 0)), "Tickets with quality issues")
        table.add_row("Good Quality", str(stats.get('good_quality', 0)), "Tickets meeting quality standards")
        table.add_row("Errors", str(stats.get('errors', 0)), "Processing failures")
        table.add_row("Skipped", str(stats.get('skipped', 0)), "Tickets not processed")
        
        return table
    
    def get_status_text(self, result) -> str:
        """Get status text for quality."""
        if result.needs_improvement:
            return "🔴 NEEDS IMPROVEMENT"
        else:
            return "🟢 GOOD QUALITY"
    
    def get_status_style(self, result) -> str:
        """Get Rich style for status."""
        return "assessment.needs_improvement" if result.needs_improvement else "assessment.good_quality"
    
    def get_border_style(self, result) -> str:
        """Get border style for panels."""
        return "red" if result.needs_improvement else "green"
