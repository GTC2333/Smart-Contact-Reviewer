# smart_contract_audit/agents/__init__.py
"""
agents 包的公共入口。
把所有 Agent 类重新导出，方便 `from agents import X`。
"""

from .contract_formatter import ContractFormatterAgent
from .law_search_agent import LawSearchAgent
from .risk_annotator import RiskAnnotatorAgent
from .correction_agent import CorrectionAgent

__all__ = [
    "ContractFormatterAgent",
    "LawSearchAgent",
    "RiskAnnotatorAgent",
    "CorrectionAgent",
]