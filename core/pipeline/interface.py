"""
Pipeline interface definition.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Callable, Optional


class PipelineStep(ABC):
    """Abstract base class for pipeline steps."""

    def __init__(self):
        self._progress_callback: Optional[Callable[[int, str], None]] = None

    def set_progress_callback(self, callback: Callable[[int, str], None]):
        """Set callback for progress updates (percentage, status_message)."""
        self._progress_callback = callback

    def _report_progress(self, progress: int, message: str):
        """Report progress if callback is set."""
        if self._progress_callback:
            self._progress_callback(progress, message)

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the pipeline step.

        Args:
            context: Pipeline context containing input data and intermediate results

        Returns:
            Updated context dictionary
        """
        pass


class Pipeline(ABC):
    """Abstract pipeline interface."""

    def __init__(self):
        self._progress_callback: Optional[Callable[[int, str], None]] = None

    def set_progress_callback(self, callback: Callable[[int, str], None]):
        """Set callback for progress updates."""
        self._progress_callback = callback

    def _report_progress(self, progress: int, message: str):
        """Report progress if callback is set."""
        if self._progress_callback:
            self._progress_callback(progress, message)

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the pipeline with input data.

        Args:
            input_data: Input data dictionary

        Returns:
            Final result dictionary
        """
        pass
