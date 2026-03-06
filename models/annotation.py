"""
Annotation and risk assessment models.
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class LawInfo(BaseModel):
    """Legal reference information."""
    matched: bool = Field(default=False, description="Whether law reference is matched")
    law_name: str = Field(default="", description="Law name")
    article: str = Field(default="", description="Article number")
    issue: str = Field(default="", description="Issue description")


class RiskAnnotation(BaseModel):
    """Risk annotation model."""
    id: str = Field(..., description="Annotation identifier")
    clause_id: str = Field(..., description="Associated clause ID")
    party: str = Field(..., description="Affected party")
    issue_type: str = Field(default="Risk", description="Type of issue")
    description: str = Field(..., description="Risk description")
    severity: str = Field(..., description="Risk severity (High/Medium/Low)")
    recommendation: str = Field(default="", description="Recommendation")
    law_reference: str = Field(default="", description="Legal reference")
    original_clause: Optional[str] = Field(default=None, description="Original clause content")


class Correction(BaseModel):
    """Correction suggestion model."""
    clause_id: str = Field(..., description="Clause ID to correct")
    suggested_revision: str = Field(..., description="Suggested revised clause text")
    note: str = Field(default="", description="Additional notes")


class AnnotationResult(BaseModel):
    """Complete annotation result combining risk and correction."""
    id: str
    clause_id: str
    party: str
    issue_type: str
    description: str
    severity: str
    recommendation: str
    law_reference: str
    suggested_revision: Optional[str] = None
    note: Optional[str] = None


class AuditResult(BaseModel):
    """Complete audit result."""
    contract_id: str = Field(..., description="Contract identifier")
    metadata: dict = Field(default_factory=dict, description="Processing metadata")
    parties: List[dict] = Field(default_factory=list, description="Contract parties")
    annotations: List[AnnotationResult] = Field(default_factory=list, description="Risk annotations")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
