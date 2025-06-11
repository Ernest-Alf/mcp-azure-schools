"""
Excel Extraction Tools - Sistema Educativo MCP
Herramientas simplificadas para extracción de datos Excel
Ernest-Alf - Junio 2025
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

class ExcelExtractor:
    """Extractor simplificado de datos Excel"""
    
    def __init__(self):
        self.excel_dir = Path(__file__).parent.parent.parent.parent.parent / "excel_files"
        self.loaded_files = {}
    
    def list_excel_files(self) -> Dict[str, Any]:
        """Lista archivos Excel disponibles"""
        try:
            if not self.excel_dir.exists():
                self.excel_dir.mkdir(exist_ok=True)
                return {"error": "Directorio excel_files creado - agregar archivos Excel"}
            
            excel_files = list(self.excel_dir.glob("*.xlsx"))
            
            file_list = []
            for file_path in excel_files:
                file_stat = file_path.stat()
                file_info = {
                    "name": file_path.name,
                    "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                    "modified": pd.Timestamp.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                }
                file_list.append(file_info)
            
            return {
                "directory": str(self.excel_dir),
                "total_files": len(file_list),
                "files": sorted(file_list, key=lambda x: x['modified'], reverse=True)
            }
        except Exception as e:
            return {"error": f"Error listando archivos: {str(e)}"}
    
    def extract_excel_data(self, filename: str, max_rows: int = 20, header_row: int = 0) -> Dict[str, Any]:
        """Extrae datos de un archivo Excel"""
        try:
            file_path = self.excel_dir / filename
            if not file_path.exists():
                return {"error": f"Archivo {filename} no encontrado"}
            
            # Leer archivo Excel
            df = pd.read_excel(file_path, header=header_row, nrows=max_rows)
            df.columns = df.columns.str.strip()
            
            # Guardar en memoria para análisis posterior
            self.loaded_files[filename] = {
                "data": df,
                "loaded_at": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Detectar columnas educativas importantes
            educational_columns = {}
            for col in df.columns:
                col_lower = col.lower()
                if 'nivel' in col_lower and 'educativo' in col_lower:
                    educational_columns['nivel_educativo'] = col
                elif 'municipio' in col_lower:
                    educational_columns['municipio'] = col
                elif 'matrícula' in col_lower or 'matricula' in col_lower:
                    educational_columns['matricula'] = col
                elif 'sostenimiento' in col_lower:
                    educational_columns['sostenimiento'] = col
                elif 'nombre' in col_lower and 'centro' in col_lower:
                    educational_columns['nombre_centro'] = col
            
            # Análisis básico automático
            analysis = {}
            if educational_columns.get('municipio'):
                municipios = df[educational_columns['municipio']].value_counts().head(10).to_dict()
                analysis['municipios'] = municipios
            
            if educational_columns.get('nivel_educativo'):
                niveles = df[educational_columns['nivel_educativo']].value_counts().to_dict()
                analysis['niveles_educativos'] = niveles
            
            return {
                "filename": filename,
                "extraction_successful": True,
                "dimensions": {
                    "rows_extracted": len(df),
                    "total_columns": len(df.columns)
                },
                "columns": list(df.columns),
                "educational_columns_detected": educational_columns,
                "data_sample": df.head(3).to_dict(orient="records"),
                "automatic_analysis": analysis,
                "loaded_in_memory": True,
                "next_steps": [
                    "Usar analyze_excel_structure() para análisis detallado",
                    "Datos listos para análisis por municipio/nivel",
                    "Disponible para importación a Azure SQL"
                ]
            }
        except Exception as e:
            return {"error": f"Error extrayendo datos: {str(e)}"}
    
    def analyze_excel_structure(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """Analiza la estructura de un archivo Excel"""
        try:
            if filename:
                file_path = self.excel_dir / filename
                if not file_path.exists():
                    return {"error": f"Archivo {filename} no encontrado"}
                
                # Leer archivo completo para análisis
                excel_file = pd.ExcelFile(file_path)
                
                structure_analysis = {
                    "filename": filename,
                    "total_sheets": len(excel_file.sheet_names),
                    "sheet_names": excel_file.sheet_names,
                    "sheets_analysis": {}
                }
                
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    structure_analysis["sheets_analysis"][sheet_name] = {
                        "rows": len(df),
                        "columns": len(df.columns),
                        "column_names": list(df.columns),
                        "data_types": df.dtypes.astype(str).to_dict(),
                        "null_values": df.isnull().sum().to_dict()
                    }
                
                return structure_analysis
            
            else:
                # Analizar archivos cargados en memoria
                if not self.loaded_files:
                    return {"message": "No hay archivos cargados. Usa extract_excel_data() primero"}
                
                memory_analysis = {
                    "loaded_files_count": len(self.loaded_files),
                    "files_in_memory": {}
                }
                
                for filename, file_data in self.loaded_files.items():
                    df = file_data["data"]
                    memory_analysis["files_in_memory"][filename] = {
                        "loaded_at": file_data["loaded_at"],
                        "rows": len(df),
                        "columns": len(df.columns),
                        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024*1024), 2)
                    }
                
                return memory_analysis
                
        except Exception as e:
            return {"error": f"Error analizando estructura: {str(e)}"}

# Instancia global del extractor
excel_extractor = ExcelExtractor()

def register_excel_tools(mcp_server: FastMCP):
    """Registra herramientas de extracción Excel en el servidor MCP"""
    
    @mcp_server.tool()
    def list_excel_files() -> str:
        """Lista todos los archivos Excel disponibles para análisis"""
        result = excel_extractor.list_excel_files()
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @mcp_server.tool()
    def extract_excel_data(filename: str, max_rows: int = 20, header_row: int = 0) -> str:
        """
        Extrae datos de un archivo Excel específico
        
        Args:
            filename: Nombre del archivo Excel (ej: "Centro de trabajo (1).xlsx")
            max_rows: Máximo número de filas a extraer (default: 20)
            header_row: Fila donde están los headers (0=primera fila, 2=tercera fila)
        """
        result = excel_extractor.extract_excel_data(filename, max_rows, header_row)
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @mcp_server.tool() 
    def analyze_excel_structure(filename: str = None) -> str:
        """
        Analiza la estructura completa de un archivo Excel
        
        Args:
            filename: Archivo específico a analizar (opcional)
        """
        result = excel_extractor.analyze_excel_structure(filename)
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    return [list_excel_files, extract_excel_data, analyze_excel_structure]
