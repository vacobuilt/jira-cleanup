"""
Base ticket iterator implementation.

This module provides the abstract base class for all ticket iterators,
defining the interface that all concrete iterator implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Optional, Dict, Any


class TicketIterator(ABC, Iterator[str]):
    """
    Abstract base class for all ticket iterators.
    
    Iterators yield ticket keys (strings) that can be processed
    by the cleanup system. Implementations handle batching, filtering,
    and other selection details internally.
    """
    
    @abstractmethod
    def __iter__(self) -> 'TicketIterator':
        """
        Return self as iterator.
        
        Returns:
            Self, since TicketIterator implements the iterator protocol.
        """
        return self
    
    @abstractmethod
    def __next__(self) -> str:
        """
        Return the next ticket key.
        
        Returns:
            A Jira issue key (e.g., 'PROJ-123')
            
        Raises:
            StopIteration: When no more tickets are available
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """
        Reset the iterator to start from the beginning.
        
        This allows reusing the same iterator instance for multiple passes.
        """
        pass
    
    @property
    @abstractmethod
    def processed_count(self) -> int:
        """
        Get the number of tickets that have been yielded so far.
        
        Returns:
            Count of processed tickets
        """
        pass
