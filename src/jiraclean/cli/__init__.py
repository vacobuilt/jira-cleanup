"""
CLI module for Jira Cleanup using Typer.

This module provides the command-line interface for the Jira Cleanup tool,
including the main application commands and subcommands.
"""

from jiraclean.cli.app import app
from jiraclean.cli.commands import main_command, config_command, setup_command

__all__ = ['app', 'main_command', 'config_command', 'setup_command']
