"""
Script de entrada para el Sistema Educativo MCP
"""

import sys
from pathlib import Path

# Añadir src al path para imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from azure_schools_mcp.main_server import initialize_mcp_server, test_server, mcp

def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_server()
    else:
        # Inicializar servidor SIN prints para MCP
        initialize_mcp_server()
        # NO imprimir nada aquí - Claude Desktop necesita comunicación MCP limpia
        mcp.run()

if __name__ == "__main__":
    main()
