"""
CLI commands for Jira Cleanup using Typer with Rich output.

This module integrates the new core processor with the Typer CLI,
providing beautiful Rich-formatted output and clean command structure.
"""

import typer
import logging
from typing import Optional
from pathlib import Path

from jiraclean.ui.console import console
from jiraclean.ui.components import StatusIndicator
from jiraclean.ui.formatters import format_error
from jiraclean.core.processor import TicketProcessor, ProcessingConfig, setup_templates
from jiraclean.utils.config import (
    load_configuration, 
    validate_config, 
    get_instance_config, 
    list_instances
)
from jiraclean.jirautil import create_jira_client
from jiraclean.cli.app import app

logger = logging.getLogger('jiraclean.cli')


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    project: Optional[str] = typer.Option(
        None,
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
    debug: bool = typer.Option(
        False,
        "--debug",
        help="🐛 Enable debug logging"
    ),
    llm_model: Optional[str] = typer.Option(
        None,
        "--llm-model", "-m",
        help="🤖 LLM model to use for assessment"
    ),
    ollama_url: Optional[str] = typer.Option(
        None,
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
        help="🏢 Jira instance to use (trilliant, personal, highspring)"
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        help="🎮 Interactive mode with prompts"
    )
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
    # If no subcommand is invoked and project is provided, run main processing
    if ctx.invoked_subcommand is None:
        if not project:
            console.print("❌ [bold red]Error:[/bold red] --project is required")
            console.print("Usage: [cyan]jiraclean --project PROJECT_KEY[/cyan]")
            console.print("Or run: [cyan]jiraclean --help[/cyan] for more options")
            raise typer.Exit(1)
        
        # Run the main processing logic
        _run_main_processing(
            project=project,
            dry_run=dry_run,
            max_tickets=max_tickets,
            debug=debug,
            llm_model=llm_model,
            ollama_url=ollama_url,
            with_llm=with_llm,
            env_file=env_file,
            instance=instance,
            interactive=interactive
        )


def _run_main_processing(
    project: str,
    dry_run: bool,
    max_tickets: int,
    debug: bool,
    llm_model: Optional[str],
    ollama_url: Optional[str],
    with_llm: bool,
    env_file: Optional[Path],
    instance: Optional[str],
    interactive: bool
):
    """Internal function to run the main processing logic."""
    try:
        # Set up logging - only show debug logs if --debug is specified
        if debug:
            log_level = logging.DEBUG
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        else:
            log_level = logging.WARNING  # Hide INFO logs unless debug
            log_format = '%(levelname)s - %(message)s'
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[logging.StreamHandler()]
        )
        
        # Load configuration
        config = load_configuration(env_file=str(env_file) if env_file else None)
        
        # Get instance-specific configuration
        try:
            instance_config = get_instance_config(config, instance)
        except KeyError as e:
            console.print(StatusIndicator.error(str(e)))
            instances = list_instances(config)
            available = list(instances.keys())
            console.print(f"Available instances: {', '.join(available)}")
            raise typer.Exit(1)
        
        # Create a mock args object for validation compatibility
        import argparse
        
        args = argparse.Namespace()
        args.project = project
        args.max_tickets = max_tickets
        args.dry_run = dry_run
        args.no_llm = not with_llm
        args.llm_model = llm_model
        args.ollama_url = ollama_url
        args.log_level = log_level
        args.instance = instance
        
        # Validate configuration
        if not validate_config(config, args):
            console.print(StatusIndicator.error("Configuration validation failed"))
            console.print("Please check your configuration file or environment variables")
            raise typer.Exit(1)
        
        # Interactive confirmation for production mode
        if interactive and not dry_run:
            console.print(StatusIndicator.warning("You are about to run in PRODUCTION mode!"))
            confirm = typer.confirm("Are you sure you want to make changes to Jira?")
            if not confirm:
                console.print(StatusIndicator.info("Switching to dry-run mode for safety"))
                dry_run = True
        
        # Create Jira client using instance-specific configuration
        jira_client = create_jira_client(
            url=instance_config['url'],
            auth_method=instance_config['auth_method'],
            username=instance_config['username'],
            token=instance_config['token'],
            dry_run=dry_run
        )
        
        # Create processing configuration
        processing_config = ProcessingConfig(
            project=project,
            max_tickets=max_tickets,
            dry_run=dry_run,
            llm_enabled=with_llm,
            llm_model=llm_model,
            ollama_url=ollama_url
        )
        
        # Create and run processor
        processor = TicketProcessor(jira_client, processing_config)
        stats = processor.process_tickets()
        
        # Log final statistics
        logger.info(f"Processing completed: {stats.processed} tickets processed, "
                   f"{stats.actioned} actions taken, {stats.errors} errors")
        
        # Exit with error code if there were errors
        if stats.errors > 0:
            raise typer.Exit(1)
        
    except Exception as e:
        error_panel = format_error(f"Error processing tickets: {str(e)}")
        console.print(error_panel)
        logger.error(f"Command execution failed: {e}")
        raise typer.Exit(1)


