"""
Base agent class with dependency injection.
Simplified to focus on core prompt rendering and LLM calling logic.
"""
import json
import time
from typing import Any, Dict, Optional
from functools import wraps
from jinja2 import Template

from core.config_manager import get_config_manager
from core.logger import get_logger
from core.llm.interface import LLMClient


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry a function on failure with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
            raise last_exception
        return wrapper
    return decorator


class BaseAgent:
    """Base class for all agents with dependency injection."""
    
    def __init__(
        self,
        agent_name: str,
        llm_client: Optional[LLMClient] = None,
        config_manager: Optional[Any] = None
    ):
        """
        Initialize base agent.
        
        Args:
            agent_name: Name of the agent (used for config lookup)
            llm_client: LLM client instance (injected, defaults to global instance)
            config_manager: Config manager instance (injected, defaults to global instance)
        """
        self.config_manager = config_manager or get_config_manager()
        self.llm_client = llm_client
        
        # Get agent-specific configuration
        agent_config = self.config_manager.get_agent_config(agent_name)
        model_mapping = self.config_manager.get("model_mapping", {})

        # Get model name and apply mapping (default to deepseek-chat if not specified)
        model_name = agent_config.get("model", "deepseek-chat")
        self.model = model_mapping.get(model_name, model_name)
        self.temperature = agent_config.get("temperature", 0.0)
        self.max_tokens = agent_config.get("max_tokens", 1000)
        
        # Get logger
        self.logger = get_logger(self.__class__.__name__)
        
        # Lazy load LLM client if not provided
        if self.llm_client is None:
            from core.llm.factory import get_llm_client
            self.llm_client = get_llm_client()
    
    def _render_prompt(self, template_key: str, **kwargs) -> str:
        """
        Render prompt template with given variables.
        
        Args:
            template_key: Key to lookup in prompt templates
            **kwargs: Variables to render in template
        
        Returns:
            Rendered prompt string
        """
        template_str = self.config_manager.get_prompt_template(template_key)
        return Template(template_str).render(**kwargs)
    
    @retry_on_failure(max_retries=3, delay=2.0, backoff=2.0)
    def _call_llm(
        self,
        system: str,
        user: str,
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call LLM with system and user prompts.
        Includes automatic retry on failure with exponential backoff.

        Args:
            system: System prompt
            user: User prompt
            response_format: Optional response format specification

        Returns:
            Dict with 'raw' key containing response content
        """
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]

        provider = self.config_manager.get("llm.provider", "openai")
        self.logger.info(f"Calling {self.model} via {provider} | system_len={len(system)}")
        
        try:
            result = self.llm_client.chat_completion(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format=response_format or {"type": "text"},
                timeout=120,
            )
            content = result["content"]
            self.logger.info(f"LLM response received, len={len(content)}")
            return {"raw": content}
        except Exception as e:
            self.logger.error(f"LLM error: {e}")
            raise
    
    def _parse_json(self, raw: str) -> Dict:
        """
        Parse JSON from raw string, handling markdown code blocks.

        Args:
            raw: Raw JSON string, possibly wrapped in markdown

        Returns:
            Parsed JSON dictionary
        """
        # First try the raw string
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # Try to clean markdown code blocks
        cleaned = raw.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        # Try parsing again
        try:
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            pass

        # Try with ast.literal_eval as fallback
        try:
            import ast
            return ast.literal_eval(cleaned.strip())
        except:
            pass

        # If all fails, raise the original error
        raise ValueError(f"Failed to parse JSON from: {cleaned[:200]}...")
