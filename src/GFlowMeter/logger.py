import logging
from pathlib import Path
from typing import Optional


def setup_logger(name: str = 'GFlowMeter', log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up and configure the logger for GFlowMeter.
    
    Args:
        name: Logger name (default: 'GFlowMeter')
        log_level: Logging level (default: logging.INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(log_level)
    
    # Create logs directory in project root
    # Get project root (assuming this file is in src/GFlowMeter/)
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    logs_dir = project_root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Use a single log file (append mode)
    log_file = logs_dir / 'gflowmeter.log'
    
    # File handler - logs everything (append mode)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Console handler - only logs ERROR and CRITICAL to keep console clean for tqdm
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)  # Only show errors in console
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log initialization to file only (not console)
    logger.debug(f"Logger initialized. Log file: {log_file}")
    
    return logger


def get_logger(name: str = 'GFlowMeter') -> logging.Logger:
    """
    Get an existing logger instance or create a new one.
    
    Args:
        name: Logger name (default: 'GFlowMeter')
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger

