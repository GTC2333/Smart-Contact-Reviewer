"""
File handling utilities for uploads and temporary files.
"""
import shutil
from pathlib import Path
from typing import Optional
from tempfile import NamedTemporaryFile
import contextlib

from core.config_manager import get_config_manager
from core.logger import get_logger
from .text_preprocess import extract_text_from_file


class FileHandler:
    """Handler for file operations."""
    
    SUPPORTED_EXTENSIONS = {'.txt', '.pdf', '.docx'}
    
    def __init__(self, upload_dir: Optional[Path] = None):
        """
        Initialize file handler.
        
        Args:
            upload_dir: Upload directory (defaults to project uploads/)
        """
        self.config = get_config_manager()
        if upload_dir is None:
            upload_dir = self.config.project_root / "uploads"
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(self.__class__.__name__)
    
    def validate_file_type(self, filename: str) -> bool:
        """
        Validate if file type is supported.
        
        Args:
            filename: File name with extension
        
        Returns:
            True if file type is supported
        """
        suffix = Path(filename).suffix.lower()
        return suffix in self.SUPPORTED_EXTENSIONS
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> Path:
        """
        Save uploaded file to upload directory.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
        
        Returns:
            Path to saved file
        """
        if not self.validate_file_type(filename):
            raise ValueError(f"Unsupported file type: {filename}")
        
        file_path = self.upload_dir / filename
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        self.logger.info(f"Saved uploaded file: {file_path}")
        return file_path
    
    def extract_text(self, file_path: Path) -> str:
        """
        Extract text from file.
        
        Args:
            file_path: Path to file
        
        Returns:
            Extracted text content
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.logger.info(f"Extracting text from: {file_path}")
        try:
            return extract_text_from_file(str(file_path))
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            raise
    
    def cleanup_file(self, file_path: Path):
        """
        Delete a file.
        
        Args:
            file_path: Path to file to delete
        """
        try:
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            self.logger.warning(f"Failed to cleanup file {file_path}: {e}")
    
    @contextlib.contextmanager
    def temporary_file(self, content: bytes, suffix: str = ".tmp"):
        """
        Context manager for temporary file.
        
        Args:
            content: File content
            suffix: File suffix
        
        Yields:
            Path to temporary file
        """
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)
        
        try:
            yield tmp_path
        finally:
            self.cleanup_file(tmp_path)
