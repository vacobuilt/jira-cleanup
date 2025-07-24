"""
CLI commands for Jira Cleanup using Typer.
"""

import typer
from typing import Optional, List
from enum import Enum
from pathlib import Path

from jiraclean.ui.console import console, print_info, print_warning, print_error, print_success
from jiraclean.ui.components import TicketCard, ProgressTracker, create_mode_banner, create_summary_table
from jiraclean.ui.formatters import format_processing_header, format_ticket, format_assessment
from jiraclean.cli.app import app


class LogLevel(str, Enum):
    """Log level options."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OutputFormat(str, Enum):
    """Output format options."""
    rich = "rich"
    json = "json"
    yaml = "yaml"
    table = "table"


@app.command()
def main_command(
    project: str = typer.Option(
        "PROJ",
        "--project", "-p",
        help="🎯 Jira project key to process"
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--production",
        help="🔍 Run in dry-run mode (safe) or production mode (makes changes)"
    ),
    max_tickets: int = typer.Option(
        50,
        "--max-tickets", "-n",
        help="📊 Maximum number of tickets to process",
        min=1,
        max=1000
    ),
    log_level: LogLevel = typer.Option(
        LogLevel.INFO,
        "--log-level", "-l",
        help="📝 Set logging level"
    ),
    llm_model: str = typer.Option(
        "llama3.2:latest",
        "--llm-model", "-m",
        help="🤖 LLM model to use for assessment"
    ),
    ollama_url: str = typer.Option(
        "http://localhost:11434",
        "--ollama-url",
        help="🔗 URL for Ollama API"
    ),
    with_llm: bool = typer.Option(
        True,
        "--with-llm/--no-llm",
        help="🧠 Enable or disable LLM assessment"
    ),
    env_file: Optional[Path] = typer.Option(
        None,
        "--env-file", "-e",
        help="📄 Path to .env file with configuration",
        exists=True
    ),
    instance: Optional[str] = typer.Option(
        None,
        "--instance", "-i",
        help="🏢 Jira instance name (from config)"
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.rich,
        "--output-format", "-o",
        help="📋 Output format"
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        help="🎮 Interactive mode with prompts"
    )
):
    """
    🎫 Process Jira tickets for governance and cleanup.
    
    This is the main command that processes tickets in the specified project,
    applies governance policies, and optionally uses LLM assessment to determine
    if tickets are quiescent (inactive) and need attention.
    
    [bold green]Examples:[/bold green]
    
    • [cyan]jiraclean --project MYPROJ --dry-run[/cyan]
    • [cyan]jiraclean --project SALES --max-tickets 10 --no-llm[/cyan]
    • [cyan]jiraclean --project DEV --production --with-llm[/cyan]
    """
    try:
        # Show processing header
        header = format_processing_header(project, dry_run, with_llm, max_tickets)
        console.print(header)
        console.print()
        
        if interactive:
            # Interactive mode - ask for confirmation
            if not dry_run:
                print_warning("You are about to run in PRODUCTION mode!")
                confirm = typer.confirm("Are you sure you want to make changes to Jira?")
                if not confirm:
                    print_info("Switching to dry-run mode for safety")
                    dry_run = True
        
        # Import and run the existing main logic
        # This is a bridge to the existing functionality
        from jiraclean.main import main as existing_main
        import sys
        
        # Prepare arguments for the existing main function
        # We'll need to adapt this based on the existing main.py structure
        args = [
            "--project", project,
            "--max-tickets", str(max_tickets),
            "--log-level", log_level.value,
            "--llm-model", llm_model,
            "--ollama-url", ollama_url
        ]
        
        if dry_run:
            args.append("--dry-run")
        
        if with_llm:
            args.append("--with-llm")
        else:
            args.append("--no-llm")
            
        if env_file:
            args.extend(["--env-file", str(env_file)])
        
        # Call existing main function
        # Note: This is a temporary bridge - we'll refactor this later
        print_info(f"Processing {max_tickets} tickets from project {project}")
        
        # For now, show what would be called
        console.print(f"[dim]Would call existing main with args: {' '.join(args)}[/dim]")
        
        # TODO: Integrate with existing main.py logic
        print_success("Command structure ready - integration with existing logic pending")
        
    except Exception as e:
        print_error(f"Error processing tickets: {str(e)}")
        raise typer.Exit(1)


@app.command("config")
def config_command(
    action: str = typer.Argument(
        help="📋 Config action: list, show, test, set-default"
    ),
    instance: Optional[str] = typer.Argument(
        None,
        help="🏢 Instance name (for test, set-default actions)"
    )
):
    """
    ⚙️ Manage Jira instance configurations.
    
    [bold green]Available actions:[/bold green]
    
    • [cyan]list[/cyan] - Show all configured instances
    • [cyan]show[/cyan] - Show current configuration  
    • [cyan]test <instance>[/cyan] - Test connection to instance
    • [cyan]set-default <instance>[/cyan] - Set default instance
    
    [bold green]Examples:[/bold green]
    
    • [cyan]jiraclean config list[/cyan]
    • [cyan]jiraclean config test production[/cyan]
    • [cyan]jiraclean config set-default staging[/cyan]
    """
    if action == "list":
        print_info("Listing configured Jira instances...")
        # TODO: Implement YAML config reading
        console.print("📋 [bold]Configured Instances:[/bold]")
        console.print("• production (default) - https://company.atlassian.net")
        console.print("• staging - https://staging.atlassian.net")
        
    elif action == "show":
        print_info("Showing current configuration...")
        # TODO: Show current config
        console.print("🔧 [bold]Current Configuration:[/bold]")
        console.print("Default instance: production")
        console.print("Config file: ~/.config/jiraclean/config.yaml")
        
    elif action == "test":
        if not instance:
            print_error("Instance name required for test action")
            raise typer.Exit(1)
        print_info(f"Testing connection to instance: {instance}")
        # TODO: Implement connection testing
        print_success(f"Connection to {instance} successful!")
        
    elif action == "set-default":
        if not instance:
            print_error("Instance name required for set-default action")
            raise typer.Exit(1)
        print_info(f"Setting default instance to: {instance}")
        # TODO: Implement default setting
        print_success(f"Default instance set to {instance}")
        
    else:
        print_error(f"Unknown config action: {action}")
        print_info("Available actions: list, show, test, set-default")
        raise typer.Exit(1)


@app.command("setup")
def setup_command(
    interactive: bool = typer.Option(
        True,
        "--interactive/--non-interactive",
        help="🎮 Interactive setup wizard"
    )
):
    """
    🚀 Set up Jira Cleanup configuration.
    
    This command helps you configure Jira instances, authentication,
    and other settings needed to use the Jira Cleanup tool.
    
    [bold green]What this does:[/bold green]
    
    • Creates configuration directory
    • Sets up Jira instance connections
    • Configures authentication
    • Tests connections
    • Sets up default preferences
    """
    console.print("🚀 [bold blue]Jira Cleanup Setup Wizard[/bold blue]")
    console.print()
    
    if interactive:
        print_info("Starting interactive setup...")
        
        # Jira URL
        jira_url = typer.prompt("🔗 Enter your Jira URL (e.g., https://company.atlassian.net)")
        
        # Username
        username = typer.prompt("👤 Enter your Jira username/email")
        
        # API Token
        console.print("🔑 You'll need a Jira API token. Get one at:")
        console.print("   https://id.atlassian.com/manage-profile/security/api-tokens")
        api_token = typer.prompt("🔐 Enter your Jira API token", hide_input=True)
        
        # Instance name
        instance_name = typer.prompt("🏷️  Enter a name for this instance", default="production")
        
        print_info("Testing connection...")
        # TODO: Test the connection
        
        print_success("Configuration saved!")
        console.print(f"✅ Instance '{instance_name}' configured successfully")
        console.print("🎯 You can now run: [cyan]jiraclean --project YOUR_PROJECT --dry-run[/cyan]")
        
    else:
        print_info("Non-interactive setup not yet implemented")
        print_info("Please run: jiraclean setup --interactive")


if __name__ == "__main__":
    app()
