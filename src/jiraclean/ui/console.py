"""
Rich console singleton for consistent terminal output across the application.
"""

from rich.console import Console
from rich.theme import Theme

# Define a custom theme for consistent styling
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "ticket.key": "bold blue",
    "ticket.type": "magenta",
    "ticket.status": "green",
    "ticket.priority": "red",
    "assessment.quiescent": "yellow",
    "assessment.active": "green",
    "assessment.failed": "red",
    "dry_run": "bold yellow",
    "production": "bold red"
})

# Create a singleton console instance
console = Console(theme=custom_theme, width=120)

# Convenience functions for common output patterns
def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"ℹ️  {message}", style="info")

def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"⚠️  {message}", style="warning")

def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"❌ {message}", style="error")

def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"✅ {message}", style="success")

def print_dry_run_notice() -> None:
    """Print a prominent dry run notice."""
    console.print("\n🔍 DRY RUN MODE - No changes will be made to Jira\n", style="dry_run")

def print_production_warning() -> None:
    """Print a prominent production mode warning."""
    console.print("\n⚠️  PRODUCTION MODE - Changes will be made to Jira!\n", style="production")
