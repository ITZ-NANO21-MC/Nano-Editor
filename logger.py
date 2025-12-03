"""Logging system for NanoEditor."""
import logging
import os
from pathlib import Path
from typing import Optional

def setup_logger(name: str = "NanoEditor", level: Optional[int] = None) -> logging.Logger:
    """Setup and return configured logger."""
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    log_level = level or logging.INFO
    logger.setLevel(log_level)
    
    # Console handler
    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logger.addHandler(console)
    
    # File handler
    log_dir = Path.home() / '.nanoeditor' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_dir / 'nanoeditor.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    return logger

# Global logger instance
logger = setup_logger()
