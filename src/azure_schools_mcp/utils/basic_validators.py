"""
Validadores básicos y flexibles - Sin restricciones rígidas
Sistema Educativo MCP
"""

from pathlib import Path
from typing import Dict, Any
import pandas as pd
from .logger import SimpleLogger

logger = SimpleLogger.get_logger("validators")

def validate_excel_file_basic(file_path: Path) -> Dict[str, Any]:
    """Validación básica de archivo Excel - Solo lo esencial"""
    
    result = {
        "valid": False,
        "error": None,
        "info": {}
    }
    
    try:
        # Solo verificar lo básico
        if not file_path.exists():
            result["error"] = f"Archivo no existe: {file_path}"
            logger.error(result["error"])
            return result
        
        if file_path.suffix.lower() not in ['.xlsx', '.xls', '.xlsm']:
            result["error"] = f"No es un archivo Excel: {file_path.suffix}"
            logger.warning(result["error"])
            return result
        
        # Verificar que se puede leer
        excel_file = pd.ExcelFile(file_path)
        
        result["info"] = {
            "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
            "sheets": excel_file.sheet_names,
            "total_sheets": len(excel_file.sheet_names),
            "readable": True
        }
        
        result["valid"] = True
        logger.debug(f"Archivo Excel válido: {file_path.name}")
        
    except Exception as e:
        result["error"] = f"Error leyendo Excel: {str(e)}"
        logger.error(result["error"])
    
    return result

def check_dataframe_basic(df: pd.DataFrame) -> Dict[str, Any]:
    """Información básica de DataFrame - Sin validaciones rígidas"""
    
    info = {
        "rows": len(df),
        "columns": len(df.columns),
        "empty": len(df) == 0,
        "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
        "column_names": list(df.columns),
        "has_data": len(df) > 0 and len(df.columns) > 0
    }
    
    logger.debug(f"DataFrame info: {info['rows']} filas, {info['columns']} columnas")
    return info

def is_file_readable(file_path: Path) -> bool:
    """Verifica si un archivo es legible"""
    try:
        return file_path.exists() and file_path.is_file() and file_path.stat().st_size > 0
    except Exception:
        return False
