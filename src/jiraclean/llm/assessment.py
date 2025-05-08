"""
LLM-based ticket assessment functionality.

This module implements ticket assessment using Ollama or other LLM services,
analyzing tickets for quiescence and recommending actions.
"""

import json
import logging
import requests
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from jiraclean.prompts import PromptRegistry
from jiraclean.utils.formatters import format_ticket_as_yaml

logger = logging.getLogger('jira_cleanup.llm')

# Global prompt registry instance
_prompt_registry = None


def get_prompt_registry() -> PromptRegistry:
    """
    Get or initialize the prompt registry.
    
    Returns:
        Configured PromptRegistry instance
        
    Raises:
        FileNotFoundError: If templates directory doesn't exist
        RuntimeError: If templates couldn't be loaded
    """
    global _prompt_registry
    
    if _prompt_registry is None:
        _prompt_registry = PromptRegistry()
        
        # Set base directory to the templates directory in the package
        module_dir = Path(__file__).parent.parent
        templates_dir = module_dir / 'prompts' / 'templates'
        _prompt_registry.set_base_dir(templates_dir)
        
        # Load templates - fail if can't load
        if not templates_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {templates_dir}")
            
        count = _prompt_registry.load_directory(templates_dir)
        if count == 0:
            raise RuntimeError(f"No templates found in {templates_dir}")
            
        logger.info(f"Loaded {count} prompt templates from {templates_dir}")
    
    return _prompt_registry


@dataclass
class AssessmentResult:
    """Structure to hold LLM assessment results for a ticket."""
    
    is_quiescent: bool
    justification: str
    responsible_party: str
    suggested_action: str
    suggested_deadline: str
    planned_comment: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssessmentResult':
        """
        Create an AssessmentResult from a dictionary.
        
        Args:
            data: Dictionary with assessment data
            
        Returns:
            AssessmentResult instance
        """
        return cls(
            is_quiescent=data.get('is_quiescent', False),
            justification=data.get('justification', 'No justification provided'),
            responsible_party=data.get('responsible_party', 'Unknown'),
            suggested_action=data.get('suggested_action', 'No action suggested'),
            suggested_deadline=data.get('suggested_deadline', 'No deadline suggested'),
            planned_comment=data.get('planned_comment', 'No comment generated')
        )
    
    @classmethod
    def default(cls) -> 'AssessmentResult':
        """
        Create a default (failed) assessment result.
        
        Returns:
            AssessmentResult instance with default values
        """
        return cls(
            is_quiescent=False,
            justification="Failed to assess ticket",
            responsible_party="Unknown",
            suggested_action="None",
            suggested_deadline="None",
            planned_comment="Failed to generate comment"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert assessment to dictionary.
        
        Returns:
            Dictionary representation of the assessment
        """
        return {
            'is_quiescent': self.is_quiescent,
            'justification': self.justification,
            'responsible_party': self.responsible_party,
            'suggested_action': self.suggested_action,
            'suggested_deadline': self.suggested_deadline,
            'planned_comment': self.planned_comment
        }


def assess_ticket(
    ticket_data: Dict[str, Any], 
    model: str = "llama3.2:latest",
    ollama_url: str = "http://localhost:11434",
    prompt_template: str = "quiescent_assessment"
) -> AssessmentResult:
    """
    Assess a ticket for quiescence using an LLM.
    
    Args:
        ticket_data: Dictionary with ticket information
        model: LLM model to use (default: llama3.2:latest)
        ollama_url: Base URL for Ollama API (default: http://localhost:11434)
        prompt_template: Name of the prompt template to use
        
    Returns:
        AssessmentResult with LLM assessment
        
    Raises:
        KeyError: If the specified template doesn't exist
    """
    try:
        ticket_yaml = format_ticket_as_yaml(ticket_data)
        prompt = build_assessment_prompt(ticket_yaml, prompt_template)
        response = call_ollama_api(prompt, model, ollama_url)
        return parse_llm_response(response)
    except Exception as e:
        logger.error(f"Error during ticket assessment: {str(e)}")
        if isinstance(e, KeyError):
            # Re-raise template not found errors
            raise
        return AssessmentResult.default()


def build_assessment_prompt(ticket_yaml: str, template_name: str = "quiescent_assessment") -> str:
    """
    Build a prompt for the LLM to assess ticket quiescence.
    
    Args:
        ticket_yaml: YAML-formatted ticket information
        template_name: Name of the prompt template to use
        
    Returns:
        Formatted prompt text
        
    Raises:
        KeyError: If the specified template doesn't exist
    """
    # Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Get prompt registry and template
    registry = get_prompt_registry()
    
    # Check if template exists
    if template_name not in registry:
        template_dir = registry._base_dir
        raise KeyError(f"Template '{template_name}' not found in {template_dir}")
    
    # Prepare variables for the template
    variables = {
        'current_date': current_date,
        'ticket_yaml': ticket_yaml
    }
    
    # Render the template
    return registry.render(template_name, variables)


def call_ollama_api(
    prompt: str, 
    model: str = "llama3.2:latest",
    base_url: str = "http://localhost:11434"
) -> str:
    """
    Call the Ollama API with the given prompt and model.
    
    Args:
        prompt: The prompt to send to Ollama
        model: The model name to use
        base_url: Base URL for Ollama API
        
    Returns:
        The response text from Ollama
        
    Raises:
        RuntimeError: If the API call fails
    """
    url = f"{base_url}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "system": "You are an expert Jira ticket analyst. Provide JSON output only."
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code != 200:
            raise RuntimeError(f"Ollama API error ({response.status_code}): {response.text}")
            
        return response.json().get("response", "")
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to connect to Ollama API: {str(e)}")


def parse_llm_response(response: str) -> AssessmentResult:
    """
    Parse the LLM response into an AssessmentResult.
    
    Args:
        response: The raw response from the LLM
        
    Returns:
        AssessmentResult instance
        
    Raises:
        ValueError: If the response cannot be parsed
    """
    if not response:
        raise ValueError("Empty response from LLM")
        
    # Clean the response - some LLMs add markdown code blocks
    cleaned_response = response
    if "```json" in response:
        # Extract content between ```json and ```
        start_idx = response.find("```json") + 7
        end_idx = response.find("```", start_idx)
        if end_idx == -1:
            raise ValueError("Malformed JSON response: unclosed code block")
        cleaned_response = response[start_idx:end_idx].strip()
    elif "```" in response:
        # Extract content between ``` and ```
        start_idx = response.find("```") + 3
        end_idx = response.find("```", start_idx)
        if end_idx == -1:
            raise ValueError("Malformed JSON response: unclosed code block")
        cleaned_response = response[start_idx:end_idx].strip()
        
    # Parse the JSON
    try:
        result_dict = json.loads(cleaned_response)
        return AssessmentResult.from_dict(result_dict)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing LLM response: {str(e)}")
        logger.error(f"Raw response: {response}")
        raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
