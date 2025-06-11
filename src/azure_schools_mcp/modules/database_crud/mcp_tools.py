"""
Database CRUD MCP Tools
Herramientas MCP para operaciones CRUD de base de datos
Ernest-Alf - Junio 2025
"""

import json
from mcp.server.fastmcp import FastMCP
from .database_manager import database_crud_manager

def register_database_crud_tools(mcp_server: FastMCP):
    """Registra herramientas MCP para operaciones CRUD de base de datos"""
    
    @mcp_server.tool()
    def import_excel_to_database(filename: str, table_name: str = "centros_trabajo_raw") -> str:
        """
        Importa datos de Excel a la base de datos Azure SQL
        
        Args:
            filename: Nombre del archivo Excel (ej: "Centro de trabajo (1).xlsx")
            table_name: Nombre de la tabla destino (default: "centros_trabajo_raw")
        """
        result = database_crud_manager.import_excel_to_database(filename, table_name)
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @mcp_server.tool()
    def create_educational_tables() -> str:
        """Crea las tablas educativas en la base de datos Azure SQL"""
        result = database_crud_manager.create_educational_tables()
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @mcp_server.tool()
    def query_schools_by_municipality(municipio: str = None) -> str:
        """
        Consulta centros educativos por municipio desde la base de datos
        
        Args:
            municipio: Nombre del municipio a consultar (opcional, si no se especifica lista todos)
        """
        result = database_crud_manager.query_schools_by_municipality(municipio)
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    return [import_excel_to_database, create_educational_tables, query_schools_by_municipality]
