"""
Sistema de logging simple y efectivo
Sistema Educativo MCP
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

class SimpleLogger:
    """Logger simple para MCP"""
    
    @staticmethod
    def setup(name: str = "mcp", level: str = "INFO") -> logging.Logger:
        """Configura un logger simple"""
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Evitar duplicar handlers
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @staticmethod
    def get_logger(module_name: str, level: str = "INFO") -> logging.Logger:
        """Obtiene un logger para un módulo específico"""
        return SimpleLogger.setup(f"mcp.{module_name}", level)

# Loggers principales del sistema
main_logger = SimpleLogger.setup("mcp")
excel_logger = SimpleLogger.setup("mcp.excel")
database_logger = SimpleLogger.setup("mcp.database")
server_logger = SimpleLogger.setup("mcp.server")
