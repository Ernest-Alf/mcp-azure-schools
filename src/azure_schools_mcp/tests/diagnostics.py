"""
Diagnostics Tools - Sistema Educativo MCP MEJORADO
Usa utils simplificados y logging centralizado
Ernest-Alf - Junio 2025
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
import pandas as pd

# Usar utils simplificados
from ..utils import main_logger, FileManager, validate_excel_file_basic

class SystemDiagnostics:
    """Diagnósticos del sistema con logging mejorado"""
    
    def __init__(self):
        self.project_root = self._find_project_root()
        self.excel_dir = self.project_root / "excel_files"
        main_logger.info("🔧 Sistema de diagnósticos inicializado")
    
    def _find_project_root(self) -> Path:
        """Encuentra la raíz del proyecto de forma inteligente"""
        current = Path(__file__).parent
        while current.parent != current:
            if (current / "excel_files").exists() or current.name == "mcp-azure-schools":
                return current
            current = current.parent
        return Path.cwd()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Estado del sistema con logging"""
        main_logger.info("Obteniendo estado del sistema...")
        
        try:
            status = {
                "timestamp": str(pd.Timestamp.now()) if 'pd' in globals() else "N/A",
                "system_info": {
                    "python_version": sys.version.split()[0],
                    "working_directory": str(Path.cwd()),
                    "project_root": str(self.project_root),
                    "excel_directory": str(self.excel_dir)
                },
                "excel_processing": self._get_excel_status(),
                "dependencies": self._check_dependencies(),
                "mcp_server": {
                    "status": "running",
                    "tools_registered": "diagnostics + excel_tools"
                }
            }
            
            main_logger.info("Estado del sistema obtenido")
            return status
            
        except Exception as e:
            error_msg = f"Error obteniendo estado: {str(e)}"
            main_logger.error(error_msg)
            return {"error": error_msg}
    
    def _get_excel_status(self) -> Dict[str, Any]:
        """Estado del procesamiento Excel"""
        excel_status = {
            "directory_exists": self.excel_dir.exists(),
            "directory_path": str(self.excel_dir)
        }
        
        if self.excel_dir.exists():
            # Usar FileManager de utils
            excel_files = FileManager.list_excel_files(self.excel_dir)
            excel_status.update({
                "files_count": len(excel_files),
                "files_found": [f.name for f in excel_files[:5]],  # Solo primeros 5
                "total_size_mb": sum(
                    FileManager.get_file_info(f).get("size_mb", 0) 
                    for f in excel_files
                )
            })
            
            # Validar primer archivo si existe
            if excel_files:
                validation = validate_excel_file_basic(excel_files[0])
                excel_status["sample_validation"] = validation
        else:
            excel_status.update({
                "files_count": 0,
                "status": "⚠️ Directorio no existe"
            })
        
        return excel_status
    
    def _check_dependencies(self) -> Dict[str, str]:
        """Verifica dependencias críticas"""
        dependencies = {}
        
        critical_modules = [
            ("mcp", "MCP Framework"),
            ("pandas", "Pandas - Procesamiento de datos"),
            ("openpyxl", "OpenPyXL - Lectura Excel"),
            ("pyodbc", "PyODBC - Conexión SQL")
        ]
        
        for module_name, description in critical_modules:
            try:
                module = __import__(module_name)
                version = getattr(module, '__version__', 'unknown')
                dependencies[description] = f"v{version}"
                main_logger.debug(f"Dependencia OK: {module_name} v{version}")
            except ImportError:
                dependencies[description] = "No disponible"
                main_logger.warning(f"Dependencia faltante: {module_name}")
        
        return dependencies
    
    def get_database_status(self) -> Dict[str, Any]:
        """Estado de Azure SQL con logging"""
        main_logger.info("🗄️ Verificando estado de base de datos...")
        
        try:
            # Usar configuración centralizada
            from ..config.settings import settings
            
            db_status = {
                "configured": settings.is_database_configured(),
                "connection_string_ready": bool(settings.get_connection_string())
            }
            
            if db_status["configured"]:
                db_status["config"] = {
                    "server": settings.database.server,
                    "database": settings.database.database,
                    "username": settings.database.username,
                    "driver": settings.database.driver
                }
                
                # Test de conexión
                try:
                    from ..config.database import db_manager
                    
                    main_logger.info("🔗 Probando conexión a BD...")
                    connection_ok = db_manager.test_connection()
                    
                    db_status.update({
                        "connection_test": connection_ok,
                        "status": "Conectada" if connection_ok else "⚠️ Error de conexión"
                    })
                    
                    if connection_ok:
                        main_logger.info("Conexión BD exitosa")
                    else:
                        main_logger.warning("Conexión BD falló")
                        
                except Exception as e:
                    db_status.update({
                        "connection_test": False,
                        "connection_error": str(e),
                        "status": "Error de conexión"
                    })
                    main_logger.error(f"Error conectando BD: {e}")
            else:
                db_status.update({
                    "status": "No configurada",
                    "recommendation": "Configurar variables en .env"
                })
                main_logger.warning("Base de datos no configurada")
            
            return db_status
            
        except Exception as e:
            error_msg = f"Error verificando BD: {str(e)}"
            main_logger.error(error_msg)
            return {"error": error_msg}

# Instancia global
system_diagnostics = SystemDiagnostics()

def register_diagnostics_tools(mcp_server: FastMCP):
    """Registra herramientas de diagnóstico mejoradas"""
    
    @mcp_server.tool()
    def system_status() -> str:
        """Estado completo del sistema MCP con logging"""
        main_logger.info("🔧 Ejecutando diagnóstico del sistema")
        result = system_diagnostics.get_system_status()
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @mcp_server.tool()
    def database_status() -> str:
        """Estado detallado de Azure SQL Database"""
        main_logger.info("🗄️ Ejecutando diagnóstico de base de datos") 
        result = system_diagnostics.get_database_status()
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    @mcp_server.tool()
    def excel_files_diagnostic() -> str:
        """Diagnóstico específico de archivos Excel"""
        main_logger.info("Ejecutando diagnóstico de archivos Excel")
        result = system_diagnostics._get_excel_status()
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    main_logger.info("Herramientas de diagnóstico registradas")
    return [system_status, database_status, excel_files_diagnostic]
