"""
Vector store implementations.
"""
from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path
import json
import pickle

from core.logger import get_logger
from .interface import VectorStore


class InMemoryVectorStore(VectorStore):
    """In-memory vector store using cosine similarity."""
    
    def __init__(self):
        """Initialize in-memory vector store."""
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.embeddings: Dict[str, List[float]] = {}
        self.logger = get_logger(self.__class__.__name__)
    
    def add(self, id: str, text: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None):
        """Add a document to the store."""
        self.documents[id] = {
            "text": text,
            "metadata": metadata or {}
        }
        self.embeddings[id] = embedding
        self.logger.debug(f"Added document {id} to vector store")
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using cosine similarity."""
        if not self.embeddings:
            return []
        
        query_vec = np.array(query_embedding)
        results = []
        
        for doc_id, doc_embedding in self.embeddings.items():
            doc_vec = np.array(doc_embedding)
            # Cosine similarity
            similarity = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
            results.append({
                "id": doc_id,
                "text": self.documents[doc_id]["text"],
                "score": float(similarity),
                "metadata": self.documents[doc_id]["metadata"]
            })
        
        # Sort by similarity (descending) and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def delete(self, id: str):
        """Delete a document from the store."""
        if id in self.documents:
            del self.documents[id]
            del self.embeddings[id]
            self.logger.debug(f"Deleted document {id} from vector store")
    
    def clear(self):
        """Clear all documents."""
        self.documents.clear()
        self.embeddings.clear()
        self.logger.info("Cleared vector store")
    
    def save(self, file_path: Path):
        """Save vector store to disk."""
        data = {
            "documents": self.documents,
            "embeddings": self.embeddings
        }
        with open(file_path, "wb") as f:
            pickle.dump(data, f)
        self.logger.info(f"Saved vector store to {file_path}")
    
    def load(self, file_path: Path):
        """Load vector store from disk."""
        if file_path.exists():
            with open(file_path, "rb") as f:
                data = pickle.load(f)
            self.documents = data["documents"]
            self.embeddings = data["embeddings"]
            self.logger.info(f"Loaded vector store from {file_path}")
        else:
            self.logger.warning(f"Vector store file not found: {file_path}")


class PersistentVectorStore(InMemoryVectorStore):
    """Persistent vector store that saves to disk."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize persistent vector store.
        
        Args:
            storage_path: Path to storage file
        """
        super().__init__()
        from core.config_manager import get_config_manager
        config = get_config_manager()
        
        if storage_path is None:
            storage_path = config.project_root / "outputs" / "vector_store.pkl"
        
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data if available
        self.load(self.storage_path)
    
    def add(self, id: str, text: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None):
        """Add document and auto-save."""
        super().add(id, text, embedding, metadata)
        self.save(self.storage_path)
    
    def delete(self, id: str):
        """Delete document and auto-save."""
        super().delete(id)
        self.save(self.storage_path)
    
    def clear(self):
        """Clear all documents and save."""
        super().clear()
        self.save(self.storage_path)
