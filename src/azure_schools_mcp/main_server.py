"""
Servidor MCP principal del Sistema Educativo - Versión Modular
"""

import sys
import os
from pathlib import Path

# Añadir src al path para imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mcp.server.fastmcp import FastMCP

# Imports absolutos
from azure_schools_mcp.config.settings import settings
from azure_schools_mcp.utils.logger import setup_logger
from azure_schools_mcp.modules.diagnostics.mcp_tools import register_diagnostics_tools
from azure_schools_mcp.modules.excel_tools.mcp_tools import register_excel_tools

# Configurar logging
logger = setup_logger("main_server")

# Crear el servidor MCP
mcp = FastMCP(settings.mcp.server_name)

def initialize_mcp_server():
    """Inicializa el servidor MCP con todos los módulos"""
    logger.info("🚀 Inicializando Sistema Educativo MCP - Versión Modular v2.0")
    
    # Registrar herramientas del módulo diagnostics
    diagnostics_tools = register_diagnostics_tools(mcp)
    logger.info(f"✅ Módulo diagnostics: {len(diagnostics_tools)} herramientas registradas")
    
    # Registrar herramientas del módulo excel_tools
    excel_tools = register_excel_tools(mcp)
    logger.info(f"✅ Módulo excel_tools: {len(excel_tools)} herramientas registradas")
    
    # TODO: Registrar otros módulos aquí cuando estén listos
    # register_schools_analysis_tools(mcp)
    # register_database_tools(mcp)
    # register_reporting_tools(mcp)
    
    total_tools = len(diagnostics_tools) + len(excel_tools)
    logger.info(f"🎯 Servidor MCP inicializado con {total_tools} herramientas totales")
    
    return mcp

# Función de prueba para mantener compatibilidad
def test_server():
    """Prueba básica del servidor MCP modular"""
    print("🧪 Probando Sistema Educativo MCP - Versión Modular v2.0...")
    
    # Inicializar servidor
    server = initialize_mcp_server()
    
    # Información del sistema
    from azure_schools_mcp.modules.diagnostics.system_info import system_info_manager
    from azure_schools_mcp.modules.excel_tools.file_manager import excel_file_manager
    
    print(f"📁 Directorio Excel: {system_info_manager.excel_dir}")
    print(f"🗄️  Azure SQL: {'✅ Configurado' if settings.is_database_configured() else '❌ No configurado'}")
    
    # Probar herramientas de diagnóstico
    try:
        report = system_info_manager.generate_diagnostic_report()
        print("✅ debug_info_v2() funciona")
        print(f"📄 Resultado: {report[:100]}...")
    except Exception as e:
        print(f"❌ Error en debug_info_v2(): {e}")
    
    # Probar herramientas de Excel
    try:
        excel_result = excel_file_manager.list_excel_files()
        print("✅ list_excel_files_v2() funciona")
        print(f"📊 Archivos Excel: {excel_result.get('total_files', 0)}")
    except Exception as e:
        print(f"❌ Error en list_excel_files_v2(): {e}")
    
    print("🚀 Servidor MCP modular v2.0 listo para ejecutar")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_server()
    else:
        # Inicializar e iniciar servidor
        initialize_mcp_server()
        print("🚀 Iniciando Sistema Educativo MCP - Versión Modular v2.0...")
        mcp.run()
