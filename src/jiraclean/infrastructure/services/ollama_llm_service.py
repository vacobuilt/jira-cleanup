"""
Ollama LLM service implementation.

This module contains an implementation of the LLM service interface
that uses the Ollama API to interact with local LLM models.
"""

import json
import requests
import logging
import yaml
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union

from jiraclean.domain.entities.ticket import Ticket
from jiraclean.domain.entities.assessment import Assessment
from jiraclean.domain.services.interfaces.llm_service import LlmService
from jiraclean.domain.services.interfaces.prompt_service import PromptService


logger = logging.getLogger('jiraclean.infrastructure.services.ollama_llm_service')


class LlmServiceError(Exception):
    """Base exception for LLM service errors."""
    pass


class OllamaConnectionError(LlmServiceError):
    """Raised when a connection to Ollama cannot be established."""
    pass


class InvalidResponseError(LlmServiceError):
    """Raised when an invalid response is received from the LLM."""
    pass


class OllamaLlmService(LlmService):
    """
    Implementation of the LLM service interface using Ollama.
    
    This service interacts with locally running Ollama to provide
    LLM capabilities for ticket assessment and comment generation.
    """
    
    def __init__(
        self,
        prompt_service: PromptService,
        ollama_url: str = "http://localhost:11434",
        model: str = "llama3.2:latest",
        timeout: int = 60
    ):
        """
        Initialize the Ollama LLM service.
        
        Args:
            prompt_service: Service for managing and rendering prompts
            ollama_url: Base URL for the Ollama API
            model: Default model to use for assessments
            timeout: Request timeout in seconds
        """
        self.prompt_service = prompt_service
        self.ollama_url = ollama_url.rstrip('/')
        self.model = model
        self.timeout = timeout
    
    def assess_ticket(self, ticket: Ticket) -> Assessment:
        """
        Assess a ticket for quiescence using the Ollama LLM.
        
        Args:
            ticket: The ticket to assess
            
        Returns:
            Assessment result containing the LLM's evaluation
            
        Raises:
            LlmServiceError: If there's an error communicating with the LLM
            InvalidResponseError: If the LLM's response can't be parsed
        """
        # Convert ticket to YAML format for the prompt
        ticket_yaml = self._format_ticket_as_yaml(ticket)
        
        # Get current date for the prompt
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Render the assessment prompt
        try:
            prompt = self.prompt_service.render_prompt(
                'quiescent_assessment',
                {
                    'current_date': current_date,
                    'ticket_yaml': ticket_yaml
                }
            )
        except Exception as e:
            logger.error(f"Error rendering prompt: {str(e)}")
            raise LlmServiceError(f"Failed to render assessment prompt: {str(e)}")
        
        # Call the Ollama API
        try:
            response_text = self._call_ollama_api(prompt)
        except Exception as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            raise LlmServiceError(f"Failed to communicate with Ollama: {str(e)}")
        
        # Parse the response
        try:
            assessment_data = self._parse_assessment_response(response_text)
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            raise InvalidResponseError(f"Failed to parse LLM response: {str(e)}")
        
        # Create the assessment object
        return Assessment.from_dict(assessment_data)
    
    def generate_comment(
        self,
        ticket: Ticket,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a comment for a ticket using the LLM.
        
        This is a direct implementation that uses the ticket and optional context
        to generate a comment without an assessment. For comments based on
        assessment results, use the CommentGenerator domain service.
        
        Args:
            ticket: The ticket to generate a comment for
            context: Optional additional context for comment generation
            
        Returns:
            Generated comment text
            
        Raises:
            LlmServiceError: If there's an error communicating with the LLM
        """
        # If context doesn't exist, initialize it
        if context is None:
            context = {}
        
        # Convert ticket to YAML format for the prompt
        ticket_yaml = self._format_ticket_as_yaml(ticket)
        
        # Get current date for the prompt
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Render the comment generation prompt
        try:
            prompt = self.prompt_service.render_prompt(
                'comment_generation',
                {
                    'current_date': current_date,
                    'ticket_yaml': ticket_yaml,
                    'context': json.dumps(context)
                }
            )
        except Exception as e:
            logger.error(f"Error rendering prompt: {str(e)}")
            raise LlmServiceError(f"Failed to render comment prompt: {str(e)}")
        
        # Call the Ollama API
        try:
            response_text = self._call_ollama_api(prompt)
        except Exception as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            raise LlmServiceError(f"Failed to communicate with Ollama: {str(e)}")
        
        # Clean and return the response
        return self._clean_text_response(response_text)
    
    def answer_question(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Ask a question to the LLM and get a response.
        
        Args:
            question: The question to ask
            context: Optional additional context for the question
            
        Returns:
            The LLM's answer to the question
            
        Raises:
            LlmServiceError: If there's an error communicating with the LLM
        """
        # If context doesn't exist, initialize it
        if context is None:
            context = {}
        
        # Create a simple prompt for the question
        prompt = f"Question: {question}\n\n"
        
        # Add context if provided
        if context:
            prompt += "Context information:\n"
            for key, value in context.items():
                prompt += f"{key}: {value}\n"
            prompt += "\n"
        
        prompt += "Please provide a helpful answer to the question."
        
        # Call the Ollama API
        try:
            response_text = self._call_ollama_api(prompt)
        except Exception as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            raise LlmServiceError(f"Failed to communicate with Ollama: {str(e)}")
        
        # Clean and return the response
        return self._clean_text_response(response_text)
    
    def _call_ollama_api(
        self,
        prompt: str,
        system_prompt: str = "You are an expert Jira ticket analyst. Provide concise, accurate information."
    ) -> str:
        """
        Call the Ollama API with a prompt.
        
        Args:
            prompt: The prompt to send to the API
            system_prompt: Optional system prompt to guide the LLM
            
        Returns:
            The text response from the API
            
        Raises:
            OllamaConnectionError: If there's an error connecting to the API
        """
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "system": system_prompt
        }
        
        try:
            logger.debug(f"Calling Ollama API with model {self.model}")
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code != 200:
                error_msg = f"Ollama API error ({response.status_code}): {response.text}"
                logger.error(error_msg)
                raise OllamaConnectionError(error_msg)
            
            return response.json().get("response", "")
        except requests.RequestException as e:
            error_msg = f"Failed to connect to Ollama API: {str(e)}"
            logger.error(error_msg)
            raise OllamaConnectionError(error_msg)
    
    def _parse_assessment_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the assessment response from the LLM.
        
        Args:
            response: The raw response from the API
            
        Returns:
            Parsed assessment data as a dictionary
            
        Raises:
            InvalidResponseError: If the response can't be parsed
        """
        if not response:
            raise InvalidResponseError("Empty response from LLM")
        
        # Clean the response - some LLMs add markdown code blocks
        cleaned_response = response
        if "```json" in response:
            # Extract content between ```json and ```
            start_idx = response.find("```json") + 7
            end_idx = response.find("```", start_idx)
            if end_idx == -1:
                raise InvalidResponseError("Malformed JSON response: unclosed code block")
            cleaned_response = response[start_idx:end_idx].strip()
        elif "```" in response:
            # Extract content between ``` and ```
            start_idx = response.find("```") + 3
            end_idx = response.find("```", start_idx)
            if end_idx == -1:
                raise InvalidResponseError("Malformed JSON response: unclosed code block")
            cleaned_response = response[start_idx:end_idx].strip()
        
        # Parse the JSON
        try:
            result = json.loads(cleaned_response)
            
            # Ensure all expected fields are present
            required_fields = [
                "is_quiescent", "justification", "responsible_party", 
                "suggested_action", "suggested_deadline", "planned_comment"
            ]
            
            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                raise InvalidResponseError(f"Missing required fields in LLM response: {missing_fields}")
            
            return result
        except json.JSONDecodeError as e:
            raise InvalidResponseError(f"Invalid JSON response from LLM: {str(e)}")
    
    def _clean_text_response(self, response: str) -> str:
        """
        Clean a text response from the LLM.
        
        Args:
            response: The raw response from the API
            
        Returns:
            Cleaned text response
        """
        # Handle empty response
        if not response:
            return ""
        
        # Remove any markdown code blocks
        cleaned_response = response
        if "```" in response:
            # Just remove the code block markers
            cleaned_response = response.replace("```", "")
        
        return cleaned_response.strip()
    
    def _format_ticket_as_yaml(self, ticket: Ticket) -> str:
        """
        Format a ticket as YAML for prompts.
        
        Args:
            ticket: The ticket to format
            
        Returns:
            YAML-formatted ticket information
        """
        # Convert ticket to dict
        ticket_dict = {
            'key': ticket.key,
            'summary': ticket.summary,
            'description': ticket.description,
            'status': ticket.status,
            'issue_type': ticket.issue_type,
            'project': ticket.project_key,
            'workflow': ticket.workflow_status,
            'created_date': ticket.created_date.isoformat(),
            'updated_date': ticket.updated_date.isoformat(),
            'users': {
                'assignee': str(ticket.assignee) if ticket.assignee else None,
                'reporter': str(ticket.reporter) if ticket.reporter else None,
                'creator': str(ticket.creator) if ticket.creator else None
            },
            'labels': ticket.labels,
            'components': ticket.components,
            'watchers': [str(w) for w in ticket.watchers],
            'comments': [],
            'changelog': []
        }
        
        # Add comments
        for comment in ticket.comments:
            comment_dict = {
                'id': comment.id,
                'author': str(comment.author),
                'created': comment.created_date.isoformat(),
                'updated': comment.updated_date.isoformat(),
                'body': comment.body,
                'is_system_comment': comment.is_system_comment
            }
            ticket_dict['comments'].append(comment_dict)
        
        # Add changelog
        for change in ticket.changelog:
            change_dict = {
                'date': change.date.isoformat(),
                'author': str(change.author),
                'field': change.field,
                'from_value': change.from_value,
                'to_value': change.to_value
            }
            ticket_dict['changelog'].append(change_dict)
        
        # Convert to YAML
        return yaml.dump(ticket_dict, default_flow_style=False, sort_keys=False)
