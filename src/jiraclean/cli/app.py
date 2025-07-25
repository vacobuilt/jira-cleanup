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

# Version option is handled in commands.py main callback
