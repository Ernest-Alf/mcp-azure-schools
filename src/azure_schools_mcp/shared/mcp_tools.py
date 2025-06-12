"""
Herramientas MCP centralizadas - Sin redundancia
Sistema Educativo MCP
Ernest-Alf - Junio 2025
"""

import json
from mcp.server.fastmcp import FastMCP
from .excel_extractor import get_excel_extractor
from typing import Dict, Any, Optional, List


def register_excel_tools(mcp_server: FastMCP):
    """Registra herramientas Excel centralizadas en el servidor MCP"""
    
    extractor = get_excel_extractor()
    
    @mcp_server.tool()
    def list_excel_files() -> str:
        """Lista todos los archivos Excel disponibles para análisis"""
        result = extractor.list_excel_files()
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @mcp_server.tool()
    def extract_excel_data(filename: str, max_rows: int = None, header_row: int = None) -> Dict[str, Any]:
        """
        Extrae datos de un archivo Excel específico con detección automática
        
        Args:
            filename: Nombre del archivo Excel
            max_rows: Máximo número de filas a extraer (default: 20)
            header_row: Fila donde están los headers (0=primera fila)
        """
        result = extractor.extract_excel_data(filename, max_rows, header_row)
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @mcp_server.tool() 
    def analyze_excel_structure(filename: str = None) -> str:
        """
        Analiza la estructura completa de archivos Excel
        
        Args:
            filename: Archivo específico a analizar (opcional)
        """
        result = extractor.analyze_excel_structure(filename)
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    return [list_excel_files, extract_excel_data, analyze_excel_structure]
