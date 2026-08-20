"""
Logging utility for the Crime Scene Reconstruction System
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from config import LOGGING_CONFIG

def setup_logger(name: str, log_file: str = None, level: str = None):
    """
    Set up a logger with console and file handlers
    
    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set level
    log_level = getattr(logging, (level or LOGGING_CONFIG['level']).upper())
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(LOGGING_CONFIG['format'])
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file or LOGGING_CONFIG.get('log_file'):
        file_path = Path(log_file) if log_file else LOGGING_CONFIG['log_file']
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(LOGGING_CONFIG['format'])
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def log_processing_step(logger, step_name: str, case_id: str, details: dict = None):
    """
    Log a processing step with structured information
    
    Args:
        logger: Logger instance
        step_name: Name of the processing step
        case_id: Case/session identifier
        details: Additional details dictionary
    """
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'case_id': case_id,
        'step': step_name,
        'details': details or {}
    }
    logger.info(f"Processing Step: {log_data}")

def log_error(logger, error: Exception, context: str = None):
    """
    Log an error with context
    
    Args:
        logger: Logger instance
        error: Exception object
        context: Additional context information
    """
    error_data = {
        'timestamp': datetime.now().isoformat(),
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context
    }
    logger.error(f"Error occurred: {error_data}", exc_info=True)

# Create default application logger
app_logger = setup_logger('crime_scene_app')
