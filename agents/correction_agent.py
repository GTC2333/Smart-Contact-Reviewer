# smart_contact_audit/agents/correction_agent.py
from .base_agent import BaseAgent
from typing import Dict, Any

class CorrectionAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="correction")

    def suggest(self, risk_info: Dict) -> Dict | None:
        if not risk_info:
            return None

        system_prompt = "你是一名合同起草专家。请根据风险描述给出修改后的完整条款文本，以 JSON 格式返回。"
        user_prompt = self._render_prompt(
            "correction_prompt",
            risk_description=risk_info.get("description", ""),
            original_clause=risk_info.get("original_clause", ""),
            recommendation=risk_info.get("recommendation", "")
        )

        raw_resp = self._call_llm(
            system=system_prompt,
            user=user_prompt
        )
        data = self._parse_json(raw_resp["raw"])

        if not data:
            return None

        return {
            "clause_id": risk_info.get("clause_id"),
            "suggested_revision": data.get("suggested_revision", ""),
            "note": data.get("note", "")
        }