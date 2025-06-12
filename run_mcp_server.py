"""
Script de entrada REFACTORIZADO - Sistema Educativo MCP
Sin código redundante - Versión limpia
Ernest-Alf - Junio 2025
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Añadir src al path para imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

try:
    from src.azure_schools_mcp.core.main_server import initialize_mcp_server, test_server, mcp
except ImportError as e:
    print(f"❌ Error importando main_server refactorizado: {e}")
    print("🔍 Verificando estructura del proyecto...")
    
    # Verificar nueva estructura
    main_server_path = project_root / "src" / "azure_schools_mcp" / "core" / "main_server.py"
    if main_server_path.exists():
        print(f"✅ main_server.py refactorizado existe en: {main_server_path}")
    else:
        print(f"❌ main_server.py NO existe en: {main_server_path}")
    
    # Verificar shared
    shared_path = project_root / "src" / "azure_schools_mcp" / "shared"
    if shared_path.exists():
        print(f"✅ Directorio shared/ existe")
        for shared_file in shared_path.iterdir():
            if shared_file.is_file():
                print(f"   📄 {shared_file.name}")
    else:
        print(f"❌ Directorio shared/ NO existe en: {shared_path}")
    
    sys.exit(1)

def main():
    """Función principal refactorizada"""
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "test":
            print("🧪 Ejecutando test del Sistema Educativo MCP REFACTORIZADO...")
            test_server()
        else:
            # Inicializar servidor limpio SIN redundancias
            initialize_mcp_server()
            
            # Ejecutar servidor MCP
            mcp.run()
            
    except Exception as e:
        print(f"❌ Error ejecutando servidor MCP refactorizado: {e}")
        print("🔍 Verificar que la estructura refactorizada esté correcta")
        sys.exit(1)

if __name__ == "__main__":
    main()
