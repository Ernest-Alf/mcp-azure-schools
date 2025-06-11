"""
Validadores comunes para el sistema
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import pandas as pd
from ..config.settings import settings

def validate_excel_file(file_path: Path) -> Dict[str, Any]:
    """Valida un archivo Excel"""
    result = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "info": {}
    }
    
    try:
        # Verificar que existe
        if not file_path.exists():
            result["errors"].append(f"Archivo no existe: {file_path}")
            return result
        
        # Verificar extensión
        if file_path.suffix.lower() not in settings.excel.supported_extensions:
            result["errors"].append(f"Extensión no soportada: {file_path.suffix}")
            return result
        
        # Verificar tamaño
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > settings.excel.max_file_size_mb:
            result["errors"].append(f"Archivo muy grande: {size_mb:.2f}MB > {settings.excel.max_file_size_mb}MB")
            return result
        
        # Intentar leer archivo
        excel_file = pd.ExcelFile(file_path)
        
        result["info"] = {
            "size_mb": round(size_mb, 2),
            "sheets": excel_file.sheet_names,
            "total_sheets": len(excel_file.sheet_names)
        }
        
        result["valid"] = True
        
    except Exception as e:
        result["errors"].append(f"Error leyendo archivo: {str(e)}")
    
    return result

def validate_dataframe(df: pd.DataFrame, required_columns: Optional[List[str]] = None) -> Dict[str, Any]:
    """Valida un DataFrame"""
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "info": {}
    }
    
    # Información básica
    result["info"] = {
        "rows": len(df),
        "columns": len(df.columns),
        "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
    }
    
    # Verificar columnas requeridas
    if required_columns:
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            result["errors"].append(f"Columnas faltantes: {missing_columns}")
            result["valid"] = False
    
    # Verificar si está vacío
    if len(df) == 0:
        result["warnings"].append("DataFrame está vacío")
    
    # Verificar valores nulos
    null_counts = df.isnull().sum()
    high_null_columns = null_counts[null_counts > len(df) * 0.5].index.tolist()
    if high_null_columns:
        result["warnings"].append(f"Columnas con >50% nulos: {high_null_columns}")
    
    return result
