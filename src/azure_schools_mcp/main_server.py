"""
Sistema Educativo MCP - Servidor Principal Simplificado
Enfocado únicamente en extracción de datos Excel
Ernest-Alf - Junio 2025
"""

import sys
from pathlib import Path

# Configurar path para imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mcp.server.fastmcp import FastMCP

# Imports de herramientas simplificadas
from azure_schools_mcp.tools.excel_extraction import register_excel_tools
from azure_schools_mcp.tools.diagnostics import register_diagnostics_tools

# Crear servidor MCP
mcp = FastMCP("sistema-educativo-mcp-simple")

def initialize_mcp_server():
    """Inicializa el servidor MCP simplificado con 5 herramientas esenciales"""
    print("🎯 Inicializando Sistema Educativo MCP - Versión Simplificada")
    
    # Registrar herramientas Excel (3 herramientas)
    excel_tools = register_excel_tools(mcp)
    print(f"✅ Excel Tools: {len(excel_tools)} herramientas registradas")
    
    # Registrar herramientas de diagnóstico (2 herramientas)
    diagnostics_tools = register_diagnostics_tools(mcp)
    print(f"✅ Diagnostics Tools: {len(diagnostics_tools)} herramientas registradas")
    
    total_tools = len(excel_tools) + len(diagnostics_tools)
    print(f"🎯 Servidor MCP inicializado con {total_tools} herramientas totales")
    print("📊 Enfoque: Extracción y análisis de datos Excel educativos")
    
    return mcp

def test_server():
    """Prueba rápida del servidor simplificado"""
    print("🧪 Probando Sistema Educativo MCP - Versión Simplificada...")
    
    # Inicializar servidor
    server = initialize_mcp_server()
    
    # Test básico de herramientas
    try:
        from azure_schools_mcp.tools.excel_extraction import excel_extractor
        from azure_schools_mcp.tools.diagnostics import system_diagnostics
        
        # Test extracción Excel
        excel_status = excel_extractor.list_excel_files()
        print(f"✅ Excel Tools: {excel_status.get('total_files', 0)} archivos detectados")
        
        # Test diagnósticos
        system_status = system_diagnostics.get_system_status()
        print(f"✅ System Status: {system_status.get('mcp_server', {}).get('tools_available', 0)} herramientas")
        
        print("🚀 Servidor MCP simplificado listo para uso")
        
    except Exception as e:
        print(f"❌ Error en test: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_server()
    else:
        # Ejecutar servidor
        initialize_mcp_server()
        mcp.run()
