"""
Factory for creating RAG components.
"""
from typing import Optional
from pathlib import Path

from core.config_manager import get_config_manager
from .embedding import create_embedding_model
from .vector_store import PersistentVectorStore
from .retriever import SimpleRAGRetriever


def create_rag_retriever(
    embedding_model_type: Optional[str] = None,
    vector_store_path: Optional[Path] = None
) -> SimpleRAGRetriever:
    """
    Factory function to create RAG retriever.
    
    Args:
        embedding_model_type: Type of embedding model (defaults to config)
        vector_store_path: Path to vector store file (defaults to config)
    
    Returns:
        RAGRetriever instance
    """
    config = get_config_manager()
    rag_config = config.get("rag", {})
    
    # Create embedding model
    model_type = embedding_model_type or rag_config.get("embedding_model", "openai")
    embedding_model = create_embedding_model(
        model_type=model_type,
        model=rag_config.get("embedding_model_name", "text-embedding-3-small")
    )
    
    # Create vector store
    if vector_store_path is None:
        store_path = config.project_root / "outputs" / "vector_store.pkl"
    else:
        store_path = vector_store_path
    
    vector_store = PersistentVectorStore(storage_path=store_path)
    
    # Create retriever
    retriever = SimpleRAGRetriever(embedding_model, vector_store)
    
    return retriever


# Global retriever instance
_rag_retriever: Optional[SimpleRAGRetriever] = None


def get_rag_retriever() -> SimpleRAGRetriever:
    """Get the global RAG retriever instance (singleton)."""
    global _rag_retriever
    if _rag_retriever is None:
        config = get_config_manager()
        rag_config = config.get("rag", {})
        
        # Only create if RAG is enabled
        if rag_config.get("enabled", True):
            _rag_retriever = create_rag_retriever()
            
            # Auto-initialize knowledge base if empty
            if hasattr(_rag_retriever.vector_store, 'documents'):
                if not _rag_retriever.vector_store.documents:
                    try:
                        from services.knowledge_base import initialize_default_knowledge_base
                        initialize_default_knowledge_base()
                    except Exception as e:
                        from core.logger import get_logger
                        logger = get_logger(__name__)
                        logger.warning(f"Failed to auto-initialize knowledge base: {e}")
        else:
            raise ValueError("RAG is disabled in configuration")
    
    return _rag_retriever
