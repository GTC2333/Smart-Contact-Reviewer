"""
Contract audit pipeline implementation.
"""
from typing import Dict, Any, List
from datetime import datetime
import uuid

from .interface import Pipeline, PipelineStep
from core.logger import get_logger
from models.contract import FormattedContract
from models.annotation import AnnotationResult


class ContractFormatterStep(PipelineStep):
    """Step 1: Format contract into structured clauses."""
    
    def __init__(self, formatter_agent):
        self.formatter = formatter_agent
        self.logger = get_logger(self.__class__.__name__)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Format contract text into structured clauses."""
        contract_text = context.get("contract_text")
        if not contract_text:
            raise ValueError("contract_text is required")
        
        self.logger.info("Formatting contract into clauses...")
        formatted = self.formatter.process(contract_text)
        context["formatted_contract"] = formatted
        return context


class LawSearchStep(PipelineStep):
    """Step 2: Search for legal references in clauses."""
    
    def __init__(self, law_search_agent):
        self.law_search = law_search_agent
        self.logger = get_logger(self.__class__.__name__)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Search legal references for each clause."""
        formatted = context.get("formatted_contract", {})
        clauses = formatted.get("clauses", [])
        
        self.logger.info(f"Searching legal references for {len(clauses)} clauses...")
        law_results = []
        for clause in clauses:
            law_info = self.law_search.check_law(clause.get("content", ""))
            law_results.append({
                "clause_id": clause.get("id"),
                "law_info": law_info
            })
        
        context["law_results"] = law_results
        return context


class RiskAnnotationStep(PipelineStep):
    """Step 3: Annotate risks in clauses."""
    
    def __init__(self, risk_annotator_agent):
        self.risk_annotator = risk_annotator_agent
        self.logger = get_logger(self.__class__.__name__)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Annotate risks for each clause."""
        formatted = context.get("formatted_contract", {})
        clauses = formatted.get("clauses", [])
        parties = formatted.get("parties", [])
        law_results = context.get("law_results", [])
        
        # Create lookup for law results
        law_lookup = {r["clause_id"]: r["law_info"] for r in law_results}
        
        self.logger.info(f"Annotating risks for {len(clauses)} clauses...")
        annotations = []
        for clause in clauses:
            clause_id = clause.get("id")
            law_info = law_lookup.get(clause_id, {})
            
            # Convert parties to list of strings for compatibility
            parties_list = [p.get("name", "") if isinstance(p, dict) else str(p) for p in parties]
            
            risk_info = self.risk_annotator.annotate(clause, law_info, parties_list)
            if risk_info:
                risk_info["original_clause"] = clause.get("content", "")
                annotations.append(risk_info)
        
        context["annotations"] = annotations
        return context


class CorrectionStep(PipelineStep):
    """Step 4: Generate correction suggestions."""
    
    def __init__(self, correction_agent):
        self.correction_agent = correction_agent
        self.logger = get_logger(self.__class__.__name__)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate correction suggestions for risks."""
        annotations = context.get("annotations", [])
        
        self.logger.info(f"Generating corrections for {len(annotations)} risks...")
        final_annotations = []
        for risk_info in annotations:
            correction = self.correction_agent.suggest(risk_info)
            if correction:
                # Merge risk info and correction
                merged = {**risk_info, **correction}
                final_annotations.append(merged)
            else:
                # Keep risk info even if no correction
                final_annotations.append(risk_info)
        
        context["final_annotations"] = final_annotations
        return context


class ContractAuditPipeline(Pipeline):
    """Main contract audit pipeline."""
    
    def __init__(
        self,
        formatter_agent,
        law_search_agent,
        risk_annotator_agent,
        correction_agent
    ):
        """Initialize pipeline with agents."""
        self.steps: List[PipelineStep] = [
            ContractFormatterStep(formatter_agent),
            LawSearchStep(law_search_agent),
            RiskAnnotationStep(risk_annotator_agent),
            CorrectionStep(correction_agent),
        ]
        self.logger = get_logger(self.__class__.__name__)
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the complete audit pipeline.
        
        Args:
            input_data: Dict with 'contract_text' key
        
        Returns:
            Complete audit result dictionary
        """
        contract_text = input_data.get("contract_text")
        if not contract_text:
            raise ValueError("contract_text is required in input_data")
        
        # Generate contract ID
        contract_id = f"C{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        
        # Initialize context
        context = {
            "contract_text": contract_text,
            "contract_id": contract_id,
        }
        
        # Execute pipeline steps
        self.logger.info(f"Starting audit pipeline for contract {contract_id}")
        for i, step in enumerate(self.steps, 1):
            self.logger.info(f"Executing step {i}/{len(self.steps)}: {step.__class__.__name__}")
            try:
                context = step.execute(context)
            except Exception as e:
                self.logger.error(f"Step {i} failed: {e}")
                raise
        
        # Build final result
        formatted = context.get("formatted_contract", {})
        final_annotations = context.get("final_annotations", [])
        
        # Convert to AnnotationResult models
        annotation_results = []
        for anno in final_annotations:
            annotation_results.append(AnnotationResult(
                id=anno.get("id", ""),
                clause_id=anno.get("clause_id", ""),
                party=anno.get("party", "both"),
                issue_type=anno.get("issue_type", "Risk"),
                description=anno.get("description", ""),
                severity=anno.get("severity", "Low"),
                recommendation=anno.get("recommendation", ""),
                law_reference=anno.get("law_reference", ""),
                suggested_revision=anno.get("suggested_revision"),
                note=anno.get("note"),
            ))
        
        result = {
            "contract_id": contract_id,
            "metadata": {
                "processed_at": datetime.now().isoformat(),
                "clause_count": len(formatted.get("clauses", [])),
                "party_count": len(formatted.get("parties", [])),
            },
            "parties": formatted.get("parties", []),
            "annotations": [a.dict() for a in annotation_results],
        }
        
        self.logger.info(f"Pipeline completed for contract {contract_id}")
        return result
