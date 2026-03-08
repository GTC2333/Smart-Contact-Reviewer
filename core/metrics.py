"""
Metrics collection for audit pipeline.
"""
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import time


@dataclass
class AuditMetrics:
    """Metrics for a single audit operation."""
    timestamp: str
    contract_name: str
    duration_seconds: float
    clause_count: int
    annotation_count: int
    error: Optional[str] = None


class MetricsCollector:
    """Collects and aggregates metrics for audit operations."""

    def __init__(self):
        self.metrics: List[AuditMetrics] = []
        self._start_times: Dict[str, float] = {}

    def start_audit(self, contract_name: str) -> str:
        """Start tracking an audit operation."""
        audit_id = f"{contract_name}_{time.time()}"
        self._start_times[audit_id] = time.time()
        return audit_id

    def record(
        self,
        audit_id: str,
        contract_name: str,
        clause_count: int = 0,
        annotation_count: int = 0,
        error: Optional[str] = None
    ):
        """Record metrics for a completed audit."""
        start_time = self._start_times.pop(audit_id, time.time())
        duration = time.time() - start_time

        metrics = AuditMetrics(
            timestamp=datetime.now().isoformat(),
            contract_name=contract_name,
            duration_seconds=round(duration, 2),
            clause_count=clause_count,
            annotation_count=annotation_count,
            error=error
        )
        self.metrics.append(metrics)

    def get_summary(self) -> Dict:
        """Get summary statistics."""
        total = len(self.metrics)
        if total == 0:
            return {
                "total_audits": 0,
                "avg_duration_seconds": 0,
                "total_clauses": 0,
                "total_annotations": 0,
            }

        successful = [m for m in self.metrics if not m.error]
        failed = [m for m in self.metrics if m.error]

        durations = [m.duration_seconds for m in self.metrics]
        clause_counts = [m.clause_count for m in self.metrics]
        annotation_counts = [m.annotation_count for m in self.metrics]

        return {
            "total_audits": total,
            "successful_audits": len(successful),
            "failed_audits": len(failed),
            "avg_duration_seconds": round(sum(durations) / len(durations), 2),
            "min_duration_seconds": round(min(durations), 2),
            "max_duration_seconds": round(max(durations), 2),
            "total_clauses": sum(clause_counts),
            "total_annotations": sum(annotation_counts),
            "avg_clauses_per_contract": round(sum(clause_counts) / len(clause_counts), 1),
            "avg_annotations_per_contract": round(sum(annotation_counts) / len(annotation_counts), 1),
        }

    def get_recent(self, limit: int = 10) -> List[Dict]:
        """Get recent metrics."""
        recent = sorted(self.metrics, key=lambda m: m.timestamp, reverse=True)[:limit]
        return [asdict(m) for m in recent]

    def clear(self):
        """Clear all metrics."""
        self.metrics.clear()
        self._start_times.clear()


# Global metrics collector instance
metrics_collector = MetricsCollector()
