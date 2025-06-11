"""
Herramientas MCP para el módulo de diagnósticos
"""

from mcp.server.fastmcp import FastMCP
from .system_info import system_info_manager
from ...utils.logger import setup_logger

logger = setup_logger("diagnostics.mcp_tools")

def register_diagnostics_tools(mcp_server: FastMCP):
    """Registra todas las herramientas MCP del módulo de diagnósticos"""
    
    @mcp_server.tool()
    def debug_info_v2() -> str:
        """Información de diagnóstico completa del Sistema Educativo MCP (versión modular)"""
        try:
            logger.info("Generando reporte de diagnóstico v2")
            return system_info_manager.generate_diagnostic_report()
        except Exception as e:
            logger.error(f"Error en debug_info_v2: {e}")
            return f"❌ Error generando diagnóstico: {str(e)}"
    
    @mcp_server.tool()
    def system_status() -> str:
        """Estado resumido del sistema"""
        try:
            sys_info = system_info_manager.get_system_info()
            db_status = system_info_manager.get_database_status()
            excel_info = system_info_manager.get_excel_files_info()
            
            status_lines = [
                "📊 ESTADO DEL SISTEMA:",
                f"🐍 Python: {sys_info['python']['version']}",
                f"🗄️  Database: {'✅ Conectada' if db_status.get('connection_test') else '❌ Sin conexión'}",
                f"📊 Archivos Excel: {excel_info['total_files']} disponibles",
                f"💾 Tamaño total: {excel_info['total_size_mb']} MB",
                f"⚙️  Log level: {system_info_manager.get_configuration_summary()['system']['log_level']}"
            ]
            
            return "\n".join(status_lines)
            
        except Exception as e:
            logger.error(f"Error en system_status: {e}")
            return f"❌ Error obteniendo estado: {str(e)}"
    
    @mcp_server.tool()
    def database_diagnostics() -> str:
        """Diagnóstico específico de la base de datos Azure SQL"""
        try:
            db_status = system_info_manager.get_database_status()
            
            diag_lines = [
                "🗄️  DIAGNÓSTICO AZURE SQL DATABASE:",
                "=" * 40,
                f"📊 Estado general: {'✅ Configurada' if db_status['configured'] else '❌ No configurada'}",
                f"🖥️  Servidor: {db_status['server']}",
                f"💾 Base de datos: {db_status['database']}",
                f"👤 Usuario: {db_status['username']}",
                f"🔐 Password: {db_status['password']}",
                f"⏱️  Timeout: {db_status['connection_timeout']}s",
                f"🔌 Test conexión: {'✅ Exitoso' if db_status.get('connection_test') else '❌ Falló'}",
            ]
            
            if not db_status.get('connection_test') and 'connection_error' in db_status:
                diag_lines.extend([
                    "",
                    f"🚨 Error de conexión:",
                    f"   {db_status['connection_error']}"
                ])
            
            return "\n".join(diag_lines)
            
        except Exception as e:
            logger.error(f"Error en database_diagnostics: {e}")
            return f"❌ Error en diagnóstico de BD: {str(e)}"
    
    @mcp_server.tool()
    def excel_files_diagnostics() -> str:
        """Diagnóstico de archivos Excel disponibles"""
        try:
            excel_info = system_info_manager.get_excel_files_info()
            
            diag_lines = [
                "📊 DIAGNÓSTICO ARCHIVOS EXCEL:",
                "=" * 40,
                f"📁 Directorio: {excel_info['directory']}",
                f"✅ Directorio existe: {'Sí' if excel_info['exists'] else 'No'}",
                f"📋 Total archivos: {excel_info['total_files']}",
                f"💾 Tamaño total: {excel_info['total_size_mb']} MB",
                ""
            ]
            
            if excel_info['files']:
                diag_lines.append("📄 Archivos encontrados:")
                for i, file_info in enumerate(excel_info['files'], 1):
                    diag_lines.append(
                        f"   {i}. {file_info['name']} "
                        f"({file_info['size_mb']} MB) "
                        f"- {file_info['modified']}"
                    )
            else:
                diag_lines.append("⚠️  No se encontraron archivos Excel")
            
            return "\n".join(diag_lines)
            
        except Exception as e:
            logger.error(f"Error en excel_files_diagnostics: {e}")
            return f"❌ Error en diagnóstico Excel: {str(e)}"
    
    logger.info("✅ Herramientas MCP de diagnósticos registradas")
    return [debug_info_v2, system_status, database_diagnostics, excel_files_diagnostics]
