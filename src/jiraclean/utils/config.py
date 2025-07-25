"""
Configuration utilities for Jira Cleanup.

This module provides functions for loading and validating
configuration from YAML files, environment variables and .env files.
Supports multiple Jira instances with instance selection.
"""

import os
import logging
import argparse
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Initialize logger early
logger = logging.getLogger('jiraclean.utils.config')

# Package is python-dotenv but imported as dotenv
try:
    from dotenv import load_dotenv
except ImportError:
    # If not installed, create a dummy function
    def load_dotenv(*args, **kwargs) -> bool:
        """Dummy implementation when dotenv is not available."""
        logger.warning("python-dotenv package not found. .env file loading is disabled.")
        return False


def load_yaml_config(config_file: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Load configuration from YAML file.
    
    Searches for config files in this order:
    1. Specified config_file path
    2. ./config.yaml (current directory)
    3. ~/.jiraclean/config.yaml (user home)
    
    Args:
        config_file: Optional path to specific config file
        
    Returns:
        Dictionary with configuration or None if no config found
    """
    config_paths = []
    
    # Add specific config file if provided
    if config_file:
        config_paths.append(Path(config_file))
    
    # Add default search paths
    config_paths.extend([
        Path('./config.yaml'),  # Current directory
        Path.home() / '.jiraclean' / 'config.yaml',  # User home
    ])
    
    # Try to load from config files
    for config_path in config_paths:
        if config_path.exists():
            try:
                logger.info(f"Loading YAML configuration from {config_path}")
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                return config
            except Exception as e:
                logger.error(f"Error loading config from {config_path}: {e}")
                continue
    
    logger.info("No YAML configuration file found, falling back to environment variables")
    return None


def load_environment_config(env_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from .env file and environment variables.
    
    This is the fallback method when no YAML config is found.
    
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
    
    # Load configuration in legacy format
    config = {
        'default_instance': 'default',
        'instances': {
            'default': {
                'name': 'Default Instance',
                'url': os.getenv('JIRA_URL', ''),
                'username': os.getenv('JIRA_USER', ''),
                'token': os.getenv('JIRA_TOKEN', ''),
                'auth_method': os.getenv('JIRA_AUTH_METHOD', 'token'),
                'description': 'Legacy environment variable configuration'
            }
        },
        'settings': {
            'logging': {
                'level': os.getenv('JIRA_CLEANUP_LOG_LEVEL', 'INFO'),
            },
            'defaults': {
                'dry_run': os.getenv('JIRA_CLEANUP_DRY_RUN', 'true').lower() == 'true',
                'force_dry_run': os.getenv('FORCE_DRY_RUN', 'false').lower() == 'true',
                'project': os.getenv('JIRA_CLEANUP_PROJECT', ''),
                'max_tickets': 50
            },
            'llm': {
                'ollama_url': os.getenv('OLLAMA_URL', 'http://localhost:11434'),
                'model': os.getenv('LLM_MODEL', 'llama3.2:latest'),
                'enabled': True
            }
        }
    }
    
    return config


def load_configuration(config_file: Optional[str] = None, env_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file or fallback to environment variables.
    
    Args:
        config_file: Optional path to YAML config file
        env_file: Optional path to .env file (fallback only)
        
    Returns:
        Dictionary with complete configuration
    """
    # Try YAML configuration first
    config = load_yaml_config(config_file)
    
    # Fallback to environment variables if no YAML config
    if config is None:
        config = load_environment_config(env_file)
    
    return config


def get_instance_config(config: Dict[str, Any], instance_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get configuration for a specific Jira instance.
    
    Args:
        config: Full configuration dictionary
        instance_name: Name of instance to get, or None for default
        
    Returns:
        Instance configuration dictionary
        
    Raises:
        KeyError: If specified instance doesn't exist
    """
    if instance_name is None:
        instance_name = config.get('default_instance', 'default')
    
    instances = config.get('instances', {})
    if instance_name not in instances:
        available = list(instances.keys())
        raise KeyError(f"Instance '{instance_name}' not found. Available instances: {available}")
    
    return instances[instance_name]


def list_instances(config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    List all available Jira instances.
    
    Args:
        config: Full configuration dictionary
        
    Returns:
        Dictionary of instance name -> instance info
    """
    instances = config.get('instances', {})
    default_instance = config.get('default_instance')
    
    result = {}
    for name, instance_config in instances.items():
        result[name] = {
            'name': instance_config.get('name', name),
            'url': instance_config.get('url', ''),
            'username': instance_config.get('username', ''),
            'description': instance_config.get('description', ''),
            'is_default': name == default_instance
        }
    
    return result


def validate_config(config: Dict[str, Any], args: argparse.Namespace) -> bool:
    """
    Validate the combined configuration from YAML/environment and CLI args.
    
    Args:
        config: Configuration dictionary
        args: Parsed command-line arguments
        
    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        # Get the instance configuration
        instance_config = get_instance_config(config, getattr(args, 'instance', None))
        
        # Check required Jira settings for the selected instance
        if not instance_config.get('url'):
            logger.error(f"URL is required for instance '{getattr(args, 'instance', 'default')}'")
            return False
        
        if not instance_config.get('username'):
            logger.error(f"Username is required for instance '{getattr(args, 'instance', 'default')}'")
            return False
        
        if not instance_config.get('token') and instance_config.get('auth_method') == 'token':
            logger.error(f"Token is required for token auth method in instance '{getattr(args, 'instance', 'default')}'")
            return False
        
        # Check if project is specified
        if not args.project:
            logger.error("Project key is required (use --project)")
            return False
        
        # Check if FORCE_DRY_RUN requires dry run mode
        settings = config.get('settings', {})
        defaults = settings.get('defaults', {})
        if defaults.get('force_dry_run') and not args.dry_run:
            logger.error("force_dry_run is set to true in configuration, but --dry-run flag is not provided")
            logger.error("For safety, the program will not run in live mode when force_dry_run is enabled")
            return False
        
        return True
        
    except KeyError as e:
        logger.error(str(e))
        return False


def setup_argument_parser(config: Dict[str, Any]) -> argparse.ArgumentParser:
    """
    Set up the command-line argument parser with consistent defaults.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='Jira Cleanup - A configurable tool for Jira ticket governance',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Get settings
    settings = config.get('settings', {})
    defaults = settings.get('defaults', {})
    llm_settings = settings.get('llm', {})
    logging_settings = settings.get('logging', {})
    
    # Instance selection
    instances = config.get('instances', {})
    default_instance = config.get('default_instance')
    
    parser.add_argument(
        '--instance',
        type=str,
        choices=list(instances.keys()),
        default=default_instance,
        help=f'Jira instance to use (default: {default_instance})'
    )
    
    parser.add_argument(
        '--project',
        type=str,
        default=defaults.get('project', ''),
        help='Jira project key to process'
    )
    
    # Set dry-run default based on configuration
    dry_run_default = defaults.get('dry_run', True) or defaults.get('force_dry_run', False)
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=dry_run_default,
        help='Run without making changes to Jira'
    )
    
    parser.add_argument(
        '--max-tickets',
        type=int,
        default=defaults.get('max_tickets', 50),
        help='Maximum number of tickets to process'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default=logging_settings.get('level', 'INFO'),
        help='Set logging level'
    )
    
    parser.add_argument(
        '--llm-model',
        type=str,
        default=llm_settings.get('model', 'llama3.2:latest'),
        help='LLM model to use for assessment'
    )
    
    parser.add_argument(
        '--ollama-url',
        type=str,
        default=llm_settings.get('ollama_url', 'http://localhost:11434'),
        help='URL for Ollama API'
    )
    
    parser.add_argument(
        '--with-llm',
        action='store_true',
        default=llm_settings.get('enabled', True),
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
        '--config-file',
        type=str,
        help='Path to YAML configuration file'
    )
    
    parser.add_argument(
        '--env-file',
        type=str,
        help='Path to .env file (fallback when no YAML config)'
    )
    
    return parser
