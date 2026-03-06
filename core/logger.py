"""
Unified logging service.
Provides consistent logging configuration and formatting across the application.
"""
import logging
from pathlib import Path
from typing import Optional
from functools import lru_cache


class LoggerFactory:
    """Factory for creating configured loggers."""
    
    _log_dir: Optional[Path] = None
    _configured: bool = False
    
    @classmethod
    def setup(cls, log_dir: Optional[Path] = None):
        """Setup logging directory."""
        if log_dir is None:
            from .config_manager import get_config_manager
            config = get_config_manager()
            log_dir = config.project_root / "outputs" / "logs"
        
        log_dir.mkdir(parents=True, exist_ok=True)
        cls._log_dir = log_dir
        cls._configured = True
    
    @classmethod
    def get_logger(cls, name: str, level: int = logging.INFO) -> logging.Logger:
        """Get a configured logger for the given name."""
        if not cls._configured:
            cls.setup()
        
        logger = logging.getLogger(name)
        
        # Avoid adding duplicate handlers
        if logger.handlers:
            return logger
        
        logger.setLevel(level)
        
        # File handler
        if cls._log_dir:
            log_file = cls._log_dir / f"agent_{name}.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(level)
            
            formatter = logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Console handler (optional, for development)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger


@lru_cache()
def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get a configured logger instance."""
    return LoggerFactory.get_logger(name, level)
