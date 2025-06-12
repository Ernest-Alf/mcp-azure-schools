"""
Utilidades básicas para manejo de archivos
Sistema Educativo MCP
"""

from pathlib import Path
from typing import Dict, Any, List
import shutil
from .logger import SimpleLogger

logger = SimpleLogger.get_logger("file_helpers")

class FileManager:
    """Gestor básico de archivos"""
    
    @staticmethod
    def ensure_directory(path: Path) -> bool:
        """Asegura que un directorio exista"""
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directorio asegurado: {path}")
            return True
        except Exception as e:
            logger.error(f"Error creando directorio {path}: {e}")
            return False
    
    @staticmethod
    def get_file_info(file_path: Path) -> Dict[str, Any]:
        """Información básica de un archivo"""
        try:
            if not file_path.exists():
                return {"exists": False}
            
            stat = file_path.stat()
            return {
                "exists": True,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "extension": file_path.suffix.lower(),
                "name": file_path.name,
                "readable": file_path.is_file()
            }
        except Exception as e:
            logger.error(f"Error obteniendo info de {file_path}: {e}")
            return {"exists": False, "error": str(e)}
    
    @staticmethod
    def list_excel_files(directory: Path) -> List[Path]:
        """Lista archivos Excel en un directorio"""
        try:
            if not directory.exists():
                return []
            
            excel_extensions = ['.xlsx', '.xls', '.xlsm']
            excel_files = []
            
            for ext in excel_extensions:
                excel_files.extend(directory.glob(f"*{ext}"))
            
            logger.debug(f"Encontrados {len(excel_files)} archivos Excel en {directory}")
            return sorted(excel_files)
            
        except Exception as e:
            logger.error(f"Error listando archivos en {directory}: {e}")
            return []
