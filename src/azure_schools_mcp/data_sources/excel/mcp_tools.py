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


def register_excel_tools(mcp_server: FastMCP):
    """Registra herramientas Excel mejoradas en el servidor MCP"""
    
    # Inicializar extractor con directorio base
    excel_dir = Path(__file__).parent.parent / "excel_files"
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
                    "modified": file_stat.st_mtime
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
        result = extractor.extract_all_data(filename)
        
        # Convertir DataFrames a dict para serialización
        if result.get("status") == "success" and "data" in result:
            for sheet_name, sheet_data in result["data"].items():
                if "dataframe" in sheet_data:
                    df = sheet_data["dataframe"]
                    sheet_data["dataframe"] = {
                        "columns": list(df.columns),
                        "rows": len(df),
                        "sample": df.head(5).to_dict('records')
                    }
                if "cleaned" in sheet_data:
                    cleaned_df = sheet_data["cleaned"]
                    sheet_data["cleaned"] = {
                        "columns": list(cleaned_df.columns),
                        "rows": len(cleaned_df),
                        "sample": cleaned_df.head(5).to_dict('records')
                    }
        
        return json.dumps(result, indent=2, ensure_ascii=False, default=str)
    
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
            
            df = result["data"][sheet_name]["cleaned"]
            
            if column not in df.columns:
                return json.dumps({
                    "status": "error",
                    "error": f"Columna '{column}' no encontrada",
                    "available_columns": list(df.columns)
                })
            
            unique_values = df[column].unique().tolist()
            
            response = {
                "status": "success",
                "filename": filename,
                "sheet": sheet_name,
                "column": column,
                "unique_values": [str(val) for val in unique_values if val is not None],
                "total_unique": len(unique_values),
                "null_count": df[column].isnull().sum()
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