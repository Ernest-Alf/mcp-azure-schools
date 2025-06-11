"""
Table Inspector - Introspección de tablas de BD
Sistema Educativo MCP - Ernest-Alf
"""

from typing import Dict, Any, List, Optional
from azure_schools_mcp.config.database import db_manager

class TableInspector:
    """Inspector de estructura de base de datos"""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def discover_schema(self) -> Dict[str, Any]:
        """Descubre el esquema completo de la base de datos"""
        try:
            if not self.db_manager.test_connection():
                return {"error": "No hay conexión a la base de datos"}
            
            # Query para obtener información de tablas
            tables_query = """
            SELECT 
                TABLE_NAME,
                TABLE_TYPE,
                TABLE_SCHEMA
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            AND TABLE_SCHEMA = 'dbo'
            ORDER BY TABLE_NAME;
            """
            
            tables_result = self.db_manager.execute_query(tables_query)
            
            schema_info = {
                "database_name": "schools-mcp-db",
                "total_tables": len(tables_result),
                "tables": {},
                "discovery_timestamp": __import__('datetime').datetime.now().isoformat()
            }
            
            # Para cada tabla, obtener estructura detallada
            for table_row in tables_result:
                table_name = table_row['TABLE_NAME']
                table_schema = self.get_table_structure(table_name)
                schema_info["tables"][table_name] = table_schema
            
            return schema_info
            
        except Exception as e:
            return {"error": f"Error discovering schema: {str(e)}"}
    
    def get_table_structure(self, table_name: str) -> Dict[str, Any]:
        """Obtiene la estructura detallada de una tabla"""
        try:
            # Query para columnas
            columns_query = f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                CHARACTER_MAXIMUM_LENGTH,
                COLUMN_DEFAULT,
                ORDINAL_POSITION
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name}'
            AND TABLE_SCHEMA = 'dbo'
            ORDER BY ORDINAL_POSITION;
            """
            
            columns_result = self.db_manager.execute_query(columns_query)
            
            # Query para claves primarias
            pk_query = f"""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_NAME = '{table_name}'
            AND CONSTRAINT_NAME LIKE 'PK_%';
            """
            
            pk_result = self.db_manager.execute_query(pk_query)
            primary_keys = [row['COLUMN_NAME'] for row in pk_result]
            
            # Query para claves foráneas
            fk_query = f"""
            SELECT 
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS rc
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu1 
                ON rc.CONSTRAINT_NAME = kcu1.CONSTRAINT_NAME
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu2 
                ON rc.UNIQUE_CONSTRAINT_NAME = kcu2.CONSTRAINT_NAME
            WHERE kcu1.TABLE_NAME = '{table_name}';
            """
            
            fk_result = self.db_manager.execute_query(fk_query)
            
            # Estructurar resultado
            table_structure = {
                "table_name": table_name,
                "columns": [],
                "primary_keys": primary_keys,
                "foreign_keys": [],
                "total_columns": len(columns_result)
            }
            
            # Procesar columnas
            for col in columns_result:
                column_info = {
                    "name": col['COLUMN_NAME'],
                    "data_type": col['DATA_TYPE'],
                    "is_nullable": col['IS_NULLABLE'] == 'YES',
                    "max_length": col['CHARACTER_MAXIMUM_LENGTH'],
                    "default_value": col['COLUMN_DEFAULT'],
                    "is_primary_key": col['COLUMN_NAME'] in primary_keys,
                    "is_foreign_key": any(fk['COLUMN_NAME'] == col['COLUMN_NAME'] for fk in fk_result)
                }
                table_structure["columns"].append(column_info)
            
            # Procesar claves foráneas
            for fk in fk_result:
                fk_info = {
                    "column": fk['COLUMN_NAME'],
                    "referenced_table": fk['REFERENCED_TABLE_NAME'],
                    "referenced_column": fk['REFERENCED_COLUMN_NAME']
                }
                table_structure["foreign_keys"].append(fk_info)
            
            return table_structure
            
        except Exception as e:
            return {"error": f"Error getting table structure: {str(e)}"}
    
    def analyze_educational_structure(self) -> Dict[str, Any]:
        """Analiza la estructura desde perspectiva educativa"""
        try:
            schema = self.discover_schema()
            if "error" in schema:
                return schema
            
            # Análisis educativo
            educational_analysis = {
                "educational_entities": {},
                "data_relationships": {},
                "potential_improvements": []
            }
            
            tables = schema.get("tables", {})
            
            # Identificar entidades educativas
            educational_keywords = {
                "centros": ["centro", "escuela", "plantel"],
                "alumnos": ["alumno", "estudiante", "matricula"],
                "docentes": ["docente", "maestro", "profesor", "personal"],
                "administrativo": ["admin", "director", "supervisor"],
                "geografia": ["municipio", "region", "zona", "sector"]
            }
            
            for table_name in tables.keys():
                for category, keywords in educational_keywords.items():
                    if any(keyword in table_name.lower() for keyword in keywords):
                        if category not in educational_analysis["educational_entities"]:
                            educational_analysis["educational_entities"][category] = []
                        educational_analysis["educational_entities"][category].append(table_name)
            
            return educational_analysis
            
        except Exception as e:
            return {"error": f"Error in educational analysis: {str(e)}"}

# Instancia global
table_inspector = TableInspector()
