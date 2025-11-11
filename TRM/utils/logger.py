"""
Configuration du logging pour TRM Solver
"""
import logging
import sys


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure et retourne un logger pour l'application
    
    Args:
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configuré
    """
    # Configuration du format des logs
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configuration du handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(log_format))
    
    # Configuration du logger
    logger = logging.getLogger("trm_solver")
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.addHandler(handler)
    
    return logger