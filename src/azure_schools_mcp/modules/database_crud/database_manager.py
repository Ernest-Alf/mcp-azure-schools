"""
Database Manager - CRUD Operations
Sistema Educativo MCP - Ernest-Alf
"""

import json
import pandas as pd
from typing import Dict, Any, List, Optional
from azure_schools_mcp.config.database import db_manager

class DatabaseCRUDManager:
    """Gestor de operaciones CRUD para la base de datos educativa"""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def import_excel_to_database(self, filename: str, table_name: str = "centros_trabajo_raw") -> Dict[str, Any]:
        """Importa datos de Excel a la base de datos"""
        try:
            from pathlib import Path
            
            # Leer archivo Excel
            excel_dir = Path(__file__).parent.parent.parent.parent.parent / "excel_files"
            file_path = excel_dir / filename
            
            if not file_path.exists():
                return {"error": f"Archivo {filename} no encontrado"}
            
            # Leer datos con headers en fila 2 (formato educativo común)
            df = pd.read_excel(file_path, header=2)
            df.columns = df.columns.str.strip()
            
            # Verificar conexión
            if not self.db_manager.test_connection():
                return {"error": "No hay conexión a la base de datos"}
            
            # TODO: Crear tabla si no existe e insertar datos
            # Por ahora simulamos la operación
            
            result = {
                "filename": filename,
                "table_name": table_name,
                "rows_to_import": len(df),
                "columns": len(df.columns),
                "columns_detected": list(df.columns),
                "status": "Ready for import",
                "database_connection": "✅ Connected",
                "next_steps": [
                    "Crear esquema de tabla definitivo",
                    "Mapear columnas Excel → BD",
                    "Insertar datos estructurados"
                ]
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Error en importación: {str(e)}"}
    
    def create_educational_tables(self) -> Dict[str, Any]:
        """Crea tablas educativas en la base de datos"""
        try:
            if not self.db_manager.test_connection():
                return {"error": "No hay conexión a la base de datos"}
            
            # SQL para crear tabla principal de centros educativos
            create_centros_sql = """
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'centros_trabajo')
            CREATE TABLE centros_trabajo (
                id INT IDENTITY(1,1) PRIMARY KEY,
                clave_centro NVARCHAR(50) UNIQUE NOT NULL,
                nombre_centro NVARCHAR(200) NOT NULL,
                nivel_educativo NVARCHAR(50) NOT NULL,
                municipio NVARCHAR(100) NOT NULL,
                localidad NVARCHAR(100),
                sostenimiento NVARCHAR(50),
                zona_escolar NVARCHAR(20),
                matricula_total INT DEFAULT 0,
                total_docentes INT DEFAULT 0,
                fecha_registro DATETIME2 DEFAULT GETDATE(),
                fecha_actualizacion DATETIME2 DEFAULT GETDATE(),
                activo BIT DEFAULT 1
            );
            """
            
            # TODO: Ejecutar SQL cuando sea necesario
            
            return {
                "operation": "create_educational_tables",
                "status": "SQL prepared",
                "tables_to_create": ["centros_trabajo", "matricula_estudiantil", "personal_educativo"],
                "database_connection": "✅ Connected",
                "ready_to_execute": True
            }
            
        except Exception as e:
            return {"error": f"Error creando tablas: {str(e)}"}
    
    def query_schools_by_municipality(self, municipio: str = None) -> Dict[str, Any]:
        """Consulta centros educativos por municipio"""
        try:
            if not self.db_manager.test_connection():
                return {"error": "No hay conexión a la base de datos"}
            
            # SQL query para análisis por municipio
            if municipio:
                query = f"""
                SELECT municipio, nivel_educativo, COUNT(*) as total_centros,
                       SUM(matricula_total) as total_alumnos,
                       AVG(matricula_total) as promedio_matricula
                FROM centros_trabajo 
                WHERE municipio = '{municipio}' AND activo = 1
                GROUP BY municipio, nivel_educativo
                ORDER BY total_centros DESC;
                """
            else:
                query = """
                SELECT municipio, COUNT(*) as total_centros,
                       SUM(matricula_total) as total_alumnos
                FROM centros_trabajo 
                WHERE activo = 1
                GROUP BY municipio
                ORDER BY total_centros DESC;
                """
            
            # TODO: Ejecutar query real cuando tengamos datos
            
            return {
                "operation": "query_schools_by_municipality",
                "municipio_filter": municipio or "todos",
                "query_prepared": query,
                "database_connection": "✅ Connected",
                "status": "Ready to execute when data is imported"
            }
            
        except Exception as e:
            return {"error": f"Error en consulta: {str(e)}"}

# Instancia global del gestor CRUD
database_crud_manager = DatabaseCRUDManager()
