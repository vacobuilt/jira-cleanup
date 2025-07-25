"""
Ticket Analysis Business Logic.

This module contains pure business logic for analyzing tickets,
separated from LLM communication concerns. It uses dependency injection
to receive an LLM service for communication.
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from jiraclean.prompts import PromptRegistry
from jiraclean.utils.formatters import format_ticket_as_yaml
from jiraclean.llm.langchain_service import LangChainLLMService, LangChainServiceError
from jiraclean.entities import AssessmentResult
from jiraclean.analysis.base import BaseTicketAnalyzer

logger = logging.getLogger('jiraclean.analysis')

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


class AnalysisError(Exception):
    """Exception raised during ticket analysis operations."""
    pass


class QuiescentAnalyzer(BaseTicketAnalyzer):
    """
    Analyzer for detecting quiescent (stalled/inactive) tickets.
    
    This analyzer specializes in identifying tickets that have become inactive
    or stalled, requiring intervention to move them forward.
    """
    
    def get_analyzer_type(self) -> str:
        """Get the type identifier for this analyzer."""
        return "quiescent"
    
    def get_default_template(self) -> str:
        """Get the default prompt template name for this analyzer."""
        return "quiescent_assessment"
    
    def analyze(self, ticket_data: Dict[str, Any], template: Optional[str] = None, **kwargs) -> AssessmentResult:
        """
        Analyze a ticket for quiescence.
        
        Args:
            ticket_data: Dictionary with ticket information
            template: Optional template name override
            **kwargs: Additional parameters
            
        Returns:
            AssessmentResult with quiescence assessment
        """
        if template is None:
            template = self.get_default_template()
        
        return self.assess_quiescence(ticket_data, template)
    
    def assess_quiescence(self, 
                         ticket_data: Dict[str, Any], 
                         template: str = "quiescent_assessment") -> AssessmentResult:
        """
        Assess a ticket for quiescence using the configured LLM.
        
        Args:
            ticket_data: Dictionary with ticket information
            template: Name of the prompt template to use
            
        Returns:
            AssessmentResult with LLM assessment
            
        Raises:
            AnalysisError: If analysis fails
            KeyError: If the specified template doesn't exist
        """
        # Extract ticket key for better logging
        ticket_key = ticket_data.get('key', 'UNKNOWN')
        
        try:
            # Build the assessment prompt
            ticket_yaml = format_ticket_as_yaml(ticket_data)
            prompt = self._build_assessment_prompt(ticket_yaml, template)
            
            # First attempt with normal instructions
            logger.info(f"ATTEMPT #1: Making assessment for ticket {ticket_key}")
            
            try:
                response = self._generate_response_with_system_message(prompt, enhanced_json=False)
                result = self._parse_llm_response(response)
                logger.info(f"ATTEMPT #1: Successfully assessed ticket {ticket_key}")
                return result
                
            except ValueError as e:
                if "Invalid JSON response" in str(e):
                    logger.warning(f"ATTEMPT #1 FAILED: Ticket {ticket_key} - JSON parsing error: {str(e)}")
                    
                    # Second attempt with enhanced JSON formatting instructions
                    try:
                        logger.info(f"RETRY ATTEMPT #2: Ticket {ticket_key} - Using enhanced JSON instructions")
                        response = self._generate_response_with_system_message(prompt, enhanced_json=True)
                        result = self._parse_llm_response(response)
                        logger.info(f"RETRY ATTEMPT #2: Successfully assessed ticket {ticket_key} after retry")
                        return result
                    except Exception as retry_error:
                        logger.error(f"RETRY ATTEMPT #2 FAILED: Ticket {ticket_key} - Error: {str(retry_error)}")
                        return AssessmentResult.default()
                else:
                    # Not a JSON parsing error, so don't retry
                    logger.error(f"Error during ticket assessment for {ticket_key}: {str(e)}")
                    return AssessmentResult.default()
                    
        except Exception as e:
            logger.error(f"Error during ticket assessment for {ticket_key}: {str(e)}")
            if isinstance(e, KeyError):
                # Re-raise template not found errors
                raise
            return AssessmentResult.default()
    
    def _build_assessment_prompt(self, ticket_yaml: str, template_name: str) -> str:
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
    
    def _generate_response_with_system_message(self, prompt: str, enhanced_json: bool = False) -> str:
        """
        Generate response from LLM with appropriate system message.
        
        Args:
            prompt: The prompt to send to the LLM
            enhanced_json: Whether to use enhanced JSON formatting instructions
            
        Returns:
            The response text from the LLM
            
        Raises:
            AnalysisError: If the LLM call fails
        """
        # Build system message
        base_system_msg = ("You are an expert Jira ticket analyst. Provide JSON output only. "
                          "For all JSON string values, especially in the planned_comment field, "
                          "format all text as a single line with no line breaks. If you need to "
                          "represent a line break in the planned_comment field, use the \\n escape "
                          "sequence. All special characters in JSON strings must be properly escaped "
                          "according to JSON formatting rules.")
        
        # Add enhanced JSON formatting instructions if requested
        if enhanced_json:
            system_msg = (base_system_msg + " IMPORTANT: Your previous response contained invalid JSON. "
                         "Please ensure all JSON objects are complete with proper closing braces and "
                         "that all property names are enclosed in double quotes. Do not include any "
                         "text outside the JSON object. Make sure the output is a complete, valid JSON object.")
        else:
            system_msg = base_system_msg
        
        # Combine system message with prompt
        full_prompt = f"System: {system_msg}\n\nUser: {prompt}"
        
        try:
            return self.llm_service.generate_response(full_prompt)
        except LangChainServiceError as e:
            raise AnalysisError(f"Failed to generate LLM response: {e}") from e
    
    def _parse_llm_response(self, response: str) -> AssessmentResult:
        """
        Parse the LLM response into an AssessmentResult.
        
        Args:
            response: The raw response from the LLM
            
        Returns:
            AssessmentResult instance
            
        Raises:
            ValueError: If the response cannot be parsed
        """
        # Only show raw response when debug logging is enabled
        if logger.isEnabledFor(logging.DEBUG):
            print("\n===== RAW LLM RESPONSE =====")
            print(response)
            print("===== END RAW RESPONSE =====\n")
        
        # Always log at debug level for record keeping
        logger.debug("\n===== RAW LLM RESPONSE =====\n" + response + "\n===== END RAW RESPONSE =====\n")
        
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
            # First attempt normal parsing
            try:
                result_dict = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                # If that fails, try to sanitize the response for common JSON formatting issues
                logger.warning(f"Initial JSON parsing failed: {str(e)}, attempting to sanitize response")
                
                # Fix common issues with line breaks and control characters in JSON values
                # This regex looks for string values that contain literal newlines
                sanitized = re.sub(r'"\s*:\s*"(.*?)(?<!\\)(?:\\\\)*\n(.*?)"', 
                                  lambda m: f'": "{m.group(1)}\\n{m.group(2)}"', 
                                  cleaned_response, flags=re.DOTALL)
                
                # Remove any control characters that aren't valid in JSON strings
                sanitized = re.sub(r'[\x00-\x1F\x7F]', '', sanitized)
                
                # Try parsing again with the sanitized response
                result_dict = json.loads(sanitized)
                logger.info("Successfully parsed JSON after sanitization")
                
            return AssessmentResult.from_dict(result_dict)
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
