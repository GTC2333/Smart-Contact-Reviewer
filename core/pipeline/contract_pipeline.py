"""
Contract audit pipeline implementation.
"""
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
import uuid
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .interface import Pipeline, PipelineStep
from core.logger import get_logger
from core.metrics import metrics_collector
from models.contract import FormattedContract
from models.annotation import AnnotationResult


class ContractFormatterStep(PipelineStep):
    """Step 1: Format contract into structured clauses."""

    def __init__(self, formatter_agent):
        super().__init__()
        self.formatter = formatter_agent
        self.logger = get_logger(self.__class__.__name__)

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Format contract text into structured clauses."""
        contract_text = context.get("contract_text")
        if not contract_text:
            raise ValueError("contract_text is required")

        self.logger.info("Formatting contract into clauses...")
        self._report_progress(5, "正在解析合同结构...")
        formatted = self.formatter.process(contract_text)
        self._report_progress(15, "合同解析完成")
        context["formatted_contract"] = formatted
        return context


class LawSearchStep(PipelineStep):
    """Step 2: Search for legal references in clauses (parallel)."""

    def __init__(self, law_search_agent, max_workers: int = 5):
        super().__init__()
        self.law_search = law_search_agent
        self.logger = get_logger(self.__class__.__name__)
        self.max_workers = max_workers

    def _check_law_single(self, clause: Dict) -> Dict:
        """Check law for a single clause."""
        clause_id = clause.get("id")
        clause_content = clause.get("content", "")

        try:
            law_info = self.law_search.check_law(clause_content)

            # Ensure law_info is always a dict
            if isinstance(law_info, list):
                if law_info:
                    law_info = law_info[0] if isinstance(law_info[0], dict) else {
                        "matched": False, "law_name": "", "article": "", "issue": ""
                    }
                else:
                    law_info = {"matched": False, "law_name": "", "article": "", "issue": ""}
            elif not isinstance(law_info, dict):
                law_info = {"matched": False, "law_name": "", "article": "", "issue": ""}

            return {
                "clause_id": clause_id,
                "law_info": law_info
            }
        except Exception as e:
            self.logger.warning(f"Law check failed for clause {clause_id}: {e}")
            return {
                "clause_id": clause_id,
                "law_info": {"matched": False, "law_name": "", "article": "", "issue": ""}
            }

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Search legal references for each clause (parallel)."""
        formatted = context.get("formatted_contract", {})
        clauses = formatted.get("clauses", [])
        clause_count = len(clauses)

        self.logger.info(f"Searching legal references for {clause_count} clauses (parallel)...")
        self._report_progress(20, f"正在检索法律依据 ({0}/{clause_count})...")

        law_results = []
        completed = 0

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_clause = {
                executor.submit(self._check_law_single, clause): clause
                for clause in clauses
            }

            for future in as_completed(future_to_clause):
                result = future.result()
                law_results.append(result)
                completed += 1

                # Report progress
                progress = 20 + int((completed / clause_count) * 25)  # 20-45%
                self._report_progress(
                    progress,
                    f"正在检索法律依据 ({completed}/{clause_count})..."
                )

        # Sort results by clause_id to maintain order
        def get_sort_key(x):
            clause_id = x.get("clause_id", 0)
            if isinstance(clause_id, int):
                return clause_id
            if isinstance(clause_id, str) and clause_id.isdigit():
                return int(clause_id)
            return 0
        law_results.sort(key=get_sort_key)

        self._report_progress(45, "法律依据检索完成")
        context["law_results"] = law_results
        return context


