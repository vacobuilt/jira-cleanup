"""
LLM service interface.

This module defines the interface for LLM services that can be used
for ticket assessment and other NLP tasks.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from jira_cleanup.src.domain.entities.ticket import Ticket
from jira_cleanup.src.domain.entities.assessment import Assessment


class LlmService(ABC):
    """
    Abstract interface for LLM service operations.
    
    This interface defines the operations that any LLM service provider
    must implement, allowing the application to remain independent of
    specific LLM implementations.
    """
    
    @abstractmethod
    def assess_ticket(self, ticket: Ticket) -> Assessment:
        """
        Assess a ticket for quiescence using the LLM.
        
        Args:
            ticket: The ticket to assess
            
        Returns:
            Assessment result containing the LLM's evaluation
            
        Raises:
            LlmServiceError: If there's an error communicating with the LLM
            InvalidResponseError: If the LLM's response can't be parsed
        """
        pass
    
    @abstractmethod
    def generate_comment(
        self,
        ticket: Ticket,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a comment for a ticket using the LLM.
        
        Args:
            ticket: The ticket to generate a comment for
            context: Optional additional context for comment generation
            
        Returns:
            Generated comment text
            
        Raises:
            LlmServiceError: If there's an error communicating with the LLM
        """
        pass
    
    @abstractmethod
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
        pass
