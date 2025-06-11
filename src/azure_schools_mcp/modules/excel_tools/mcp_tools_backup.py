   @mcp_server.tool()
   def excel_comprehensive_summary(filename: str, sheet_name: str = None) -> str:
       """Genera análisis estadístico completo de un archivo Excel (versión modular avanzada)"""
       try:
           logger.info(f"Generando resumen completo de: {filename}")
           
           # Primero cargar el archivo
           load_result = excel_file_manager.read_excel_file(
               filename, sheet_name, max_rows=1000  # Cargar más datos para análisis
           )
           
           if load_result["status"] != "success":
               return f"❌ Error cargando archivo: {load_result.get('error', 'Error desconocido')}"
           
           # Obtener DataFrame desde el caché
           cache_key = load_result["file_data"]["cached_as"]
           df = excel_file_manager.loaded_files.get(cache_key)
           
           if df is None:
               return "❌ Error: No se pudo obtener datos del archivo cargado"
           
           # Generar análisis completo
           analysis = excel_analyzer.generate_comprehensive_summary(df, filename, sheet_name)
           
           if analysis["status"] != "success":
               return f"❌ Error en análisis: {analysis['error']}"
           
           # Formatear respuesta
           basic = analysis["basic_info"]
           data_types = analysis["data_types"]
           null_analysis = analysis["null_analysis"]
           
           response_lines = [
               f"📊 ANÁLISIS COMPLETO: {basic['filename']}",
               "=" * 60,
               f"📄 Hoja: {basic['sheet']}",
               f"📏 Dimensiones: {basic['dimensions']['rows']:,} filas × {basic['dimensions']['columns']} columnas",
               f"💾 Memoria: {basic['memory_usage']['total_mb']} MB",
               f"🕐 Análisis: {analysis['timestamp'][:19]}",
               ""
           ]
           
           # Tipos de datos
           response_lines.extend([
               "🔤 TIPOS DE DATOS:",
               f"   📊 Numéricas: {len(data_types['numeric_columns'])} columnas",
               f"   📝 Texto: {len(data_types['text_columns'])} columnas",
               f"   📅 Fechas: {len(data_types['datetime_columns'])} columnas",
               ""
           ])
           
           # Calidad de datos
           null_summary = null_analysis["summary"]
           response_lines.extend([
               "⚠️  CALIDAD DE DATOS:",
               f"   ✅ Filas completas: {null_summary['complete_rows']:,} ({null_summary['completion_rate']}%)",
               f"   🔍 Filas con nulos: {null_summary['rows_with_nulls']:,}",
               f"   📊 Score calidad: {null_analysis['recommendations']['data_quality_score']}%",
               ""
           ])
           
           # Estadísticas numéricas (top 3)
           if "column_statistics" in analysis["numeric_statistics"]:
               numeric_stats = analysis["numeric_statistics"]["column_statistics"]
               response_lines.append("📈 ESTADÍSTICAS NUMÉRICAS (Top 3):")
               for i, (col, stats) in enumerate(list(numeric_stats.items())[:3], 1):
                   response_lines.append(
                       f"   {i}. {col}: Media={stats['mean']}, "
                       f"Rango=[{stats['min']}-{stats['max']}], "
                       f"Outliers={stats['outliers_count']}"
                   )
               response_lines.append("")
           
           # Columnas de texto más interesantes
           if "column_statistics" in analysis["text_statistics"]:
               text_stats = analysis["text_statistics"]["column_statistics"]
               response_lines.append("📝 ANÁLISIS DE TEXTO (Top 3):")
               for i, (col, stats) in enumerate(list(text_stats.items())[:3], 1):
                   top_value = list(stats['most_common'].keys())[0] if stats['most_common'] else "N/A"
                   response_lines.append(
                       f"   {i}. {col}: {stats['unique_values']} valores únicos, "
                       f"Más común: '{top_value}'"
                   )
               response_lines.append("")
           
           # Patrones detectados
           patterns = analysis["detected_patterns"]
           if any(patterns.values()):
               response_lines.append("🔍 PATRONES DETECTADOS:")
               if patterns["potential_id_columns"]:
                   response_lines.append(f"   🆔 IDs: {', '.join(patterns['potential_id_columns'])}")
               if patterns["potential_category_columns"]:
                   cat_names = [item["column"] for item in patterns["potential_category_columns"]]
                   response_lines.append(f"   🏷️  Categorías: {', '.join(cat_names)}")
               if patterns["potential_date_columns"]:
                   response_lines.append(f"   📅 Fechas: {', '.join(patterns['potential_date_columns'])}")
               response_lines.append("")
           
           # Recomendaciones
           if analysis["recommendations"]:
               response_lines.append("💡 RECOMENDACIONES:")
               for rec in analysis["recommendations"][:3]:  # Top 3
                   response_lines.append(f"   • {rec}")
           
           return "\n".join(response_lines)
           
       except Exception as e:
           logger.error(f"Error en excel_comprehensive_summary: {e}")
           return f"❌ Error generando análisis: {str(e)}"
   
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
   return [list_excel_files_v2, get_excel_file_info, read_excel_file_v2, 
           excel_comprehensive_summary, list_loaded_excel_files]
