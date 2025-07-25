"""
Ticket Quality Analysis.

This module provides analysis for ticket quality, including completeness,
clarity, and adherence to standards.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from jiraclean.entities.quality_result import QualityResult
from jiraclean.utils.formatters import format_ticket_as_yaml
from jiraclean.llm.langchain_service import LangChainServiceError
from jiraclean.analysis.base import BaseTicketAnalyzer
from jiraclean.analysis.ticket_analyzer import get_prompt_registry, AnalysisError

logger = logging.getLogger('jiraclean.analysis.quality')


class TicketQualityAnalyzer(BaseTicketAnalyzer):
    """
    Analyzer for assessing ticket quality and completeness.
    
    This analyzer evaluates tickets for quality factors such as:
    - Completeness of description and acceptance criteria
    - Clarity of requirements and scope
    - Proper labeling and categorization
    - Adherence to team standards
    """
    
    def get_analyzer_type(self) -> str:
        """Get the type identifier for this analyzer."""
        return "ticket_quality"
    
    def get_default_template(self) -> str:
        """Get the default prompt template name for this analyzer."""
        return "ticket_quality_assessment"
    
    def analyze(self, ticket_data: Dict[str, Any], template: Optional[str] = None, **kwargs) -> QualityResult:
        """
        Analyze a ticket for quality and completeness.
        
        Args:
            ticket_data: Dictionary with ticket information
            template: Optional template name override
            **kwargs: Additional parameters
            
        Returns:
            QualityResult with quality assessment
        """
        if template is None:
            template = self.get_default_template()
        
        return self.assess_quality(ticket_data, template)
    
    def assess_quality(self, 
                      ticket_data: Dict[str, Any], 
                      template: str = "ticket_quality_assessment") -> QualityResult:
        """
        Assess a ticket for quality using the configured LLM.
        
        Args:
            ticket_data: Dictionary with ticket information
            template: Name of the prompt template to use
            
        Returns:
            QualityResult with quality assessment
            
        Raises:
            AnalysisError: If analysis fails
            KeyError: If the specified template doesn't exist
        """
        # Extract ticket key for better logging
        ticket_key = ticket_data.get('key', 'UNKNOWN')
        
        try:
            # Validate ticket data
            if not self.validate_ticket_data(ticket_data):
                logger.error(f"Invalid ticket data for {ticket_key}")
                return QualityResult.default()
            
            # Build the assessment prompt
            ticket_yaml = format_ticket_as_yaml(ticket_data)
            prompt = self._build_quality_prompt(ticket_yaml, template)
            
            # Generate response
            logger.info(f"Assessing ticket quality for {ticket_key}")
            
            try:
                response = self._generate_response_with_system_message(prompt)
                result = self._parse_quality_response(response)
                logger.info(f"Successfully assessed ticket quality for {ticket_key}")
                return result
                
            except ValueError as e:
                logger.error(f"Quality assessment failed for {ticket_key}: {str(e)}")
                return QualityResult.default()
                    
        except Exception as e:
            logger.error(f"Error during quality assessment for {ticket_key}: {str(e)}")
            if isinstance(e, KeyError):
                # Re-raise template not found errors
                raise
            return QualityResult.default()
    
    def _build_quality_prompt(self, ticket_yaml: str, template_name: str) -> str:
        """
        Build a prompt for the LLM to assess ticket quality.
        
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
    
    def _generate_response_with_system_message(self, prompt: str) -> str:
        """
        Generate response from LLM with quality assessment system message.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The response text from the LLM
            
        Raises:
            AnalysisError: If the LLM call fails
        """
        # Build system message for quality assessment
        system_msg = ("You are an expert Jira ticket quality analyst. Provide JSON output only. "
                     "Assess tickets for completeness, clarity, and adherence to best practices. "
                     "For all JSON string values, format text as single lines with \\n for line breaks. "
                     "All special characters in JSON strings must be properly escaped.")
        
        # Combine system message with prompt
        full_prompt = f"System: {system_msg}\n\nUser: {prompt}"
        
        try:
            return self.llm_service.generate_response(full_prompt)
        except LangChainServiceError as e:
            raise AnalysisError(f"Failed to generate LLM response: {e}") from e
    
    def _parse_quality_response(self, response: str) -> QualityResult:
        """
        Parse the LLM response into a QualityResult for quality assessment.
        
        Args:
            response: The raw response from the LLM
            
        Returns:
            QualityResult instance
            
        Raises:
            ValueError: If the response cannot be parsed
        """
        # Log response for debugging
        logger.debug(f"Quality assessment response: {response}")
        
        if not response:
            raise ValueError("Empty response from LLM")
            
        # Clean the response - some LLMs add markdown code blocks
        cleaned_response = response
        if "```json" in response:
            start_idx = response.find("```json") + 7
            end_idx = response.find("```", start_idx)
            if end_idx == -1:
                raise ValueError("Malformed JSON response: unclosed code block")
            cleaned_response = response[start_idx:end_idx].strip()
        elif "```" in response:
            start_idx = response.find("```") + 3
            end_idx = response.find("```", start_idx)
            if end_idx == -1:
                raise ValueError("Malformed JSON response: unclosed code block")
            cleaned_response = response[start_idx:end_idx].strip()
            
        # Parse the JSON
        try:
            result_dict = json.loads(cleaned_response)
            
            # Map quality assessment fields to AssessmentResult
            # For quality assessment, we interpret the results differently:
            # - is_quiescent becomes "needs_improvement" (quality issues found)
            # - justification explains quality assessment
            # - suggested_action provides improvement recommendations
            
            quality_result = {
                'is_quiescent': result_dict.get('needs_improvement', False),
                'justification': result_dict.get('quality_assessment', 'No quality assessment provided'),
                'responsible_party': result_dict.get('responsible_party', 'Ticket Author'),
                'suggested_action': result_dict.get('improvement_suggestions', 'No improvements suggested'),
                'suggested_deadline': result_dict.get('suggested_deadline', 'Next sprint planning'),
                'planned_comment': result_dict.get('planned_comment', 'Quality assessment completed')
            }
            
            return QualityResult.from_dict(quality_result)
            
        except Exception as e:
            logger.error(f"Error parsing quality assessment response: {str(e)}")
            logger.error(f"Raw response: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {str(e)}")
