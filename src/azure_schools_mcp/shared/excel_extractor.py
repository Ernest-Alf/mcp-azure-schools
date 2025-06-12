"""
Extractor centralizado de Excel - VERSIÓN CORREGIDA
Sin problemas de serialización JSON
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from ..config.settings import settings

class ExcelExtractor:
    def __init__(self):
        self.excel_dir = self._get_excel_directory()
        self.loaded_files = {}
    
    def _get_excel_directory(self) -> Path:
        current = Path(__file__).parent
        while current.parent != current:
            excel_dir = current.parent / "excel_files"
            if excel_dir.exists() or current.name == "mcp-azure-schools":
                return excel_dir
            current = current.parent
        excel_dir = Path.cwd() / "excel_files"
        excel_dir.mkdir(exist_ok=True)
        return excel_dir
    
    def _safe_serialize(self, obj):
        """Convierte objetos a tipos serializables"""
        if pd.isna(obj):
            return None
        elif hasattr(obj, 'item'):  # numpy types
            return obj.item()
        else:
            return str(obj)
    
    def list_excel_files(self) -> Dict[str, Any]:
        try:
            if not self.excel_dir.exists():
                self.excel_dir.mkdir(exist_ok=True)
                return {
                    "status": "directory_created",
                    "message": f"Directorio creado en: {self.excel_dir}"
                }
            
            excel_files = list(self.excel_dir.glob("*.xlsx")) + list(self.excel_dir.glob("*.xls"))
            
            if not excel_files:
                return {
                    "status": "no_files",
                    "directory": str(self.excel_dir),
                    "message": "No se encontraron archivos Excel"
                }
            
            file_list = []
            for file_path in excel_files:
                file_stat = file_path.stat()
                file_info = {
                    "name": file_path.name,
                    "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                    "modified": pd.Timestamp.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                }
                file_list.append(file_info)
            
            return {
                "status": "success",
                "directory": str(self.excel_dir),
                "total_files": len(file_list),
                "files": sorted(file_list, key=lambda x: x["modified"], reverse=True)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def extract_excel_data(self, filename: str, max_rows: int = 20, header_row: int = None) -> Dict[str, Any]:
        try:
            file_path = self.excel_dir / filename
            if not file_path.exists():
                return {"status": "error", "error": f"Archivo {filename} no encontrado"}
            
            # Auto-detectar header si no se especifica
            if header_row is None:
                header_row = self._detect_header_row(file_path)
            
            df = pd.read_excel(file_path, header=header_row, nrows=max_rows)
            df.columns = df.columns.astype(str).str.strip()
            
            # Convertir datos a tipos serializables
            sample_data = []
            for _, row in df.head(3).iterrows():
                row_dict = {}
                for col in df.columns:
                    row_dict[col] = self._safe_serialize(row[col])
                sample_data.append(row_dict)
            
            return {
                "status": "success",
                "filename": filename,
                "header_row_used": header_row + 1,
                "extraction_info": {
                    "rows_extracted": len(df),
                    "total_columns": len(df.columns)
                },
                "columns": list(df.columns),
                "data_sample": sample_data
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _detect_header_row(self, file_path: Path, max_check: int = 5) -> int:
        """Detecta automáticamente la fila de headers"""
        try:
            for row in range(max_check):
                df_test = pd.read_excel(file_path, header=row, nrows=2)
                if len(df_test.columns) > 1:
                    unnamed_count = sum(1 for col in df_test.columns if str(col).startswith('Unnamed'))
                    if unnamed_count / len(df_test.columns) < 0.3:  # Menos del 30% unnamed
                        return row
            return 0
        except:
            return 0

# Instancia global
_excel_extractor_instance = None

def get_excel_extractor():
    global _excel_extractor_instance
    if _excel_extractor_instance is None:
        _excel_extractor_instance = ExcelExtractor()
    return _excel_extractor_instance