class RiskAnnotationStep(PipelineStep):
    """Step 3: Annotate risks in clauses (parallel)."""

    def __init__(self, risk_annotator_agent, max_workers: int = 5):
        super().__init__()
        self.risk_annotator = risk_annotator_agent
        self.logger = get_logger(self.__class__.__name__)
        self.max_workers = max_workers

    def _annotate_single(self, clause: Dict, law_info: Dict, parties_list: List[str]) -> Optional[Dict]:
        """Annotate risk for a single clause."""
        try:
            risk_info = self.risk_annotator.annotate(clause, law_info, parties_list)
            if risk_info:
                risk_info["original_clause"] = clause.get("content", "")
                return risk_info
            return None
        except Exception as e:
            self.logger.warning(f"Risk annotation failed for clause {clause.get('id')}: {e}")
            return None

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Annotate risks for each clause (parallel)."""
        formatted = context.get("formatted_contract", {})
        clauses = formatted.get("clauses", [])
        parties = formatted.get("parties", [])
        law_results = context.get("law_results", [])

        # Create lookup for law results
        law_lookup = {}
        for r in law_results:
            clause_id = r.get("clause_id")
            law_info = r.get("law_info", {})
            if isinstance(law_info, list):
                law_info = law_info[0] if law_info else {}
            law_lookup[clause_id] = law_info

        # Convert parties to list of strings
        parties_list = []
        for p in parties:
            if isinstance(p, dict):
                parties_list.append(p.get("name", p.get("role", "")))
            elif isinstance(p, str):
                parties_list.append(p)
            else:
                parties_list.append(str(p))

        clause_count = len(clauses)
        self.logger.info(f"Annotating risks for {clause_count} clauses (parallel)...")
        self._report_progress(50, f"正在分析风险 ({0}/{clause_count})...")

        annotations = []
        completed = 0

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for clause in clauses:
                clause_id = clause.get("id")
                law_info = law_lookup.get(clause_id, {})
                future = executor.submit(self._annotate_single, clause, law_info, parties_list)
                futures.append(future)

            for future in as_completed(futures):
                result = future.result()
                if result:
                    annotations.append(result)
                completed += 1

                # Report progress
                progress = 50 + int((completed / clause_count) * 20)  # 50-70%
                self._report_progress(
                    progress,
                    f"正在分析风险 ({completed}/{clause_count})..."
                )

        self._report_progress(70, "风险分析完成")
        context["annotations"] = annotations
        return context


class CorrectionStep(PipelineStep):
    """Step 4: Generate correction suggestions (parallel)."""

    def __init__(self, correction_agent, max_workers: int = 5):
        super().__init__()
        self.correction_agent = correction_agent
        self.logger = get_logger(self.__class__.__name__)
        self.max_workers = max_workers

    def _suggest_single(self, risk_info: Dict) -> Dict:
        """Generate correction for a single risk."""
        try:
            correction = self.correction_agent.suggest(risk_info)
            if correction:
                return {**risk_info, **correction}
            return risk_info
        except Exception as e:
            self.logger.warning(f"Correction generation failed: {e}")
            return risk_info

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate correction suggestions for risks (parallel)."""
        annotations = context.get("annotations", [])
        annotation_count = len(annotations)

        self.logger.info(f"Generating corrections for {annotation_count} risks (parallel)...")
        self._report_progress(75, f"正在生成修改建议 ({0}/{annotation_count})...")

        final_annotations = []
        completed = 0

        if annotation_count > 0:
            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [
                    executor.submit(self._suggest_single, risk_info)
                    for risk_info in annotations
                ]

                for future in as_completed(futures):
                    result = future.result()
                    final_annotations.append(result)
                    completed += 1

                    # Report progress
                    progress = 75 + int((completed / annotation_count) * 20)  # 75-95%
                    self._report_progress(
                        progress,
                        f"正在生成修改建议 ({completed}/{annotation_count})..."
                    )
        else:
            self._report_progress(95, "无需生成修改建议")

        self._report_progress(95, "修改建议生成完成")
        context["final_annotations"] = final_annotations
        return context


class ContractAuditPipeline(Pipeline):
    """Main contract audit pipeline."""

    def __init__(
        self,
        formatter_agent,
        law_search_agent,
        risk_annotator_agent,
        correction_agent,
        max_workers: int = 5
    ):
        """Initialize pipeline with agents."""
        self.max_workers = max_workers
        self.steps: List[PipelineStep] = [
            ContractFormatterStep(formatter_agent),
            LawSearchStep(law_search_agent, max_workers=max_workers),
            RiskAnnotationStep(risk_annotator_agent, max_workers=max_workers),
            CorrectionStep(correction_agent, max_workers=max_workers),
        ]
        self.logger = get_logger(self.__class__.__name__)
        self._progress_callback: Optional[Callable[[int, str], None]] = None

    def set_progress_callback(self, callback: Callable[[int, str], None]):
        """Set global progress callback and propagate to steps."""
        self._progress_callback = callback
        for step in self.steps:
            step.set_progress_callback(callback)

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

        # Start metrics tracking
        contract_name = input_data.get("contract_name", contract_id)
        audit_id = metrics_collector.start_audit(contract_name)
        start_time = time.time()

        # Execute pipeline steps
        self.logger.info(f"Starting audit pipeline for contract {contract_id}")
        self._report_progress(0, "开始审核合同...")

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
            "contract_text": contract_text,
            "metadata": {
                "processed_at": datetime.now().isoformat(),
                "clause_count": len(formatted.get("clauses", [])),
                "party_count": len(formatted.get("parties", [])),
            },
            "parties": formatted.get("parties", []),
            "clauses": formatted.get("clauses", []),
            "annotations": [a.dict() for a in annotation_results],
            "corrections": [
                {
                    "clause_id": a.clause_id,
                    "issue": a.description,
                    "suggested_revision": a.suggested_revision,
                    "note": a.note,
                }
                for a in annotation_results
                if a.suggested_revision or a.note
            ],
        }

        # Record metrics
        duration = time.time() - start_time
        metrics_collector.record(
            audit_id=audit_id,
            contract_name=contract_name,
            clause_count=len(formatted.get("clauses", [])),
            annotation_count=len(annotation_results)
        )

        self._report_progress(100, "审核完成")
        self.logger.info(f"Pipeline completed for contract {contract_id} in {duration:.2f}s")
        return result
