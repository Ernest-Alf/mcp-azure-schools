"""
Script de entrada REFACTORIZADO - Sistema Educativo MCP
Sin código redundante - Versión limpia
Ernest-Alf - Junio 2025
"""

import sys
from pathlib import Path

# Añadir src al path para imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

try:
   from src.azure_schools_mcp.core.main_server import initialize_mcp_server, test_server, mcp
except ImportError as e:
   print(f"Error importando main_server: {e}")
   print("Verificando estructura del proyecto...")
   
   # Verificar estructura
   main_server_path = project_root / "src" / "azure_schools_mcp" / "core" / "main_server.py"
   excel_tools_path = project_root / "src" / "azure_schools_mcp" / "data_sources" / "excel" / "mcp_tools.py"
   
   print(f"main_server.py: {'Existe' if main_server_path.exists() else 'NO existe'}")
   print(f"excel mcp_tools.py: {'Existe' if excel_tools_path.exists() else 'NO existe'}")
   
   sys.exit(1)

def main():
   """Función principal refactorizada"""
   try:
       if len(sys.argv) > 1 and sys.argv[1] == "test":
           print("Ejecutando test del Sistema Educativo MCP...")
           test_server()
       else:
           initialize_mcp_server()
           mcp.run()
           
   except Exception as e:
       print(f"❌ Error ejecutando servidor MCP: {e}")
       sys.exit(1)

if __name__ == "__main__":
   main()