# smart_contact_audit/agents/contract_formatter.py
from .base_agent import BaseAgent
from typing import List, Dict

class ContractFormatterAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="contract_formatter")

    def process(self, contract_text: str) -> Dict:
        system_prompt = "你是一名专业的合同结构化分析师。请严格按照 JSON 格式输出。"
        user_prompt = self._render_prompt(
            "formatter_prompt",
            contract_text=contract_text
        )

        raw_resp = self._call_llm(
            system=system_prompt,
            user=user_prompt,
            response_format={"type": "json_object"}
        )
        result = self._parse_json(raw_resp["raw"])

        clauses = result.get("clauses", [])
        for i, c in enumerate(clauses):
            c.setdefault("id", str(i + 1))
            c.setdefault("title", "")
            c.setdefault("content", "")
        parties = result.get("parties", [])
        return {"clauses": clauses, "parties": parties}