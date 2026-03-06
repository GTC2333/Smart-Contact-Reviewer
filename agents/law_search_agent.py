"""
Law search agent with RAG support.
"""
from .base_agent import BaseAgent
from typing import Dict, Any, Optional
from core.rag.factory import get_rag_retriever
from core.rag.interface import RAGRetriever


class LawSearchAgent(BaseAgent):
    """Law search agent with RAG-enhanced retrieval."""
    
    def __init__(self, rag_retriever: Optional[RAGRetriever] = None):
        """
        Initialize law search agent.
        
        Args:
            rag_retriever: Optional RAG retriever (uses global instance if None)
        """
        super().__init__(agent_name="law_search")
        self.rag_retriever = rag_retriever
        if self.rag_retriever is None:
            try:
                self.rag_retriever = get_rag_retriever()
            except Exception as e:
                self.logger.warning(f"RAG retriever not available: {e}. Continuing without RAG.")
                self.rag_retriever = None
    
    def check_law(self, clause_content: str) -> Dict[str, Any]:
        """
        Check law references in clause with RAG enhancement.
        
        Args:
            clause_content: Clause content to check
        
        Returns:
            Law information dictionary
        """
        # Retrieve relevant legal documents using RAG
        retrieved_context = ""
        if self.rag_retriever:
            try:
                results = self.rag_retriever.retrieve(clause_content, top_k=3)
                if results:
                    retrieved_context = "\n\n相关法条参考：\n"
                    for i, result in enumerate(results, 1):
                        retrieved_context += f"{i}. {result.get('text', '')[:200]}...\n"
                        if result.get('metadata', {}).get('law_name'):
                            retrieved_context += f"   来源：{result['metadata']['law_name']}\n"
                    self.logger.info(f"Retrieved {len(results)} relevant legal documents")
            except Exception as e:
                self.logger.warning(f"RAG retrieval failed: {e}. Continuing without context.")
        
        # Build enhanced prompt with RAG context
        system_prompt = "你是一名法律检索专家。请返回 JSON 格式，字段严格遵守模板。"
        user_prompt = self._render_prompt(
            "law_search_prompt",
            clause_content=clause_content,
            retrieved_context=retrieved_context if retrieved_context else ""
        )
        
        raw_resp = self._call_llm(
            system=system_prompt,
            user=user_prompt,
            response_format={"type": "json_object"}
        )
        result = self._parse_json(raw_resp["raw"])
        
        result.setdefault("matched", False)
        result.setdefault("law_name", "")
        result.setdefault("article", "")
        result.setdefault("issue", "")
        return result
