"""
Pipeline interface definition.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class PipelineStep(ABC):
    """Abstract base class for pipeline steps."""
    
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
