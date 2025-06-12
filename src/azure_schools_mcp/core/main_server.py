"""
Sistema Educativo MCP - Servidor Principal REFACTORIZADO
Sin código redundante - Versión limpia
Ernest-Alf - Junio 2025
"""

import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Imports centralizados
from azure_schools_mcp.data_sources.excel.mcp_tools import register_excel_tools

# Imports condicionales para módulos opcionales
try:
   from azure_schools_mcp.tests.diagnostics import register_diagnostics_tools
   DIAGNOSTICS_AVAILABLE = True
except ImportError:
   DIAGNOSTICS_AVAILABLE = False

try:
   from azure_schools_mcp.database_management import register_database_management_tools
   DATABASE_MODULE_AVAILABLE = True
except ImportError:
   DATABASE_MODULE_AVAILABLE = False

# Crear servidor MCP único
mcp = FastMCP("sistema-educativo-mcp-refactorizado")

def initialize_mcp_server():
   """Inicializa el servidor MCP con módulos sin redundancia"""
   print("Inicializando Sistema Educativo MCP - VERSIÓN REFACTORIZADA")
   
   total_tools = 0
   
   # Excel Tools (obligatorio)
   excel_tools = register_excel_tools(mcp)
   print(f"Excel Tools: {len(excel_tools)} herramientas")
   total_tools += len(excel_tools)
   
   # Diagnostics Tools (opcional)
   if DIAGNOSTICS_AVAILABLE:
       diagnostics_tools = register_diagnostics_tools(mcp)
       print(f"Diagnostics Tools: {len(diagnostics_tools)} herramientas")
       total_tools += len(diagnostics_tools)
   else:
       print("Diagnostics Tools: No disponible")
   
   # Database Management (opcional)
   if DATABASE_MODULE_AVAILABLE:
       database_tools = register_database_management_tools(mcp)
       print(f"Database Management: {len(database_tools)} herramientas")
       total_tools += len(database_tools)
   else:
       print("Database Management: No disponible")
   
   print(f"Servidor MCP inicializado con {total_tools} herramientas totales")
   
   return mcp

def test_server():
   """Prueba del servidor refactorizado"""
   print("Probando Sistema Educativo MCP...")
   
   server = initialize_mcp_server()
   
   try:
       from azure_schools_mcp.data_sources.excel.excel_extractor import ExcelExtractor
       
       excel_dir = Path(__file__).parent.parent.parent / "excel_files"
       extractor = ExcelExtractor(excel_dir)
       
       print("Excel Extractor: Funcionando")
       print("Sistema refactorizado: Operativo")
       
   except Exception as e:
       print(f"Error en test: {e}")

if __name__ == "__main__":
   if len(sys.argv) > 1 and sys.argv[1] == "test":
       test_server()
   else:
       initialize_mcp_server()
       mcp.run()