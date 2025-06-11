"""
Sistema de logging centralizado
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from ..config.settings import settings

def setup_logger(
    name: str = "azure_schools_mcp",
    log_file: Optional[str] = None,
    level: Optional[str] = None
) -> logging.Logger:
    """Configura y retorna un logger"""
    
    # Nivel de logging
    log_level = level or settings.system.log_level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Evitar duplicar handlers
    if logger.handlers:
        return logger
    
    # Formato de mensajes
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (opcional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Logger principal del sistema
main_logger = setup_logger()
