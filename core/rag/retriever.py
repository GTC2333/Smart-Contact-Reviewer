"""
RAG retriever implementation.
"""
from typing import List, Dict, Any

from core.logger import get_logger
from .interface import RAGRetriever, EmbeddingModel, VectorStore


class SimpleRAGRetriever(RAGRetriever):
    """Simple RAG retriever implementation."""
    
    def __init__(self, embedding_model: EmbeddingModel, vector_store: VectorStore):
        """
        Initialize RAG retriever.
        
        Args:
            embedding_model: Embedding model for query encoding
            vector_store: Vector store for document retrieval
        """
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.logger = get_logger(self.__class__.__name__)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Query text
            top_k: Number of results to return
        
        Returns:
            List of retrieved documents
        """
        # Generate query embedding
        query_embedding = self.embedding_model.embed(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, top_k=top_k)
        
        self.logger.info(f"Retrieved {len(results)} documents for query: {query[:50]}...")
        return results
    
    def add_document(self, id: str, text: str, metadata: Dict[str, Any] = None):
        """
        Add a document to the knowledge base.
        
        Args:
            id: Document identifier
            text: Document text
            metadata: Optional metadata
        """
        embedding = self.embedding_model.embed(text)
        self.vector_store.add(id, text, embedding, metadata)
        self.logger.info(f"Added document {id} to knowledge base")
    
    def add_documents_batch(self, documents: List[Dict[str, Any]]):
        """
        Add multiple documents to the knowledge base.
        
        Args:
            documents: List of dicts with 'id', 'text', and optional 'metadata'
        """
        texts = [doc["text"] for doc in documents]
        embeddings = self.embedding_model.embed_batch(texts)
        
        for doc, embedding in zip(documents, embeddings):
            self.vector_store.add(
                doc["id"],
                doc["text"],
                embedding,
                doc.get("metadata")
            )
        
        self.logger.info(f"Added {len(documents)} documents to knowledge base")
