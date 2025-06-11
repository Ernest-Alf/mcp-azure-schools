"""
Script de entrada para el Sistema Educativo MCP
Versión actualizada para estructura modular
Ernest-Alf - Junio 2025
"""

import sys
from pathlib import Path

# Añadir src al path para imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

try:
    from azure_schools_mcp.main_server import initialize_mcp_server, test_server, mcp
except ImportError as e:
    print(f"❌ Error importando main_server: {e}")
    print("🔍 Verificando estructura del proyecto...")
    
    # Verificar estructura
    main_server_path = project_root / "src" / "azure_schools_mcp" / "main_server.py"
    if main_server_path.exists():
        print(f"✅ main_server.py existe en: {main_server_path}")
    else:
        print(f"❌ main_server.py NO existe en: {main_server_path}")
    
    # Verificar módulos
    modules_path = project_root / "src" / "azure_schools_mcp" / "modules"
    if modules_path.exists():
        print(f"✅ Directorio modules/ existe")
        for module_dir in modules_path.iterdir():
            if module_dir.is_dir():
                print(f"   📁 {module_dir.name}/")
    else:
        print(f"❌ Directorio modules/ NO existe en: {modules_path}")
    
    sys.exit(1)

def main():
    """Función principal"""
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "test":
            print("🧪 Ejecutando test del Sistema Educativo MCP...")
            test_server()
        else:
            # Inicializar servidor SIN prints para MCP (Claude Desktop necesita comunicación limpia)
            initialize_mcp_server()
            
            # NO imprimir nada aquí - Claude Desktop necesita comunicación MCP limpia
            mcp.run()
            
    except Exception as e:
        print(f"❌ Error ejecutando servidor MCP: {e}")
        print("🔍 Verificar que la estructura modular esté correcta")
        sys.exit(1)

if __name__ == "__main__":
    main()