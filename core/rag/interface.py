"""
RAG interface definitions.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class EmbeddingModel(ABC):
    """Abstract interface for embedding models."""
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
        
        Returns:
            Embedding vector
        """
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
        
        Returns:
            List of embedding vectors
        """
        pass


class VectorStore(ABC):
    """Abstract interface for vector storage."""
    
    @abstractmethod
    def add(self, id: str, text: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None):
        """
        Add a document to the vector store.
        
        Args:
            id: Document identifier
            text: Document text
            embedding: Document embedding vector
            metadata: Optional metadata
        """
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
        
        Returns:
            List of search results with 'id', 'text', 'score', 'metadata'
        """
        pass
    
    @abstractmethod
    def delete(self, id: str):
        """
        Delete a document from the store.
        
        Args:
            id: Document identifier
        """
        pass
    
    @abstractmethod
    def clear(self):
        """Clear all documents from the store."""
        pass


class RAGRetriever(ABC):
    """Abstract interface for RAG retrieval."""
    
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query text
            top_k: Number of results to return
        
        Returns:
            List of retrieved documents with 'text', 'score', 'metadata'
        """
        pass
