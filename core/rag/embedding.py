"""
Embedding service implementations.
"""
from typing import List
import numpy as np

from core.config_manager import get_config_manager
from core.logger import get_logger
from .interface import EmbeddingModel


class OpenAIEmbeddingModel(EmbeddingModel):
    """OpenAI embedding model."""

    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize OpenAI embedding model.

        Args:
            model: Embedding model name
        """
        from openai import OpenAI as OpenAIClient

        self.config = get_config_manager()
        self.logger = get_logger(self.__class__.__name__)
        llm_config = self.config.get_llm_config()
        openai_cfg = llm_config.get("openai", {})

        self.client = OpenAIClient(
            api_key=openai_cfg.get("api_key", ""),
            base_url=openai_cfg.get("base_url"),
            timeout=60,
        )
        self.model = model

    def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"Embedding failed: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            self.logger.error(f"Batch embedding failed: {e}")
            raise


class OllamaEmbeddingModel(EmbeddingModel):
    """Ollama local embedding model."""

    def __init__(self, model: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama embedding model.

        Args:
            model: Ollama embedding model name (e.g., nomic-embed-text, mxbai-embed-large)
            base_url: Ollama server URL
        """
        import httpx

        self.config = get_config_manager()
        self.logger = get_logger(self.__class__.__name__)

        # Get RAG config for Ollama settings
        rag_config = self.config.get("rag", {})
        ollama_cfg = rag_config.get("ollama", {})

        self.model = ollama_cfg.get("model", model)
        self.base_url = ollama_cfg.get("base_url", base_url)
        self.client = httpx.Client(timeout=60)

    def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        try:
            response = self.client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text}
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            self.logger.error(f"Ollama embedding failed: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        # Ollama doesn't support batch embedding, call sequentially
        return [self.embed(text) for text in texts]


class SimpleEmbeddingModel(EmbeddingModel):
    """Simple TF-IDF-like embedding for testing (not production-ready)."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.logger.warning("Using simple embedding model - not recommended for production")
    
    def embed(self, text: str) -> List[float]:
        """Simple character-based embedding (for testing only)."""
        # This is a placeholder - in production, use proper embedding models
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        # Convert to 128-dim vector (simple hash-based)
        vector = [int(hash_hex[i:i+2], 16) / 255.0 for i in range(0, min(256, len(hash_hex)), 2)]
        # Pad or truncate to 128 dimensions
        while len(vector) < 128:
            vector.append(0.0)
        return vector[:128]
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return [self.embed(text) for text in texts]


def create_embedding_model(model_type: str = "openai", **kwargs) -> EmbeddingModel:
    """
    Factory function to create embedding model.

    Args:
        model_type: Type of embedding model ('openai', 'simple', or 'ollama')
        **kwargs: Additional arguments for model initialization

    Returns:
        EmbeddingModel instance
    """
    if model_type == "openai":
        return OpenAIEmbeddingModel(model=kwargs.get("model", "text-embedding-3-small"))
    elif model_type == "simple":
        return SimpleEmbeddingModel()
    elif model_type == "ollama":
        return OllamaEmbeddingModel(
            model=kwargs.get("model", "nomic-embed-text"),
            base_url=kwargs.get("base_url", "http://localhost:11434")
        )
    else:
        raise ValueError(f"Unsupported embedding model type: {model_type}")
