"""
Audit service for API layer.
Handles file uploads and text extraction, then calls pipeline service.
"""
from pathlib import Path
from typing import Dict, Any

from core.logger import get_logger
from utils.file_handler import FileHandler
from services.pipeline_service import get_pipeline_service


class AuditService:
    """Service for handling audit requests."""
    
    def __init__(self, file_handler: FileHandler = None):
        """
        Initialize audit service.
        
        Args:
            file_handler: Optional file handler (creates default if None)
        """
        self.file_handler = file_handler or FileHandler()
        self.pipeline_service = get_pipeline_service()
        self.logger = get_logger(self.__class__.__name__)
    
    def audit_from_file(
        self,
        file_content: bytes,
        filename: str,
        cleanup: bool = True
    ) -> Dict[str, Any]:
        """
        Audit contract from uploaded file.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            cleanup: Whether to cleanup saved file after processing
        
        Returns:
            Audit result dictionary
        """
        # Validate file type
        if not self.file_handler.validate_file_type(filename):
            raise ValueError(f"Unsupported file type: {filename}")
        
        # Save file
        file_path = self.file_handler.save_uploaded_file(file_content, filename)
        
        try:
            # Extract text
            contract_text = self.file_handler.extract_text(file_path)
            
            # Run audit
            result = self.pipeline_service.audit_contract(contract_text)
            
            return result
        finally:
            if cleanup:
                self.file_handler.cleanup_file(file_path)
    
    def audit_from_text(self, contract_text: str) -> Dict[str, Any]:
        """
        Audit contract from text.
        
        Args:
            contract_text: Contract text content
        
        Returns:
            Audit result dictionary
        """
        return self.pipeline_service.audit_contract(contract_text)
