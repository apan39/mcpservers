"""Logging utilities for the MCP server."""

import logging
from typing import Optional

def setup_logger(name: str = "mcp_server", level: Optional[int] = None) -> logging.Logger:
    """Set up and configure a logger.
    
    Args:
        name: Name for the logger
        level: Logging level (defaults to INFO)
        
    Returns:
        Configured logger instance
    """
    if level is None:
        level = logging.INFO
        
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger