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
            
            df = pd.read_excel(file_path, header=header_row, nrows=max_rows if max_rows is not None else None)
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
    
    def analyze_excel_structure(self, filename: str = None) -> Dict[str, Any]:
        """Analiza estructura completa de archivos Excel"""
        try:
            if filename:
                return self._analyze_specific_file(filename)
            else:
                return self._analyze_loaded_files()
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _analyze_specific_file(self, filename: str) -> Dict[str, Any]:
        """Analiza un archivo específico con detección inteligente de headers"""
        file_path = self.excel_dir / filename
        if not file_path.exists():
            return {"status": "error", "error": f"Archivo {filename} no encontrado"}
        
        try:
            excel_file = pd.ExcelFile(file_path)
            
            result = {
                "status": "success",
                "filename": filename,
                "total_sheets": len(excel_file.sheet_names),
                "sheets": {}
            }
            
            for sheet_name in excel_file.sheet_names:
                # Detectar header automáticamente para esta hoja
                detected_header_row = self._detect_header_row_for_sheet(file_path, sheet_name)
                
                # Leer con header detectado
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=detected_header_row)
                
                # Información de la hoja
                sheet_info = {
                    "detected_header_row": detected_header_row + 1,  # Para mostrar fila real (1-based)
                    "total_columns": len(df.columns),
                    "columns": list(df.columns),
                    "sample_data_rows": len(df),
                    "column_analysis": {}
                }
                
                # Análisis de cada columna
                for col in df.columns:
                    col_analysis = {
                        "has_data": not df[col].isna().all(),
                        "unique_values": int(df[col].nunique()) if not df[col].isna().all() else 0,
                        "sample_values": [self._safe_serialize(val) for val in df[col].dropna().head(3).tolist()]
                    }
                    sheet_info["column_analysis"][col] = col_analysis
                
                result["sheets"][sheet_name] = sheet_info
            
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _detect_header_row_for_sheet(self, file_path: Path, sheet_name: str, max_check: int = 5) -> int:
        """Detecta header específicamente para una hoja"""
        try:
            for row in range(max_check):
                df_test = pd.read_excel(file_path, sheet_name=sheet_name, header=row, nrows=3)
                if len(df_test.columns) > 1:
                    # Verificar que no sean muchas columnas "Unnamed"
                    unnamed_count = sum(1 for col in df_test.columns if str(col).startswith('Unnamed'))
                    if unnamed_count / len(df_test.columns) < 0.3:  # Menos del 30% unnamed
                        return row
            return 0
        except:
            return 0
    
    def _analyze_loaded_files(self) -> Dict[str, Any]:
        """Analiza archivos cargados en memoria"""
        if not self.loaded_files:
            return {
                "status": "no_data",
                "message": "No hay archivos cargados en memoria"
            }
        
        return {
            "status": "success",
            "loaded_files": len(self.loaded_files),
            "files": list(self.loaded_files.keys())
        }

# Instancia global
_excel_extractor_instance = None

def get_excel_extractor():
    global _excel_extractor_instance
    if _excel_extractor_instance is None:
        _excel_extractor_instance = ExcelExtractor()
    return _excel_extractor_instance
