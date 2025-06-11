"""
Módulo de diagnóstico del sistema - Información y estado del sistema
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from azure_schools_mcp.config.settings import settings
from azure_schools_mcp.utils.logger import setup_logger

logger = setup_logger("diagnostics.system_info")

class SystemInfoManager:
    """Gestor de información del sistema"""
    
    def __init__(self):
        self.excel_dir = Path(__file__).parent.parent.parent.parent.parent / "excel_files"
        self.project_root = Path(__file__).parent.parent.parent.parent.parent
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtiene información completa del sistema"""
        return {
            "python": {
                "version": sys.version.split()[0],
                "executable": sys.executable,
                "platform": sys.platform
            },
            "project": {
                "root": str(self.project_root),
                "excel_dir": str(self.excel_dir),
                "excel_dir_exists": self.excel_dir.exists()
            },
            "environment": {
                "working_directory": os.getcwd(),
                "user": os.getenv('USER', 'unknown'),
                "home": os.getenv('HOME', 'unknown')
            }
        }
    
    def get_database_status(self) -> Dict[str, Any]:
        """Obtiene estado de la base de datos"""
        status = {
            "configured": settings.is_database_configured(),
            "server": settings.database.server if settings.database.server else "No configurado",
            "database": settings.database.database if settings.database.database else "No configurado",
            "username": "✅ Configurado" if settings.database.username else "❌ No configurado",
            "password": "✅ Configurado" if settings.database.password else "❌ No configurado",
            "connection_timeout": settings.database.connection_timeout
        }
        
        # Test de conexión
        try:
            from azure_schools_mcp.config.database import db_manager
            status["connection_test"] = db_manager.test_connection()
        except Exception as e:
            status["connection_test"] = False
            status["connection_error"] = str(e)
        
        return status
    
    def get_excel_files_info(self) -> Dict[str, Any]:
        """Obtiene información de archivos Excel disponibles"""
        info = {
            "directory": str(self.excel_dir),
            "exists": self.excel_dir.exists(),
            "files": [],
            "total_files": 0,
            "total_size_mb": 0
        }
        
        if self.excel_dir.exists():
            excel_extensions = settings.excel.supported_extensions
            excel_files = []
            
            for ext in excel_extensions:
                excel_files.extend(self.excel_dir.glob(f"*{ext}"))
            
            file_info_list = []
            total_size = 0
            
            for file_path in excel_files:
                file_stat = file_path.stat()
                size_mb = file_stat.st_size / (1024 * 1024)
                
                file_info = {
                    "name": file_path.name,
                    "size_mb": round(size_mb, 2),
                    "modified": pd.Timestamp.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                }
                file_info_list.append(file_info)
                total_size += size_mb
            
            info["files"] = sorted(file_info_list, key=lambda x: x['modified'], reverse=True)
            info["total_files"] = len(file_info_list)
            info["total_size_mb"] = round(total_size, 2)
        
        return info
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de configuración del sistema"""
        return {
            "mcp": {
                "server_name": settings.mcp.server_name,
                "max_tools": settings.mcp.max_tools,
                "timeout_seconds": settings.mcp.timeout_seconds
            },
            "excel": {
                "max_file_size_mb": settings.excel.max_file_size_mb,
                "supported_extensions": settings.excel.supported_extensions,
                "max_rows_per_query": settings.excel.max_rows_per_query
            },
            "system": {
                "log_level": settings.system.log_level,
                "max_rows_default": settings.system.max_rows_default,
                "cache_enabled": settings.system.cache_enabled,
                "cache_ttl_minutes": settings.system.cache_ttl_minutes,
                "debug_mode": settings.system.debug_mode
            }
        }
    
    def generate_diagnostic_report(self) -> str:
        """Genera el reporte de diagnóstico completo (migrado desde debug_info)"""
        report_lines = [
            "🎓 Sistema Educativo MCP - Diagnóstico Completo",
            "=" * 60,
            ""
        ]
        
        # Información del sistema
        sys_info = self.get_system_info()
        report_lines.extend([
            "🖥️  INFORMACIÓN DEL SISTEMA:",
            f"   📂 Directorio de trabajo: {sys_info['environment']['working_directory']}",
            f"   📁 Carpeta Excel: {self.excel_dir}",
            f"   ✅ Carpeta Excel existe: {sys_info['project']['excel_dir_exists']}",
            f"   🐍 Python: {sys_info['python']['version']}",
            f"   💻 Plataforma: {sys_info['python']['platform']}",
            f"   👤 Usuario: {sys_info['environment']['user']}",
            ""
        ])
        
        # Estado de la base de datos
        db_status = self.get_database_status()
        report_lines.extend([
            "🗄️  AZURE SQL DATABASE:",
            f"   🔧 Configurado: {'✅' if db_status['configured'] else '❌'}",
            f"   🖥️  Servidor: {db_status['server']}",
            f"   💾 Base de datos: {db_status['database']}",
            f"   👤 Usuario: {db_status['username']}",
            f"   🔐 Password: {db_status['password']}",
            f"   🔌 Test conexión: {'✅ OK' if db_status.get('connection_test') else '❌ Error'}",
            ""
        ])
        
        # Archivos Excel
        excel_info = self.get_excel_files_info()
        report_lines.extend([
            "📊 ARCHIVOS EXCEL:",
            f"   📁 Directorio: {excel_info['directory']}",
            f"   ✅ Existe: {'✅' if excel_info['exists'] else '❌'}",
            f"   📋 Total archivos: {excel_info['total_files']}",
            f"   💾 Tamaño total: {excel_info['total_size_mb']} MB",
            ""
        ])
        
        # Listar archivos si existen
        if excel_info['files']:
            report_lines.append("   📄 Archivos encontrados:")
            for i, file_info in enumerate(excel_info['files'], 1):
                report_lines.append(f"      {i}. 📊 {file_info['name']} ({file_info['size_mb']} MB)")
            report_lines.append("")
        
        # Configuración del sistema
        config = self.get_configuration_summary()
        report_lines.extend([
            "⚙️  CONFIGURACIÓN:",
            f"   🔧 MCP Server: {config['mcp']['server_name']}",
            f"   📊 Max filas default: {config['system']['max_rows_default']}",
            f"   📝 Log level: {config['system']['log_level']}",
            f"   💾 Cache enabled: {config['system']['cache_enabled']}",
            f"   🐛 Debug mode: {config['system']['debug_mode']}",
            ""
        ])
        
        report_lines.extend([
            "=" * 60,
            "🚀 Estado: Sistema operativo y listo para análisis educativo"
        ])
        
        return "\n".join(report_lines)

# Instancia global del gestor
system_info_manager = SystemInfoManager()
