"""
Configuration utilities for Jira Cleanup.

This module provides functions for loading and validating
configuration from environment variables and .env files.
"""

import os
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

from dotenv import load_dotenv

logger = logging.getLogger('jira_cleanup.utils.config')


def load_environment_config(env_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from .env file and environment variables.
    
    First checks for specified .env file, then current directory, then user's home.
    Falls back to environment variables if .env file is not found.
    
    Args:
        env_file: Optional path to specific .env file to load
        
    Returns:
        Dictionary with configuration values
    """
    # Start with specific env file if provided
    dotenv_loaded = False
    if env_file:
        env_path = Path(env_file)
        if env_path.exists():
            logger.info(f"Loading environment from {env_path}")
            load_dotenv(dotenv_path=env_path)
            dotenv_loaded = True
    
    if not dotenv_loaded:
        # Locations to search for .env file
        dotenv_paths = [
            Path('.env'),  # Current directory
            Path.home() / '.env',  # User's home directory
        ]
        
        # Try to load from .env file
        for dotenv_path in dotenv_paths:
            if dotenv_path.exists():
                logger.info(f"Loading environment from {dotenv_path}")
                load_dotenv(dotenv_path=dotenv_path)
                dotenv_loaded = True
                break
        
        if not dotenv_loaded:
            logger.warning("No .env file found. Using environment variables directly.")
    
    # Load configuration
    config = {
        'jira': {
            'url': os.getenv('JIRA_URL', ''),
            'username': os.getenv('JIRA_USER', ''),
            'token': os.getenv('JIRA_TOKEN', ''),
            'auth_method': os.getenv('JIRA_AUTH_METHOD', 'token')
        },
        'logging': {
            'level': os.getenv('JIRA_CLEANUP_LOG_LEVEL', 'INFO'),
        },
        'defaults': {
            'dry_run': os.getenv('JIRA_CLEANUP_DRY_RUN', 'true').lower() == 'true',
            'force_dry_run': os.getenv('FORCE_DRY_RUN', 'false').lower() == 'true',
            'project': os.getenv('JIRA_CLEANUP_PROJECT', ''),
            'ollama_url': os.getenv('OLLAMA_URL', 'http://localhost:11434'),
            'llm_model': os.getenv('LLM_MODEL', 'llama3.2:latest')
        }
    }
    
    return config


def validate_config(config: Dict[str, Any], args: argparse.Namespace) -> bool:
    """
    Validate the combined configuration from environment and CLI args.
    
    Args:
        config: Configuration dictionary
        args: Parsed command-line arguments
        
    Returns:
        True if configuration is valid, False otherwise
    """
    # Check required Jira settings
    if not config['jira']['url']:
        logger.error("JIRA_URL environment variable is required")
        return False
    
    if not config['jira']['username']:
        logger.error("JIRA_USER environment variable is required")
        return False
    
    if not config['jira']['token'] and config['jira']['auth_method'] == 'token':
        logger.error("JIRA_TOKEN environment variable is required for token auth method")
        return False
    
    # Check if project is specified
    if not args.project:
        logger.error("Project key is required (use --project or JIRA_CLEANUP_PROJECT)")
        return False
    
    # Check if FORCE_DRY_RUN requires dry run mode
    if config['defaults']['force_dry_run'] and not args.dry_run:
        logger.error("FORCE_DRY_RUN is set to true in the environment, but --dry-run flag is not provided")
        logger.error("For safety, the program will not run in live mode when FORCE_DRY_RUN is enabled")
        return False
    
    return True


def setup_argument_parser(config: Dict[str, Any]) -> argparse.ArgumentParser:
    """
    Set up the command-line argument parser with consistent defaults.
    
    Args:
        config: Configuration dictionary from environment
        
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='Jira Cleanup - A configurable tool for Jira ticket governance',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--project',
        type=str,
        default=config['defaults']['project'],
        help='Jira project key to process'
    )
    
    # Set dry-run default based on both environment variables
    dry_run_default = config['defaults']['dry_run'] or config['defaults']['force_dry_run']
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=dry_run_default,
        help='Run without making changes to Jira'
    )
    
    parser.add_argument(
        '--max-tickets',
        type=int,
        default=50,
        help='Maximum number of tickets to process'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default=config['logging']['level'],
        help='Set logging level'
    )
    
    parser.add_argument(
        '--llm-model',
        type=str,
        default=config['defaults']['llm_model'],
        help='LLM model to use for assessment'
    )
    
    parser.add_argument(
        '--ollama-url',
        type=str,
        default=config['defaults']['ollama_url'],
        help='URL for Ollama API'
    )
    
    parser.add_argument(
        '--with-llm',
        action='store_true',
        default=True,
        help='Enable LLM assessment (default: True)'
    )
    
    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Disable LLM assessment'
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information and exit'
    )
    
    parser.add_argument(
        '--env-file',
        type=str,
        help='Path to .env file with configuration (default: .env or ~/.env)'
    )
    
    return parser
