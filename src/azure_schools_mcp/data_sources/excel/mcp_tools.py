"""
Herramientas MCP centralizadas - Con ExcelExtractor mejorado
Sistema Educativo MCP
Ernest-Alf - Junio 2025
"""

import json
from mcp.server.fastmcp import FastMCP
from azure_schools_mcp.data_sources.excel.excel_extractor import ExcelExtractor
from pathlib import Path
from typing import Dict, Any, Optional, List
from azure_schools_mcp.utils.json_helpers import safe_json_response
import pandas as pd

def register_excel_tools(mcp_server: FastMCP):
    """Registra herramientas Excel mejoradas en el servidor MCP"""
    
    # Inicializar extractor con directorio base
    excel_dir = Path(__file__).parent.parent.parent.parent.parent / "excel_files"
    extractor = ExcelExtractor(excel_dir)
    
    @mcp_server.tool()
    def list_excel_files() -> str:
        """Lista todos los archivos Excel disponibles para análisis"""
        try:
            excel_files = list(excel_dir.glob("*.xlsx")) + list(excel_dir.glob("*.xls"))
            
            file_list = []
            for file_path in excel_files:
                file_stat = file_path.stat()
                file_info = {
                    "name": file_path.name,
                    "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
                    "modified": int(file_stat.st_mtime)  # Convertir timestamp a entero
                }
                file_list.append(file_info)
            
            result = {
                "status": "success",
                "directory": str(excel_dir),
                "total_files": len(file_list),
                "files": file_list
            }
            
        except Exception as e:
            result = {"status": "error", "error": str(e)}
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @mcp_server.tool()
    def extract_excel_complete(filename: str) -> str:
        """
        Extrae y valida completamente un archivo Excel con limpieza de datos
        
        Args:
            filename: Nombre del archivo Excel
        """

        import json
        
        try:
            file_path = extractor.excel_dir / filename
            
            # Determinar engine basado en extensión
            if filename.lower().endswith('.xls'):
                engine = 'xlrd'
            elif filename.lower().endswith('.xlsx'):
                engine = 'openpyxl'
            else:
                engine = None
            
            # Leer todas las hojas
            try:
                if engine:
                    all_sheets = pd.read_excel(file_path, sheet_name=None, engine=engine)
                else:
                    all_sheets = pd.read_excel(file_path, sheet_name=None)
            except Exception as e:
                return json.dumps({
                    "status": "error",
                    "error": f"Error leyendo archivo: {str(e)}"
                })
            
            # Resto del código permanece igual...
            result = extractor.extract_all_data(filename)
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "status": "error", 
                "error": str(e)
            }, indent=2, ensure_ascii=False)
    
    @mcp_server.tool()
    def get_unique_values(filename: str, column: str, sheet_name: str = None) -> str:
        """
        Extrae valores únicos de una columna específica
        
        Args:
            filename: Nombre del archivo Excel
            column: Nombre de la columna
            sheet_name: Nombre de la hoja (opcional, usa la primera válida)
        """
        try:
            result = extractor.extract_all_data(filename)
            
            if result.get("status") != "success":
                return json.dumps(result)
            
            # Seleccionar hoja
            if sheet_name is None:
                sheet_name = next(iter(result["data"].keys()))
            
            if sheet_name not in result["data"]:
                return json.dumps({
                    "status": "error", 
                    "error": f"Hoja '{sheet_name}' no encontrada"
                })
            
            # Obtener datos limpios y crear DataFrame
            sheet_data = result["data"][sheet_name]["cleaned"]
            
            if isinstance(sheet_data, dict):
                # Los datos están serializados como diccionario
                if "sample" in sheet_data:
                    # Usar muestra de datos
                    df = pd.DataFrame(sheet_data["sample"])
                else:
                    # Recargar archivo completo
                    df = pd.read_excel(extractor.excel_dir / filename, sheet_name=sheet_name)
            else:
                # sheet_data ya es un DataFrame
                df = sheet_data
            
            if column not in df.columns:
                return json.dumps({
                    "status": "error",
                    "error": f"Columna '{column}' no encontrada",
                    "available_columns": list(df.columns)
                })
            
            # Obtener valores únicos y convertir a tipos serializables
            unique_values = df[column].dropna().unique()
            unique_values_serializable = []
            
            for val in unique_values:
                if pd.isna(val):
                    continue
                # Convertir tipos numpy/pandas a tipos Python nativos
                if hasattr(val, 'item'):
                    unique_values_serializable.append(val.item())
                else:
                    unique_values_serializable.append(val)
            
            response = {
                "status": "success",
                "filename": filename,
                "sheet": sheet_name,
                "column": column,
                "unique_values": unique_values_serializable,
                "total_unique": len(unique_values_serializable),
                "null_count": int(df[column].isnull().sum())
            }
            
        except Exception as e:
            response = {"status": "error", "error": str(e)}
        
        return json.dumps(response, indent=2, ensure_ascii=False)
    
    @mcp_server.tool()
    def filter_by_value(filename: str, column: str, value: str, sheet_name: str = None) -> str:
        """
        Filtra datos por valor específico en una columna
        
        Args:
            filename: Nombre del archivo Excel
            column: Columna a filtrar
            value: Valor a buscar
            sheet_name: Hoja específica (opcional)
        """
        try:
            result = extractor.extract_all_data(filename)
            
            if result.get("status") != "success":
                return json.dumps(result)
            
            # Seleccionar hoja
            if sheet_name is None:
                sheet_name = next(iter(result["data"].keys()))
            
            df = result["data"][sheet_name]["cleaned"]
            filtered_df = df[df[column] == value]
            
            response = {
                "status": "success",
                "filename": filename,
                "sheet": sheet_name,
                "filter": f"{column} = {value}",
                "total_matches": len(filtered_df),
                "data": filtered_df.to_dict('records')
            }
            
        except Exception as e:
            response = {"status": "error", "error": str(e)}
        
        return json.dumps(response, indent=2, ensure_ascii=False, default=str)
    
    return [list_excel_files, extract_excel_complete, get_unique_values, filter_by_value]