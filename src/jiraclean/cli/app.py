"""
Main Typer application for Jira Cleanup CLI.
"""

import typer
from typing import Optional
from rich.console import Console

from jiraclean.ui.console import console

# Create the main Typer app
app = typer.Typer(
    name="jiraclean",
    help="🎫 Jira Cleanup - A configurable tool for Jira ticket governance",
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True
)

# Version callback
def version_callback(value: bool):
    """Show version information."""
    if value:
        console.print("🎫 [bold blue]Jira Cleanup[/bold blue] version [green]0.1.0[/green]")
        console.print("A configurable, policy-based tool for automated Jira ticket governance")
        raise typer.Exit()

# Global options that apply to all commands
@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, 
        "--version", 
        callback=version_callback, 
        is_eager=True,
        help="Show version information and exit"
    ),
):
    """
    🎫 Jira Cleanup - A configurable tool for Jira ticket governance
    
    This tool helps maintain clean and efficient Jira workspaces by identifying
    and addressing tickets that need attention, providing accountability, and
    closing tickets that are no longer relevant.
    
    [bold green]Quick Examples:[/bold green]
    
    • [cyan]jiraclean --project PROJ --dry-run[/cyan] - Test run on project PROJ
    • [cyan]jiraclean config list[/cyan] - Show configured Jira instances  
    • [cyan]jiraclean setup[/cyan] - Interactive configuration setup
    
    [bold yellow]Safety First:[/bold yellow] Always use --dry-run first to preview changes!
    """
    pass
