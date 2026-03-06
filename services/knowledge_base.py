"""
Knowledge base service for managing legal documents and RAG data.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.config_manager import get_config_manager
from core.logger import get_logger
from core.rag.factory import create_rag_retriever
from core.rag.interface import RAGRetriever


class KnowledgeBaseService:
    """Service for managing knowledge base and RAG data."""
    
    def __init__(self, rag_retriever: Optional[RAGRetriever] = None):
        """
        Initialize knowledge base service.
        
        Args:
            rag_retriever: Optional RAG retriever (creates default if None)
        """
        self.config = get_config_manager()
        self.logger = get_logger(self.__class__.__name__)
        
        if rag_retriever is None:
            self.rag_retriever = create_rag_retriever()
        else:
            self.rag_retriever = rag_retriever
    
    def add_law_document(self, law_name: str, article: str, content: str):
        """
        Add a law document to the knowledge base.
        
        Args:
            law_name: Name of the law (e.g., "民法典")
            article: Article number (e.g., "第五百一十条")
            content: Article content
        """
        doc_id = f"{law_name}_{article}"
        metadata = {
            "law_name": law_name,
            "article": article,
            "type": "law"
        }
        self.rag_retriever.add_document(doc_id, content, metadata)
        self.logger.info(f"Added law document: {doc_id}")
    
    def add_law_documents_batch(self, documents: List[Dict[str, Any]]):
        """
        Add multiple law documents to the knowledge base.
        
        Args:
            documents: List of dicts with 'law_name', 'article', 'content'
        """
        formatted_docs = []
        for doc in documents:
            doc_id = f"{doc['law_name']}_{doc['article']}"
            formatted_docs.append({
                "id": doc_id,
                "text": doc["content"],
                "metadata": {
                    "law_name": doc["law_name"],
                    "article": doc["article"],
                    "type": "law"
                }
            })
        
        self.rag_retriever.add_documents_batch(formatted_docs)
        self.logger.info(f"Added {len(formatted_docs)} law documents to knowledge base")
    
    def add_case(self, case_id: str, case_title: str, case_content: str, metadata: Optional[Dict] = None):
        """
        Add a legal case to the knowledge base.
        
        Args:
            case_id: Case identifier
            case_title: Case title
            case_content: Case content
            metadata: Optional metadata
        """
        full_text = f"{case_title}\n\n{case_content}"
        case_metadata = {
            "type": "case",
            "case_id": case_id,
            "title": case_title,
            **(metadata or {})
        }
        self.rag_retriever.add_document(case_id, full_text, case_metadata)
        self.logger.info(f"Added case: {case_id}")
    
    def load_from_file(self, file_path: Path):
        """
        Load knowledge base documents from a JSON file.
        
        Args:
            file_path: Path to JSON file with documents
        """
        import json
        
        if not file_path.exists():
            self.logger.warning(f"Knowledge base file not found: {file_path}")
            return
        
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        
        # Support different formats
        if "laws" in data:
            self.add_law_documents_batch(data["laws"])
        elif "documents" in data:
            self.rag_retriever.add_documents_batch(data["documents"])
        else:
            # Assume it's a list of documents
            if isinstance(data, list):
                self.rag_retriever.add_documents_batch(data)
            else:
                self.logger.error(f"Unsupported knowledge base file format: {file_path}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            top_k: Number of results
        
        Returns:
            List of search results
        """
        return self.rag_retriever.retrieve(query, top_k=top_k)


def initialize_default_knowledge_base():
    """Initialize knowledge base with default legal documents."""
    service = KnowledgeBaseService()
    config = get_config_manager()
    
    # Try to load from knowledge base file
    kb_file = config.project_root / "data" / "knowledge_base.json"
    if kb_file.exists():
        service.load_from_file(kb_file)
        return
    
    # Add some default legal documents if file doesn't exist
    default_laws = [
        {
            "law_name": "民法典",
            "article": "第五百一十条",
            "content": "合同生效后，当事人就质量、价款或者报酬、履行地点等内容没有约定或者约定不明确的，可以协议补充；不能达成补充协议的，按照合同相关条款或者交易习惯确定。"
        },
        {
            "law_name": "民法典",
            "article": "第五百九十条",
            "content": "当事人一方因不可抗力不能履行合同的，根据不可抗力的影响，部分或者全部免除责任，但是法律另有规定的除外。因不可抗力不能履行合同的，应当及时通知对方，以减轻可能给对方造成的损失，并应当在合理期限内提供证明。"
        },
        {
            "law_name": "民法典",
            "article": "第五百七十七条",
            "content": "当事人一方不履行合同义务或者履行合同义务不符合约定的，应当承担继续履行、采取补救措施或者赔偿损失等违约责任。"
        }
    ]
    
    service.add_law_documents_batch(default_laws)
    service.logger.info("Initialized default knowledge base with sample legal documents")
