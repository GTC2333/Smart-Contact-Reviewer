"""
LLM client interface definition.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class LLMClient(ABC):
    """Abstract interface for LLM clients."""
    
    @abstractmethod
    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        Create a chat completion.
        
        Args:
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_format: Response format specification
            timeout: Request timeout in seconds
        
        Returns:
            Dict with 'content' key containing the response text
        """
        pass
