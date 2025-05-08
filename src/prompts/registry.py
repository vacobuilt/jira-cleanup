"""
Prompt registry implementation for Jira Cleanup.

This module provides classes for managing and rendering prompt templates
from YAML files, enabling centralized prompt management and variable substitution.
"""

import os
import re
import yaml
import json
import logging
from typing import Dict, Any, Set, Optional, List, Union
from dataclasses import dataclass
from pathlib import Path
from string import Template

logger = logging.getLogger('jira_cleanup.prompts')


@dataclass
class PromptTemplate:
    """
    A template for an LLM prompt with metadata.
    
    Attributes:
        name: Unique identifier for the prompt
        template: The template string with variable placeholders
        description: Human-readable description of the prompt
        required_vars: Set of variable names required by this prompt
        optional_vars: Set of variable names that are optional
        metadata: Additional metadata about the prompt
    """
    name: str
    template: str
    description: str = ""
    required_vars: Set[str] = None
    optional_vars: Set[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize after dataclass creation."""
        # Initialize empty collections if None
        if self.required_vars is None:
            self.required_vars = set()
        if self.optional_vars is None:
            self.optional_vars = set()
        if self.metadata is None:
            self.metadata = {}
            
        # Auto-detect variables if not provided
        if not self.required_vars and not self.optional_vars:
            self._detect_variables()
    
    def _detect_variables(self):
        """
        Detect variables in the template using regex.
        
        This scans the template for ${var} style variables and adds them
        to the required_vars set.
        """
        # Find all ${var} style variables
        var_pattern = r'\${([a-zA-Z0-9_]+)}'
        matches = re.findall(var_pattern, self.template)
        
        # Add to required variables
        for var in matches:
            self.required_vars.add(var)
    
    def render(self, values: Dict[str, Any]) -> str:
        """
        Render the template with the provided values.
        
        Args:
            values: Dictionary of values to substitute into the template
            
        Returns:
            The rendered template with variables replaced
            
        Raises:
            KeyError: If a required variable is missing
        """
        # Check for missing required variables
        missing_vars = self.required_vars - set(values.keys())
        if missing_vars:
            raise KeyError(f"Missing required variables for prompt '{self.name}': {missing_vars}")
        
        # Use string.Template for variable substitution
        template = Template(self.template)
        return template.safe_substitute(values)
    
    def get_missing_vars(self, values: Dict[str, Any]) -> Set[str]:
        """
        Get the set of missing required variables.
        
        Args:
            values: Dictionary of available values
            
        Returns:
            Set of variable names that are required but not provided
        """
        return self.required_vars - set(values.keys())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the template to a dictionary.
        
        Returns:
            Dictionary representation of the template
        """
        return {
            'name': self.name,
            'template': self.template,
            'description': self.description,
            'required_vars': list(self.required_vars),
            'optional_vars': list(self.optional_vars),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """
        Create a PromptTemplate from a dictionary.
        
        Args:
            data: Dictionary with template data
            
        Returns:
            New PromptTemplate instance
        """
        required_vars = set(data.get('required_vars', []))
        optional_vars = set(data.get('optional_vars', []))
        
        return cls(
            name=data['name'],
            template=data['template'],
            description=data.get('description', ''),
            required_vars=required_vars,
            optional_vars=optional_vars,
            metadata=data.get('metadata', {})
        )


class PromptRegistry:
    """
    Registry for managing and accessing prompt templates.
    
    This class provides dictionary-like access to prompt templates
    while adding functionality for loading templates from files
    and managing variable substitution.
    """
    
    def __init__(self):
        """Initialize an empty registry."""
        self._templates: Dict[str, PromptTemplate] = {}
        self._base_dir: Optional[Path] = None
    
    def __getitem__(self, key: str) -> PromptTemplate:
        """Get a prompt template by name."""
        if key not in self._templates:
            raise KeyError(f"Prompt template '{key}' not found in registry")
        return self._templates[key]
    
    def __setitem__(self, key: str, value: PromptTemplate):
        """Add or update a prompt template."""
        if not isinstance(value, PromptTemplate):
            raise TypeError("Value must be a PromptTemplate instance")
        self._templates[key] = value
    
    def __contains__(self, key: str) -> bool:
        """Check if a template exists in the registry."""
        return key in self._templates
    
    def __len__(self) -> int:
        """Get the number of templates in the registry."""
        return len(self._templates)
    
    def keys(self):
        """Get the names of all templates in the registry."""
        return self._templates.keys()
    
    def values(self):
        """Get all template objects in the registry."""
        return self._templates.values()
    
    def items(self):
        """Get all (name, template) pairs in the registry."""
        return self._templates.items()
    
    def get(self, key: str, default=None) -> Optional[PromptTemplate]:
        """Get a template by name with an optional default."""
        return self._templates.get(key, default)
    
    def set_base_dir(self, base_dir: Union[str, Path]):
        """Set the base directory for template loading."""
        self._base_dir = Path(base_dir) if base_dir else None
    
    def load_template(self, path: Union[str, Path]) -> PromptTemplate:
        """
        Load a single template from a YAML or JSON file.
        
        Args:
            path: Path to the template file
            
        Returns:
            The loaded PromptTemplate
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file has an invalid format
        """
        path = Path(path)
        
        # Resolve path if base directory is set
        if self._base_dir and not path.is_absolute():
            path = self._base_dir / path
        
        # Check if file exists
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {path}")
        
        # Load based on file extension
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix.lower() in ('.yaml', '.yml'):
                data = yaml.safe_load(f)
            elif path.suffix.lower() == '.json':
                data = json.load(f)
            else:
                # For .txt or other formats, treat as raw template
                template_text = f.read()
                # Use filename (without extension) as template name
                name = path.stem
                data = {
                    'name': name,
                    'template': template_text,
                    'description': f"Template loaded from {path.name}"
                }
        
        # Create template
        template = PromptTemplate.from_dict(data)
        
        # Add to registry
        self._templates[template.name] = template
        logger.debug(f"Loaded template '{template.name}' from {path}")
        
        return template
    
    def load_directory(self, directory: Union[str, Path], recursive: bool = True) -> int:
        """
        Load all templates from a directory.
        
        Args:
            directory: Directory containing template files
            recursive: Whether to search subdirectories
            
        Returns:
            Number of templates loaded
        """
        directory = Path(directory)
        
        # Resolve path if base directory is set
        if self._base_dir and not directory.is_absolute():
            directory = self._base_dir / directory
        
        # Check if directory exists
        if not directory.exists() or not directory.is_dir():
            raise FileNotFoundError(f"Template directory not found: {directory}")
        
        # Find template files
        template_files = []
        extensions = ('.yaml', '.yml', '.json', '.txt')
        
        if recursive:
            for ext in extensions:
                template_files.extend(directory.glob(f"**/*{ext}"))
        else:
            for ext in extensions:
                template_files.extend(directory.glob(f"*{ext}"))
        
        # Load each template
        count = 0
        for path in template_files:
            try:
                self.load_template(path)
                count += 1
            except Exception as e:
                logger.error(f"Failed to load template from {path}: {str(e)}")
        
        return count
    
    def render(self, template_name: str, values: Dict[str, Any]) -> str:
        """
        Render a template with the given values.
        
        Args:
            template_name: Name of the template to render
            values: Dictionary of values to substitute
            
        Returns:
            The rendered template
            
        Raises:
            KeyError: If the template doesn't exist or required variables are missing
        """
        template = self[template_name]
        return template.render(values)
    
    def get_required_vars(self, template_name: str) -> Set[str]:
        """
        Get the set of required variables for a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Set of required variable names
            
        Raises:
            KeyError: If the template doesn't exist
        """
        template = self[template_name]
        return template.required_vars
    
    def get_optional_vars(self, template_name: str) -> Set[str]:
        """
        Get the set of optional variables for a template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Set of optional variable names
            
        Raises:
            KeyError: If the template doesn't exist
        """
        template = self[template_name]
        return template.optional_vars
    
    def get_missing_vars(self, template_name: str, values: Dict[str, Any]) -> Set[str]:
        """
        Get the set of missing required variables for a template.
        
        Args:
            template_name: Name of the template
            values: Dictionary of available values
            
        Returns:
            Set of missing required variable names
            
        Raises:
            KeyError: If the template doesn't exist
        """
        template = self[template_name]
        return template.get_missing_vars(values)
    
    def save_template(self, template_name: str, path: Union[str, Path], format: str = 'yaml'):
        """
        Save a template to a file.
        
        Args:
            template_name: Name of the template to save
            path: Path to save the template to
            format: Format to save in ('yaml', 'json')
            
        Raises:
            KeyError: If the template doesn't exist
            ValueError: If the format is invalid
        """
        template = self[template_name]
        path = Path(path)
        
        # Resolve path if base directory is set
        if self._base_dir and not path.is_absolute():
            path = self._base_dir / path
        
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save in specified format
        with open(path, 'w', encoding='utf-8') as f:
            if format.lower() == 'yaml':
                yaml.dump(template.to_dict(), f, default_flow_style=False, width=80)
            elif format.lower() == 'json':
                json.dump(template.to_dict(), f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
        
        logger.debug(f"Saved template '{template_name}' to {path}")
