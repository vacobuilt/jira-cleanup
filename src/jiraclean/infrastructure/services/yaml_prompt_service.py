"""
YAML prompt service implementation.

This module contains an implementation of the prompt service interface
that loads and renders prompt templates from YAML files.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

from jiraclean.domain.services.interfaces.prompt_service import PromptService


logger = logging.getLogger('jiraclean.infrastructure.services.yaml_prompt_service')


class PromptNotFoundError(Exception):
    """Raised when a requested prompt template cannot be found."""
    pass


class PromptRenderError(Exception):
    """Raised when there's an error rendering a prompt template."""
    pass


class YamlPromptService(PromptService):
    """
    Implementation of the prompt service interface using YAML files.
    
    This service loads prompt templates from YAML files and manages them
    for rendering with variables.
    """
    
    def __init__(
        self,
        templates_dir: Optional[str] = None,
        auto_reload: bool = False
    ):
        """
        Initialize the YAML prompt service.
        
        Args:
            templates_dir: Directory containing prompt template YAML files
            auto_reload: Whether to reload templates for each request
        """
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._templates_dir = None
        
        if templates_dir:
            self.set_templates_dir(templates_dir)
        
        self.auto_reload = auto_reload
    
    def set_templates_dir(self, templates_dir: str) -> None:
        """
        Set the directory containing prompt template YAML files.
        
        Args:
            templates_dir: Path to the templates directory
            
        Raises:
            ValueError: If the directory doesn't exist
        """
        path = Path(templates_dir)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Templates directory does not exist: {templates_dir}")
        
        self._templates_dir = path
        self._load_templates()
    
    def get_prompt(self, prompt_name: str) -> str:
        """
        Get a raw prompt template by name.
        
        Args:
            prompt_name: The name of the prompt to retrieve
            
        Returns:
            The prompt template text
            
        Raises:
            PromptNotFoundError: If the prompt doesn't exist
        """
        if self.auto_reload:
            self._load_templates()
            
        template_data = self._get_template_data(prompt_name)
        return template_data.get('template', '')
    
    def render_prompt(self, prompt_name: str, variables: Dict[str, Any]) -> str:
        """
        Render a prompt template with variables.
        
        Args:
            prompt_name: The name of the prompt to render
            variables: Dictionary of variables to substitute in the template
            
        Returns:
            The rendered prompt text
            
        Raises:
            PromptNotFoundError: If the prompt doesn't exist
            PromptRenderError: If there's an error rendering the prompt
        """
        template = self.get_prompt(prompt_name)
        
        # Validate variables
        missing_vars = self.validate_variables(prompt_name, variables)
        if missing_vars:
            raise PromptRenderError(f"Missing required variables for prompt '{prompt_name}': {', '.join(missing_vars)}")
        
        # Perform simple template substitution
        try:
            rendered = template
            for var_name, var_value in variables.items():
                placeholder = f"{{{var_name}}}"
                rendered = rendered.replace(placeholder, str(var_value))
            
            # Check if any unreplaced variables remain
            unreplaced = []
            start_idx = 0
            while True:
                start_idx = rendered.find('{', start_idx)
                if start_idx == -1:
                    break
                    
                end_idx = rendered.find('}', start_idx)
                if end_idx == -1:
                    break
                    
                var_placeholder = rendered[start_idx:end_idx+1]
                # Check if this looks like a template variable
                if '{' in var_placeholder and '}' in var_placeholder and not '{{' in var_placeholder:
                    unreplaced.append(var_placeholder)
                
                start_idx = end_idx + 1
            
            if unreplaced:
                logger.warning(f"Found unreplaced variables in rendered prompt '{prompt_name}': {unreplaced}")
            
            return rendered
        except Exception as e:
            raise PromptRenderError(f"Error rendering prompt '{prompt_name}': {str(e)}")
    
    def list_prompts(self) -> List[str]:
        """
        List all available prompt names.
        
        Returns:
            List of prompt names
        """
        if self.auto_reload:
            self._load_templates()
            
        return list(self._templates.keys())
    
    def get_prompt_metadata(self, prompt_name: str) -> Dict[str, Any]:
        """
        Get metadata about a prompt.
        
        Args:
            prompt_name: The name of the prompt
            
        Returns:
            Dictionary of metadata
            
        Raises:
            PromptNotFoundError: If the prompt doesn't exist
        """
        template_data = self._get_template_data(prompt_name)
        
        # Extract metadata fields (everything except 'template')
        metadata = {k: v for k, v in template_data.items() if k != 'template'}
        return metadata
    
    def validate_variables(self, prompt_name: str, variables: Dict[str, Any]) -> List[str]:
        """
        Validate that all required variables for a prompt are provided.
        
        Args:
            prompt_name: The name of the prompt
            variables: Dictionary of provided variables
            
        Returns:
            List of missing variable names (empty if all variables are provided)
            
        Raises:
            PromptNotFoundError: If the prompt doesn't exist
        """
        template = self.get_prompt(prompt_name)
        
        # Find all variable placeholders in the template
        required_vars = set()
        start_idx = 0
        while True:
            start_idx = template.find('{', start_idx)
            if start_idx == -1:
                break
                
            end_idx = template.find('}', start_idx)
            if end_idx == -1:
                break
                
            var_name = template[start_idx+1:end_idx]
            if var_name and not '{' in var_name:  # Skip double braces
                required_vars.add(var_name)
            
            start_idx = end_idx + 1
        
        # Check which required variables are missing
        provided_vars = set(variables.keys())
        missing_vars = required_vars - provided_vars
        
        return sorted(list(missing_vars))
    
    def _load_templates(self) -> None:
        """
        Load all prompt templates from the templates directory.
        
        Raises:
            ValueError: If templates_dir is not set
        """
        if not self._templates_dir:
            raise ValueError("Templates directory not set. Call set_templates_dir() first.")
        
        self._templates.clear()
        
        # Find all YAML files in the templates directory
        yaml_files = list(self._templates_dir.glob('*.yaml')) + list(self._templates_dir.glob('*.yml'))
        
        if not yaml_files:
            logger.warning(f"No YAML template files found in {self._templates_dir}")
        
        # Load each template file
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    template_data = yaml.safe_load(f)
                
                # Validate template data
                if not isinstance(template_data, dict):
                    logger.warning(f"Invalid template data in {yaml_file}: not a dictionary")
                    continue
                
                if 'name' not in template_data:
                    # Use filename without extension as name
                    template_data['name'] = yaml_file.stem
                
                if 'template' not in template_data:
                    logger.warning(f"Missing 'template' field in {yaml_file}")
                    continue
                
                # Store the template
                template_name = template_data['name']
                self._templates[template_name] = template_data
                logger.debug(f"Loaded template '{template_name}' from {yaml_file}")
                
            except Exception as e:
                logger.error(f"Error loading template from {yaml_file}: {str(e)}")
    
    def _get_template_data(self, prompt_name: str) -> Dict[str, Any]:
        """
        Get template data for a prompt.
        
        Args:
            prompt_name: The name of the prompt
            
        Returns:
            The template data dictionary
            
        Raises:
            PromptNotFoundError: If the prompt doesn't exist
        """
        if prompt_name not in self._templates:
            raise PromptNotFoundError(f"Prompt template '{prompt_name}' not found")
        
        return self._templates[prompt_name]
