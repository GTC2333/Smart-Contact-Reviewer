"""
Pipeline service for contract audit.
Provides high-level interface for running audit pipelines.
"""
from typing import Dict, Any, Optional, Callable

from core.pipeline.contract_pipeline import ContractAuditPipeline
from core.logger import get_logger
from agents import (
    ContractFormatterAgent,
    LawSearchAgent,
    RiskAnnotatorAgent,
    CorrectionAgent,
)


class PipelineService:
    """Service for running contract audit pipelines."""

    def __init__(
        self,
        formatter_agent: Optional[ContractFormatterAgent] = None,
        law_search_agent: Optional[LawSearchAgent] = None,
        risk_annotator_agent: Optional[RiskAnnotatorAgent] = None,
        correction_agent: Optional[CorrectionAgent] = None,
        max_workers: int = 5,
    ):
        """
        Initialize pipeline service with agents.

        Args:
            formatter_agent: Optional formatter agent (creates default if None)
            law_search_agent: Optional law search agent (creates default if None)
            risk_annotator_agent: Optional risk annotator agent (creates default if None)
            correction_agent: Optional correction agent (creates default if None)
            max_workers: Maximum parallel workers for LLM calls
        """
        self.logger = get_logger(self.__class__.__name__)
        self.max_workers = max_workers

        # Create agents if not provided (dependency injection)
        self.formatter = formatter_agent or ContractFormatterAgent()
        self.law_search = law_search_agent or LawSearchAgent()
        self.risk_annotator = risk_annotator_agent or RiskAnnotatorAgent()
        self.correction = correction_agent or CorrectionAgent()

        # Create pipeline with parallel processing
        self.pipeline = ContractAuditPipeline(
            formatter_agent=self.formatter,
            law_search_agent=self.law_search,
            risk_annotator_agent=self.risk_annotator,
            correction_agent=self.correction,
            max_workers=max_workers,
        )

    def audit_contract(
        self,
        contract_text: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Run audit pipeline on contract text.

        Args:
            contract_text: Raw contract text
            progress_callback: Optional callback for progress updates (progress, message)

        Returns:
            Audit result dictionary
        """
        self.logger.info("Starting contract audit...")

        # Set progress callback on pipeline
        if progress_callback:
            self.pipeline.set_progress_callback(progress_callback)

        input_data = {"contract_text": contract_text}
        result = self.pipeline.run(input_data)
        self.logger.info(f"Audit completed for contract {result.get('contract_id')}")
        return result


# Global service instance (singleton pattern)
_service_instance: Optional[PipelineService] = None


def get_pipeline_service() -> PipelineService:
    """Get the global pipeline service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = PipelineService()
    return _service_instance
