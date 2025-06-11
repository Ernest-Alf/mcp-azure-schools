"""
Herramientas MCP para el módulo Excel Tools
"""

import json
from mcp.server.fastmcp import FastMCP
from .file_manager import excel_file_manager
from .analyzer import excel_analyzer
from azure_schools_mcp.utils.logger import setup_logger

logger = setup_logger("excel_tools.mcp_tools")

def register_excel_tools(mcp_server: FastMCP):
    """Registra todas las herramientas MCP del módulo Excel Tools"""
    
    @mcp_server.tool()
    def list_excel_files_v2() -> str:
        """Lista archivos Excel disponibles con información detallada (versión modular)"""
        try:
            logger.info("Listando archivos Excel v2")
            result = excel_file_manager.list_excel_files()
            
            if result["status"] == "empty":
                return f"📁 {result['message']}\n💡 {result['suggestion']}"
            
            if result["status"] == "error":
                return f"❌ Error: {result['error']}"
            
            # Formatear respuesta
            response_lines = [
                "📊 ARCHIVOS EXCEL DISPONIBLES:",
                "=" * 40,
                f"📁 Directorio: {result['directory']}",
                f"�� Total archivos: {result['total_files']}",
                f"💾 Tamaño total: {result['total_size_mb']} MB",
                ""
            ]
            
            for i, file_info in enumerate(result['files'], 1):
                status_icon = "✅" if file_info['valid'] else "❌"
                response_lines.append(
                    f"   {i}. {status_icon} {file_info['name']} "
                    f"({file_info['size_mb']} MB) - {file_info['modified']}"
                )
            
            return "\n".join(response_lines)
            
        except Exception as e:
            logger.error(f"Error en list_excel_files_v2: {e}")
            return f"❌ Error listando archivos: {str(e)}"
    
    @mcp_server.tool()
    def get_excel_file_info(filename: str) -> str:
        """Obtiene información detallada de un archivo Excel específico"""
        try:
            logger.info(f"Obteniendo info de archivo: {filename}")
            result = excel_file_manager.get_file_info(filename)
            
            if result["status"] == "not_found":
                return f"❌ {result['error']}\n📋 Archivos disponibles: {', '.join(result['available_files'])}"
            
            if result["status"] == "invalid":
                return f"❌ Archivo inválido:\n   Errores: {', '.join(result['errors'])}"
            
            if result["status"] == "error":
                return f"❌ Error: {result['error']}"
            
            # Formatear información del archivo
            file_info = result["file_info"]
            response_lines = [
                f"📊 INFORMACIÓN DEL ARCHIVO: {file_info['name']}",
                "=" * 50,
                f"📁 Ruta: {file_info['path']}",
                f"💾 Tamaño: {file_info['size_mb']} MB",
                f"📅 Modificado: {file_info['modified']}",
                f"📋 Hojas: {file_info['sheets']['count']}",
                f"📝 Nombres: {', '.join(file_info['sheets']['names'])}",
                ""
            ]
            
            # Información de cada hoja
            for sheet_name, sheet_info in file_info['sheets']['details'].items():
                if 'error' in sheet_info:
                    response_lines.append(f"   ❌ {sheet_name}: {sheet_info['error']}")
                else:
                    response_lines.append(
                        f"   📄 {sheet_name}: {sheet_info['rows']} filas, "
                        f"{sheet_info['column_count']} columnas "
                        f"({sheet_info['estimated_memory_mb']} MB)"
                    )
            
            return "\n".join(response_lines)
            
        except Exception as e:
            logger.error(f"Error en get_excel_file_info: {e}")
            return f"❌ Error obteniendo información: {str(e)}"
    
    @mcp_server.tool()
    def read_excel_file_v2(filename: str, sheet_name: str = None, 
                          max_rows: int = 10, header_row: int = 0) -> str:
        """Lee contenido de archivo Excel con configuración avanzada (versión modular)"""
        try:
            logger.info(f"Leyendo archivo Excel: {filename}")
            result = excel_file_manager.read_excel_file(
                filename, sheet_name, max_rows, header_row
            )
            
            if result["status"] == "not_found":
                return f"❌ {result['error']}\n📋 Archivos disponibles: {', '.join(result['available_files'])}"
            
            if result["status"] == "error":
                return f"❌ Error: {result['error']}\n🔧 {result['details']}"
            
            # Formatear datos leídos
            file_data = result["file_data"]
            metadata = result["metadata"]
            
            response_lines = [
                f"📊 CONTENIDO DEL ARCHIVO: {file_data['filename']}",
                "=" * 50,
                f"📄 Hoja: {file_data['sheet']}",
                f"📋 Filas cargadas: {file_data['rows_loaded']}",
                f"📊 Columnas: {file_data['column_count']}",
                f"💾 Memoria: {metadata['memory_usage_mb']} MB",
                f"🔑 Guardado como: {file_data['cached_as']}",
                "",
                "📝 COLUMNAS:",
                "   " + ", ".join(file_data['columns']),
                ""
            ]
            
            # Mostrar datos de muestra
            if file_data['data']:
                response_lines.append("📋 DATOS DE MUESTRA:")
                for i, row in enumerate(file_data['data'][:3], 1):
                    response_lines.append(f"   Fila {i}: {dict(list(row.items())[:3])}...")
            
            # Información de valores nulos
            null_counts = metadata['null_counts']
            if any(null_counts.values()):
                response_lines.extend([
                    "",
                    "⚠️  VALORES NULOS:",
                    "   " + ", ".join([f"{k}: {v}" for k, v in null_counts.items() if v > 0])
                ])
            
            return "\n".join(response_lines)
            
        except Exception as e:
            logger.error(f"Error en read_excel_file_v2: {e}")
            return f"❌ Error leyendo archivo: {str(e)}"
    
    @mcp_server.tool()
    def list_loaded_excel_files() -> str:
        """Lista archivos Excel cargados en memoria con información de uso"""
        try:
            logger.info("Listando archivos cargados en memoria")
            result = excel_file_manager.get_loaded_files()
            
            if result["status"] == "empty":
                return f"📭 {result['message']}\n💡 {result['suggestion']}"
            
            response_lines = [
                "💾 ARCHIVOS EXCEL EN MEMORIA:",
                "=" * 40,
                f"📊 Total cargados: {result['total_loaded']}",
                f"💾 Memoria total: {result['total_memory_mb']} MB",
                ""
            ]
            
            for i, file_info in enumerate(result['loaded_files'], 1):
                response_lines.append(
                    f"   {i}. 🔑 {file_info['cache_key']}"
                )
                response_lines.append(
                    f"      📏 {file_info['rows']:,} filas × {file_info['columns']} columnas"
                )
                response_lines.append(
                    f"      💾 {file_info['memory_mb']} MB"
                )
                response_lines.append(
                    f"      📋 Columnas: {', '.join(file_info['column_names'])}..."
                )
                response_lines.append("")
            
            response_lines.extend([
                "🛠️  OPERACIONES DISPONIBLES:",
                "   " + " | ".join(result['available_operations'])
            ])
            
            return "\n".join(response_lines)
            
        except Exception as e:
            logger.error(f"Error en list_loaded_excel_files: {e}")
            return f"❌ Error listando archivos cargados: {str(e)}"
    
    logger.info("✅ Herramientas MCP de Excel Tools registradas")
    return [list_excel_files_v2, get_excel_file_info, read_excel_file_v2, list_loaded_excel_files]
