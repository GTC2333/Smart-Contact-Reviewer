# smart_contact_audit/agents/risk_annotator.py
from .base_agent import BaseAgent
from typing import List, Dict, Any
import uuid

class RiskAnnotatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="risk_annotator")

    def annotate(self, clause: Dict, law_info: Dict, parties: List[str]) -> Dict | None:
        system_prompt = (
            "你是一名合同风险评估专家。请对本条款进行风险标注，"
            "仅在发现风险时返回 JSON 格式，否则返回空对象 {}。"
        )
        user_prompt = self._render_prompt(
            "risk_annotation_prompt",
            clause_id=clause.get("id", ""),
            clause_content=clause.get("content", ""),
            law_check=law_info,
            parties=parties
        )

        raw_resp = self._call_llm(
            system=system_prompt,
            user=user_prompt,
            response_format={"type": "json_object"}
        )
        data = self._parse_json(raw_resp["raw"])

        if not data:
            return None

        anno = {
            "id": f"anno-{uuid.uuid4().hex[:6]}",
            "clause_id": clause.get("id"),
            "party": data.get("party", "both"),
            "issue_type": data.get("issue_type", "Risk"),
            "description": data.get("description", ""),
            "severity": data.get("severity", "Low").capitalize(),
            "recommendation": data.get("recommendation", ""),
            "law_reference": data.get("law_reference", "")
        }
        return {k: v for k, v in anno.items() if v}