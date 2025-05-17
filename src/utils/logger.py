"""
Logger Utility

Provides consistent logging functionality throughout the application.
"""

import logging
from pathlib import Path
import sys
from datetime import datetime

def setup_logger(name: str) -> logging.Logger:
    """
    Set up and return a logger with consistent formatting
    
    Args:
        name: Logger name (typically __name__ from the calling module)
        
    Returns:
        Configured Logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create a logger
    logger = logging.getLogger(name)
    
    # Only configure if it hasn't been configured already
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create a formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create file handler for logging to a file
        today = datetime.now().strftime('%Y-%m-%d')
        file_handler = logging.FileHandler(logs_dir / f'resume_optimizer_{today}.log')
        file_handler.setFormatter(formatter)
        
        # Create console handler for logging to console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger
