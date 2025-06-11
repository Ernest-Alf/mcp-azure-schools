"""
Diagnostics Tools - Sistema Educativo MCP
Herramientas simplificadas de diagnóstico
Ernest-Alf - Junio 2025
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

class SystemDiagnostics:
    """Diagnósticos simplificados del sistema"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent.parent
        self.excel_dir = self.project_root / "excel_files"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Estado básico del sistema"""
        try:
            # Info básica del sistema
            status = {
                "system_info": {
                    "python_version": sys.version.split()[0],
                    "working_directory": str(Path.cwd()),
                    "project_root": str(self.project_root)
                },
                "excel_processing": {
                    "excel_directory": str(self.excel_dir),
                    "excel_dir_exists": self.excel_dir.exists(),
                    "excel_files_count": len(list(self.excel_dir.glob("*.xlsx"))) if self.excel_dir.exists() else 0
                },
                "mcp_server": {
                    "server_status": "running",
                    "tools_available": 5
                }
            }
            
            # Verificar dependencias críticas
            dependencies = {}
            try:
                import mcp
                dependencies["mcp"] = "✅ Disponible"
            except:
                dependencies["mcp"] = "❌ No disponible"
            
            try:
                import pandas
                dependencies["pandas"] = f"✅ v{pandas.__version__}"
            except:
                dependencies["pandas"] = "❌ No disponible"
                
            try:
                import openpyxl
                dependencies["openpyxl"] = f"✅ v{openpyxl.__version__}"
            except:
                dependencies["openpyxl"] = "❌ No disponible"
            
            status["dependencies"] = dependencies
            
            return status
            
        except Exception as e:
            return {"error": f"Error obteniendo estado: {str(e)}"}
    
    def get_database_status(self) -> Dict[str, Any]:
        """Estado de la conexión Azure SQL"""
        try:
            # Importar configuración de BD
            try:
                from azure_schools_mcp.config.database import db_manager
                
                db_status = {
                    "database_configured": True,
                    "connection_test": False,
                    "connection_details": {
                        "server": "drvii-apps.database.windows.net",
                        "database": "schools-mcp-db"
                    }
                }
                
                # Test de conexión
                try:
                    connection_ok = db_manager.test_connection()
                    db_status["connection_test"] = connection_ok
                    db_status["status"] = "✅ Conectada" if connection_ok else "⚠️ No disponible"
                except Exception as e:
                    db_status["connection_error"] = str(e)
                    db_status["status"] = "❌ Error de conexión"
                
                return db_status
                
            except ImportError:
                return {
                    "database_configured": False,
                    "status": "❌ Módulo de BD no configurado",
                    "recommendation": "Verificar configuración en config/database.py"
                }
                
        except Exception as e:
            return {"error": f"Error verificando BD: {str(e)}"}

# Instancia global de diagnósticos
system_diagnostics = SystemDiagnostics()

def register_diagnostics_tools(mcp_server: FastMCP):
    """Registra herramientas de diagnóstico en el servidor MCP"""
    
    @mcp_server.tool()
    def system_status() -> str:
        """Estado general del sistema MCP y dependencias"""
        result = system_diagnostics.get_system_status()
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @mcp_server.tool()
    def database_status() -> str:
        """Estado de la conexión a Azure SQL Database"""
        result = system_diagnostics.get_database_status()
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    return [system_status, database_status]
