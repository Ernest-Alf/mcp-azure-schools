"""
Database Management MCP Tools
Herramientas MCP para gestión de base de datos
Ernest-Alf - Junio 2025
"""

import json
from mcp.server.fastmcp import FastMCP
from .schema_registry import schema_registry
from .table_inspector import table_inspector
from .crud_generator import crud_generator

def register_database_management_tools(mcp_server: FastMCP):
    """Registra herramientas MCP para gestión de base de datos"""
    
    @mcp_server.tool()
    def discover_database_schema() -> str:
        """
        Descubre y documenta el esquema completo de la base de datos
        Útil para entender la estructura actual y generar herramientas automáticamente
        """
        result = table_inspector.discover_schema()
        
        # Registrar en schema registry
        if "tables" in result:
            for table_name, table_schema in result["tables"].items():
                schema_registry.register_table_schema(table_schema)
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @mcp_server.tool()
    def get_table_documentation(table_name: str) -> str:
        """
        Obtiene documentación detallada de una tabla específica
        
        Args:
            table_name: Nombre de la tabla a documentar
        """
        table_schema = schema_registry.get_table_schema(table_name)
        
        if not table_schema:
            # Intentar descubrir la tabla
            structure = table_inspector.get_table_structure(table_name)
            if "error" not in structure:
                schema_registry.register_table_schema(structure)
                table_schema = structure
        
        return json.dumps(table_schema, indent=2, ensure_ascii=False)
    
    @mcp_server.tool()
    def generate_crud_operations(table_name: str) -> str:
        """
        Genera operaciones CRUD automáticamente para una tabla
        
        Args:
            table_name: Nombre de la tabla para generar CRUD
        """
        # Obtener esquema de la tabla
        table_schema = schema_registry.get_table_schema(table_name)
        
        if not table_schema:
            return json.dumps({
                "error": f"Tabla {table_name} no encontrada. Ejecuta discover_database_schema() primero."
            })
        
        # Generar operaciones CRUD
        crud_operations = crud_generator.generate_table_operations(table_schema)
        
        # Agregar queries educativas específicas
        educational_queries = crud_generator.generate_educational_queries(table_name)
        
        result = {
            "table_name": table_name,
            "crud_operations": crud_operations,
            "educational_queries": educational_queries,
            "generated_at": __import__('datetime').datetime.now().isoformat()
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @mcp_server.tool()
    def analyze_educational_structure() -> str:
        """
        Analiza la estructura de la base de datos desde perspectiva educativa
        Identifica entidades relacionadas con alumnos, docentes, centros, etc.
        """
        result = table_inspector.analyze_educational_structure()
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @mcp_server.tool()
    def export_database_documentation() -> str:
        """
        Exporta documentación completa de la base de datos en formato markdown
        """
        documentation = schema_registry.export_schema_documentation()
        
        result = {
            "documentation": documentation,
            "format": "markdown",
            "generated_at": __import__('datetime').datetime.now().isoformat(),
            "total_tables": len(schema_registry.get_all_tables())
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    return [
        discover_database_schema,
        get_table_documentation, 
        generate_crud_operations,
        analyze_educational_structure,
        export_database_documentation
    ]
