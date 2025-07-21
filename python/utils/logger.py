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
    import os
    
    if level is None:
        env_level = os.getenv("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, env_level, logging.INFO)
        
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
        
    logger.setLevel(level)
    
    # Create console handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger