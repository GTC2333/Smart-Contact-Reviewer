"""
Contract data models.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Party(BaseModel):
    """Contract party model."""
    role: str = Field(..., description="Party role (e.g., '甲方', '乙方')")
    name: str = Field(..., description="Party name")


class Clause(BaseModel):
    """Contract clause model."""
    id: str = Field(..., description="Clause identifier")
    title: str = Field(default="", description="Clause title")
    content: str = Field(..., description="Clause content")


class FormattedContract(BaseModel):
    """Formatted contract structure."""
    clauses: List[Clause] = Field(default_factory=list, description="List of contract clauses")
    parties: List[Party] = Field(default_factory=list, description="List of contract parties")
    
    @classmethod
    def from_dict(cls, data: dict) -> "FormattedContract":
        """Create from dictionary."""
        clauses = [Clause(**c) if isinstance(c, dict) else c for c in data.get("clauses", [])]
        parties = [Party(**p) if isinstance(p, dict) else p for p in data.get("parties", [])]
        return cls(clauses=clauses, parties=parties)


class ContractInput(BaseModel):
    """Input contract data."""
    contract_text: str = Field(..., description="Raw contract text")
