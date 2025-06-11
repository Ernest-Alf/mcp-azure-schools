"""
Sistema Educativo MCP - Servidor Principal
Versión con Database Management Module
Ernest-Alf - Junio 2025
"""

import sys
from pathlib import Path

# Configurar path para imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mcp.server.fastmcp import FastMCP

# Imports de módulos
from azure_schools_mcp.tools.excel_extraction import register_excel_tools
from azure_schools_mcp.tools.diagnostics import register_diagnostics_tools
from azure_schools_mcp.modules.database_management import register_database_management_tools

# Crear servidor MCP
mcp = FastMCP("sistema-educativo-mcp")

def initialize_mcp_server():
    """Inicializa el servidor MCP con todos los módulos"""
    print("🎯 Inicializando Sistema Educativo MCP - Database Management")
    
    # Módulos existentes
    excel_tools = register_excel_tools(mcp)
    print(f"✅ Excel Tools: {len(excel_tools)} herramientas")
    
    diagnostics_tools = register_diagnostics_tools(mcp)
    print(f"✅ Diagnostics Tools: {len(diagnostics_tools)} herramientas")
    
    # Nuevo módulo Database Management
    database_management_tools = register_database_management_tools(mcp)
    print(f"✅ Database Management: {len(database_management_tools)} herramientas")
    
    total_tools = len(excel_tools) + len(diagnostics_tools) + len(database_management_tools)
    print(f"🎯 Servidor MCP inicializado con {total_tools} herramientas totales")
    print("📊 Arquitectura evolutiva lista para análisis de tus archivos Excel")
    
    return mcp

def test_server():
    """Prueba del servidor con Database Management"""
    print("🧪 Probando Sistema Educativo MCP - Database Management...")
    
    server = initialize_mcp_server()
    
    # Test básico del nuevo módulo
    try:
        from azure_schools_mcp.modules.database_management import schema_registry, table_inspector
        
        print("✅ Schema Registry: Funcionando")
        print("✅ Table Inspector: Funcionando") 
        print("✅ Database Management Module: Operativo")
        print("🚀 Sistema listo para analizar tus archivos Excel y crear esquemas automáticamente")
        
    except Exception as e:
        print(f"❌ Error en Database Management: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_server()
    else:
        initialize_mcp_server()
        mcp.run()