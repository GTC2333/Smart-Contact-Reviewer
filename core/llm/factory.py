"""
LLM client factory for creating different provider clients.
"""
from typing import Dict, Any, Optional, List
from .interface import LLMClient
from ..config_manager import get_config_manager


class OpenAICompatibleClient(LLMClient):
    """OpenAI-compatible client wrapper."""
    
    def __init__(self, client: Any):
        self.client = client
    
    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """Create chat completion using OpenAI-compatible API."""
        resp = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format or {"type": "text"},
            timeout=timeout,
        )
        return {"content": resp.choices[0].message.content.strip()}


class AnthropicCompatibleClient(LLMClient):
    """Anthropic Claude client wrapper."""
    
    def __init__(self, client: Any):
        self.client = client
    
    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """Create chat completion using Anthropic API."""
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] != "system"]
        
        resp = self.client.messages.create(
            model=model,
            system=system,
            messages=user_messages,
            max_tokens=max_tokens or 1024,
            temperature=temperature,
        )
        return {"content": resp.content[0].text}


class GeminiCompatibleClient(LLMClient):
    """Google Gemini client wrapper."""
    
    def __init__(self, model: Any):
        self.model = model
    
    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """Create chat completion using Gemini API."""
        import google.generativeai as genai
        
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        content = "\n".join(m["content"] for m in messages if m["role"] != "system")
        
        if system:
            content = f"[SYSTEM]: {system}\n{content}"
        
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        
        resp = self.model.generate_content(content, generation_config=generation_config)
        return {"content": resp.text}


def create_llm_client() -> LLMClient:
    """
    Factory function to create an LLM client based on configuration.
    
    Returns:
        LLMClient instance
    """
    config = get_config_manager()
    llm_config = config.get_llm_config()
    provider = llm_config.get("provider", "openai")
    model_mapping = config.get("model_mapping", {})
    
    if provider == "openai":
        from openai import OpenAI as OpenAIClient
        openai_cfg = llm_config.get("openai", {})
        client = OpenAIClient(
            api_key=openai_cfg.get("api_key", ""),
            base_url=openai_cfg.get("base_url"),
            timeout=120,
        )
        return OpenAICompatibleClient(client)
    
    elif provider == "azure":
        from openai import OpenAI as OpenAIClient
        import httpx
        azure_cfg = llm_config.get("azure", {})
        client = OpenAIClient(
            api_key=azure_cfg.get("api_key", ""),
            base_url=azure_cfg.get("endpoint", "") + f"openai/deployments/{azure_cfg.get('deployment', '')}",
            http_client=httpx.Client(
                params={"api-version": azure_cfg.get("api_version", "2024-02-01")}
            ),
            timeout=120,
        )
        return OpenAICompatibleClient(client)
    
    elif provider == "anthropic":
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("请安装: pip install anthropic")
        anthropic_cfg = llm_config.get("anthropic", {})
        client = Anthropic(
            api_key=anthropic_cfg.get("api_key", ""),
            base_url=anthropic_cfg.get("base_url"),
        )
        return AnthropicCompatibleClient(client)
    
    elif provider == "gemini":
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("请安装: pip install google-generativeai")
        gemini_cfg = llm_config.get("gemini", {})
        genai.configure(api_key=gemini_cfg.get("api_key", ""))
        model = genai.GenerativeModel(model_mapping.get("default", "gemini-1.5-flash"))
        return GeminiCompatibleClient(model)
    
    elif provider == "deepseek":
        from openai import OpenAI as OpenAIClient
        deepseek_cfg = llm_config.get("deepseek", {})
        client = OpenAIClient(
            api_key=deepseek_cfg.get("api_key", ""),
            base_url=deepseek_cfg.get("base_url", "https://api.deepseek.com/v1"),
            timeout=120,
        )
        return OpenAICompatibleClient(client)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


# Cache the client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get the global LLM client instance (singleton)."""
    global _llm_client
    if _llm_client is None:
        _llm_client = create_llm_client()
    return _llm_client
