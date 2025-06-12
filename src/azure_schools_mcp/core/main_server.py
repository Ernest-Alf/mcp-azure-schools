"""
Sistema Educativo MCP - Servidor Principal REFACTORIZADO
Sin código redundante - Versión limpia
Ernest-Alf - Junio 2025
"""

import sys
from pathlib import Path

# Configurar path para imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root / "src"))

from mcp.server.fastmcp import FastMCP

# Imports centralizados - SIN redundancia
from azure_schools_mcp.shared.mcp_tools import register_excel_tools
from azure_schools_mcp.tests.diagnostics import register_diagnostics_tools

# Imports condicionales para módulos opcionales
try:
    from azure_schools_mcp.database_management import register_database_management_tools
    DATABASE_MODULE_AVAILABLE = True
except ImportError:
    DATABASE_MODULE_AVAILABLE = False

# Crear servidor MCP único
mcp = FastMCP("sistema-educativo-mcp-refactorizado")

def initialize_mcp_server():
    """Inicializa el servidor MCP con módulos sin redundancia"""
    print("🎯 Inicializando Sistema Educativo MCP - VERSIÓN REFACTORIZADA")
    print("✨ Sin código redundante - Arquitectura limpia")
    
    total_tools = 0
    
    # Excel Tools (centralizado)
    excel_tools = register_excel_tools(mcp)
    print(f"✅ Excel Tools (centralizado): {len(excel_tools)} herramientas")
    total_tools += len(excel_tools)
    
    # Diagnostics Tools
    diagnostics_tools = register_diagnostics_tools(mcp)
    print(f"✅ Diagnostics Tools: {len(diagnostics_tools)} herramientas")
    total_tools += len(diagnostics_tools)
    
    # Database Management (opcional)
    if DATABASE_MODULE_AVAILABLE:
        database_tools = register_database_management_tools(mcp)
        print(f"✅ Database Management: {len(database_tools)} herramientas")
        total_tools += len(database_tools)
    else:
        print("⚠️ Database Management: No disponible (módulo opcional)")
    
    print(f"🎯 Servidor MCP inicializado con {total_tools} herramientas totales")
    print("📊 Arquitectura limpia - Sin redundancias")
    
    return mcp

def test_server():
    """Prueba del servidor refactorizado"""
    print("🧪 Probando Sistema Educativo MCP REFACTORIZADO...")
    
    server = initialize_mcp_server()
    
    # Test del extractor centralizado
    try:
        from azure_schools_mcp.shared.excel_extractor import get_excel_extractor
        
        extractor = get_excel_extractor()
        test_result = extractor.list_excel_files()
        
        print("✅ Excel Extractor centralizado: Funcionando")
        print(f"✅ Estado: {test_result.get('status', 'unknown')}")
        print("✅ Sistema refactorizado: Operativo")
        print("🚀 Sin código redundante - Listo para producción")
        
    except Exception as e:
        print(f"❌ Error en test refactorizado: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_server()
    else:
        initialize_mcp_server()
        mcp.run()
