"""
Gestor de archivos Excel - Módulo Excel Tools
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
from ...config.settings import settings
from ...utils.logger import setup_logger
from ...utils.validators import validate_excel_file

logger = setup_logger("excel_tools.file_manager")

class ExcelFileManager:
    """Gestor de archivos Excel con funcionalidades avanzadas"""
    
    def __init__(self):
        self.excel_dir = Path(__file__).parent.parent.parent.parent.parent / "excel_files"
        self.loaded_files: Dict[str, pd.DataFrame] = {}
        self.file_metadata: Dict[str, Dict[str, Any]] = {}
    
    def list_excel_files(self) -> Dict[str, Any]:
        """Lista archivos Excel con información detallada"""
        try:
            # Crear directorio si no existe
            self.excel_dir.mkdir(exist_ok=True)
            
            excel_files = []
            total_size = 0
            
            for ext in settings.excel.supported_extensions:
                excel_files.extend(self.excel_dir.glob(f"*{ext}"))
            
            if not excel_files:
                return {
                    "status": "empty",
                    "message": "No se encontraron archivos Excel",
                    "directory": str(self.excel_dir),
                    "total_files": 0,
                    "suggestion": "Coloca archivos .xlsx en la carpeta excel_files/"
                }
            
            file_list = []
            for file_path in excel_files:
                file_stat = file_path.stat()
                size_mb = file_stat.st_size / (1024 * 1024)
                total_size += size_mb
                
                # Validar archivo
                validation = validate_excel_file(file_path)
                
                file_info = {
                    "name": file_path.name,
                    "size_mb": round(size_mb, 2),
                    "modified": pd.Timestamp.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    "extension": file_path.suffix.lower(),
                    "valid": validation["valid"],
                    "status": "✅ Válido" if validation["valid"] else "❌ Error"
                }
                
                if not validation["valid"]:
                    file_info["errors"] = validation["errors"]
                
                file_list.append(file_info)
            
            # Ordenar por fecha de modificación
            file_list.sort(key=lambda x: x['modified'], reverse=True)
            
            return {
                "status": "success",
                "directory": str(self.excel_dir),
                "total_files": len(file_list),
                "total_size_mb": round(total_size, 2),
                "files": file_list,
                "metadata": {
                    "supported_extensions": settings.excel.supported_extensions,
                    "max_file_size_mb": settings.excel.max_file_size_mb
                }
            }
            
        except Exception as e:
            logger.error(f"Error listando archivos Excel: {e}")
            return {
                "status": "error",
                "error": str(e),
                "directory": str(self.excel_dir)
            }
    
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """Obtiene información detallada de un archivo Excel específico"""
        try:
            file_path = self.excel_dir / filename
            
            if not file_path.exists():
                available_files = [f.name for f in self.excel_dir.glob("*.xlsx")]
                return {
                    "status": "not_found",
                    "error": f"Archivo '{filename}' no encontrado",
                    "available_files": available_files
                }
            
            # Validar archivo
            validation = validate_excel_file(file_path)
            if not validation["valid"]:
                return {
                    "status": "invalid",
                    "errors": validation["errors"],
                    "warnings": validation.get("warnings", [])
                }
            
            # Leer información del archivo
            excel_file = pd.ExcelFile(file_path)
            file_stat = file_path.stat()
            
            # Información de hojas
            sheets_info = {}
            for sheet_name in excel_file.sheet_names:
                try:
                    df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)  # Solo headers
                    sheets_info[sheet_name] = {
                        "columns": list(df.columns),
                        "column_count": len(df.columns)
                    }
                    
                    # Obtener número de filas sin cargar todo
                    df_sample = pd.read_excel(file_path, sheet_name=sheet_name)
                    sheets_info[sheet_name]["rows"] = len(df_sample)
                    sheets_info[sheet_name]["estimated_memory_mb"] = round(
                        df_sample.memory_usage(deep=True).sum() / (1024 * 1024), 2
                    )
                    
                except Exception as e:
                    sheets_info[sheet_name] = {
                        "error": f"Error leyendo hoja: {str(e)}"
                    }
            
            return {
                "status": "success",
                "file_info": {
                    "name": filename,
                    "path": str(file_path),
                    "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                    "modified": pd.Timestamp.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    "sheets": {
                        "count": len(excel_file.sheet_names),
                        "names": excel_file.sheet_names,
                        "details": sheets_info
                    }
                },
                "validation": validation
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo info del archivo {filename}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def read_excel_file(self, filename: str, sheet_name: Optional[str] = None, 
                       max_rows: int = 10, header_row: int = 0) -> Dict[str, Any]:
        """Lee contenido de archivo Excel con configuración flexible"""
        try:
            file_path = self.excel_dir / filename
            
            if not file_path.exists():
                available_files = [f.name for f in self.excel_dir.glob("*.xlsx")]
                return {
                    "status": "not_found",
                    "error": f"Archivo '{filename}' no encontrado",
                    "available_files": available_files
                }
            
            # Leer archivo Excel
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row, nrows=max_rows)
            else:
                df = pd.read_excel(file_path, header=header_row, nrows=max_rows)
            
            # Limpiar nombres de columnas
            df.columns = df.columns.str.strip()
            
            # Guardar en memoria para uso posterior
            cache_key = f"{filename}_{sheet_name or 'default'}_{header_row}"
            self.loaded_files[cache_key] = df.copy()
            
            return {
                "status": "success",
                "file_data": {
                    "filename": filename,
                    "sheet": sheet_name or "primera_hoja",
                    "header_row": header_row,
                    "rows_loaded": len(df),
                    "columns": list(df.columns),
                    "column_count": len(df.columns),
                    "data": df.to_dict(orient="records"),
                    "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                    "cached_as": cache_key
                },
                "metadata": {
                    "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
                    "null_counts": df.isnull().sum().to_dict(),
                    "sample_data": df.head(2).to_dict(orient="records") if len(df) > 0 else []
                }
            }
            
        except Exception as e:
            logger.error(f"Error leyendo archivo Excel {filename}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "details": f"Error específico: {type(e).__name__}"
            }
    
    def get_loaded_files(self) -> Dict[str, Any]:
        """Lista archivos cargados en memoria"""
        if not self.loaded_files:
            return {
                "status": "empty",
                "message": "No hay archivos cargados en memoria",
                "suggestion": "Usa read_excel_file() para cargar archivos"
            }
        
        loaded_info = []
        total_memory = 0
        
        for cache_key, df in self.loaded_files.items():
            memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
            total_memory += memory_mb
            
            loaded_info.append({
                "cache_key": cache_key,
                "rows": len(df),
                "columns": len(df.columns),
                "memory_mb": round(memory_mb, 2),
                "column_names": list(df.columns)[:5]  # Primeras 5 columnas
            })
        
        return {
            "status": "success",
            "total_loaded": len(self.loaded_files),
            "total_memory_mb": round(total_memory, 2),
            "loaded_files": loaded_info,
            "available_operations": [
                "excel_summary()",
                "schools_data_analysis()",
                "custom_analysis()"
            ]
        }
    def get_excel_file_info(self, filename: str) -> str:
        """Obtiene información de un archivo Excel (retorna JSON string)"""
        result = self.get_file_info(filename)  # Este puede devolver dict
        
        # Si es dict, convertir a JSON string
        if isinstance(result, dict):
            import json
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        # Si ya es string, devolverlo tal como está
        return result


    def list_loaded_excel_files(self) -> dict:
        """Lista archivos Excel cargados en memoria"""
        loaded_files = []
        for filename, metadata in self.file_metadata.items():
            if metadata.get('loaded', False):
                loaded_files.append({
                    'filename': filename,
                    'loaded_at': metadata.get('loaded_at', 'Unknown'),
                    'size_mb': metadata.get('size_mb', 0),
                    'rows': metadata.get('rows', 0),
                    'columns': metadata.get('columns', 0)
                })
        
        return {
            'total_loaded': len(loaded_files),
            'loaded_files': loaded_files
        }


# Instancia global del gestor
excel_file_manager = ExcelFileManager()