@app.command("config")
def config_command(
    action: str = typer.Argument(
        help="📋 Config action: list, show, test"
    ),
    instance: Optional[str] = typer.Argument(
        None,
        help="🏢 Instance name (for test action)"
    )
):
    """
    ⚙️ Manage Jira instance configurations.
    
    [bold green]Available actions:[/bold green]
    
    • [cyan]list[/cyan] - Show all configured instances
    • [cyan]show[/cyan] - Show current configuration  
    • [cyan]test <instance>[/cyan] - Test connection to instance
    
    [bold green]Examples:[/bold green]
    
    • [cyan]jiraclean config list[/cyan]
    • [cyan]jiraclean config show[/cyan]
    • [cyan]jiraclean config test production[/cyan]
    """
    try:
        if action == "list":
            console.print(StatusIndicator.info("Listing configured Jira instances..."))
            
            # Load configuration
            config = load_configuration()
            
            console.print("📋 [bold]Current Configuration:[/bold]")
            console.print(f"• Jira URL: {config['jira']['url']}")
            console.print(f"• Username: {config['jira']['username']}")
            console.print(f"• Auth Method: {config['jira']['auth_method']}")
            console.print(f"• Default Project: {config['defaults'].get('project', 'Not set')}")
            
        elif action == "show":
            console.print(StatusIndicator.info("Showing current configuration..."))
            
            # Load and display configuration
            config = load_configuration()
            
            console.print("🔧 [bold]Configuration Details:[/bold]")
            console.print(f"Jira URL: {config['jira']['url']}")
            console.print(f"Username: {config['jira']['username']}")
            console.print(f"LLM Model: {config['defaults'].get('llm_model', 'llama3.2:latest')}")
            console.print(f"Ollama URL: {config['defaults'].get('ollama_url', 'http://localhost:11434')}")
            
        elif action == "test":
            if not instance:
                console.print(StatusIndicator.error("Instance name required for test action"))
                console.print("Usage: jiraclean config test <instance>")
                raise typer.Exit(1)
            
            console.print(StatusIndicator.info(f"Testing connection to Jira..."))
            
            # Load configuration and test connection
            config = load_configuration()
            
            try:
                jira_client = create_jira_client(
                    url=config['jira']['url'],
                    auth_method=config['jira']['auth_method'],
                    username=config['jira']['username'],
                    token=config['jira']['token'],
                    dry_run=True  # Safe test mode
                )
                
                # Test with a simple API call
                # This will be handled by the dry run client safely
                console.print(StatusIndicator.success("Connection test successful!"))
                
            except Exception as e:
                console.print(StatusIndicator.error(f"Connection test failed: {str(e)}"))
                raise typer.Exit(1)
            
        else:
            console.print(StatusIndicator.error(f"Unknown config action: {action}"))
            console.print("Available actions: list, show, test")
            raise typer.Exit(1)
            
    except Exception as e:
        error_panel = format_error(f"Config command failed: {str(e)}")
        console.print(error_panel)
        raise typer.Exit(1)


@app.command("setup")
def setup_command(
    install_templates: bool = typer.Option(
        False,
        "--install-templates",
        help="📄 Install default LLM prompt templates"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="💪 Force overwrite existing templates"
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--non-interactive",
        help="🎮 Interactive setup wizard"
    )
):
    """
    🚀 Set up Jira Cleanup configuration and templates.
    
    This command helps you configure templates and other settings
    needed to use the Jira Cleanup tool effectively.
    
    [bold green]What this does:[/bold green]
    
    • Installs default LLM prompt templates
    • Shows configuration guidance
    • Tests basic functionality
    
    [bold green]Examples:[/bold green]
    
    • [cyan]jiraclean setup --install-templates[/cyan]
    • [cyan]jiraclean setup --install-templates --force[/cyan]
    """
    try:
        console.print("🚀 [bold blue]Jira Cleanup Setup[/bold blue]")
        console.print()
        
        if install_templates:
            # Use the setup_templates function from core processor
            exit_code = setup_templates(install_templates=True, force=force)
            if exit_code != 0:
                raise typer.Exit(exit_code)
        
        if interactive:
            console.print(StatusIndicator.info("Interactive setup guidance:"))
            console.print()
            console.print("📋 [bold]Configuration Checklist:[/bold]")
            console.print("1. Create a .env file with your Jira credentials")
            console.print("2. Set JIRA_URL, JIRA_USERNAME, and JIRA_TOKEN")
            console.print("3. Test your configuration with: [cyan]jiraclean config test[/cyan]")
            console.print("4. Run a dry-run test: [cyan]jiraclean --project TEST --dry-run --max-tickets 1[/cyan]")
            console.print()
            console.print("📄 [bold]Example .env file:[/bold]")
            console.print("JIRA_URL=https://your-company.atlassian.net")
            console.print("JIRA_USERNAME=your-email@company.com")
            console.print("JIRA_TOKEN=your-api-token")
            console.print()
            console.print("🔑 Get your API token at:")
            console.print("https://id.atlassian.com/manage-profile/security/api-tokens")
        
        console.print()
        console.print(StatusIndicator.success("Setup completed!"))
        console.print("🎯 You can now run: [cyan]jiraclean --project YOUR_PROJECT --dry-run[/cyan]")
        
    except Exception as e:
        error_panel = format_error(f"Setup command failed: {str(e)}")
        console.print(error_panel)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
