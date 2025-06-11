"""
CRUD Generator - Generador automático de operaciones CRUD
Sistema Educativo MCP - Ernest-Alf
"""

from typing import Dict, Any, List
import json

class CRUDGenerator:
    """Generador automático de operaciones CRUD basado en esquemas"""
    
    def __init__(self):
        pass
    
    def generate_table_operations(self, table_schema: Dict[str, Any]) -> Dict[str, str]:
        """Genera operaciones CRUD para una tabla"""
        table_name = table_schema.get('table_name')
        columns = table_schema.get('columns', [])
        
        operations = {
            "insert": self._generate_insert_operation(table_name, columns),
            "select": self._generate_select_operation(table_name, columns),
            "update": self._generate_update_operation(table_name, columns),
            "delete": self._generate_delete_operation(table_name, columns)
        }
        
        return operations
    
    def _generate_insert_operation(self, table_name: str, columns: List[Dict]) -> str:
        """Genera operación INSERT"""
        # Filtrar columnas que no son identity/auto-increment
        insertable_columns = [
            col for col in columns 
            if not col.get('is_identity', False) and col.get('name') != 'id'
        ]
        
        column_names = [col['name'] for col in insertable_columns]
        placeholders = ['?' for _ in column_names]
        
        query = f"""
        INSERT INTO {table_name} ({', '.join(column_names)})
        VALUES ({', '.join(placeholders)});
        """
        
        return query.strip()
    
    def _generate_select_operation(self, table_name: str, columns: List[Dict]) -> str:
        """Genera operación SELECT"""
        column_names = [col['name'] for col in columns]
        
        query = f"""
        SELECT {', '.join(column_names)}
        FROM {table_name}
        WHERE 1=1
        {{filters}}
        ORDER BY {columns[0]['name'] if columns else 'id'};
        """
        
        return query.strip()
    
    def _generate_update_operation(self, table_name: str, columns: List[Dict]) -> str:
        """Genera operación UPDATE"""
        # Identificar primary key
        pk_columns = [col['name'] for col in columns if col.get('is_primary_key')]
        pk_column = pk_columns[0] if pk_columns else 'id'
        
        # Filtrar columnas actualizables
        updatable_columns = [
            col for col in columns 
            if not col.get('is_primary_key', False) and col.get('name') != 'id'
        ]
        
        set_clauses = [f"{col['name']} = ?" for col in updatable_columns]
        
        query = f"""
        UPDATE {table_name}
        SET {', '.join(set_clauses)}
        WHERE {pk_column} = ?;
        """
        
        return query.strip()
    
    def _generate_delete_operation(self, table_name: str, columns: List[Dict]) -> str:
        """Genera operación DELETE"""
        # Identificar primary key
        pk_columns = [col['name'] for col in columns if col.get('is_primary_key')]
        pk_column = pk_columns[0] if pk_columns else 'id'
        
        query = f"""
        DELETE FROM {table_name}
        WHERE {pk_column} = ?;
        """
        
        return query.strip()
    
    def generate_educational_queries(self, table_name: str) -> Dict[str, str]:
        """Genera queries específicas para análisis educativo"""
        educational_queries = {}
        
        # Queries específicas según el tipo de tabla
        if 'centro' in table_name.lower() or 'escuela' in table_name.lower():
            educational_queries.update({
                "by_municipality": f"""
                    SELECT municipio, COUNT(*) as total_centros
                    FROM {table_name}
                    WHERE activo = 1
                    GROUP BY municipio
                    ORDER BY total_centros DESC;
                """,
                "by_level": f"""
                    SELECT nivel_educativo, COUNT(*) as total
                    FROM {table_name}
                    WHERE activo = 1
                    GROUP BY nivel_educativo;
                """
            })
        
        elif 'alumno' in table_name.lower() or 'matricula' in table_name.lower():
            educational_queries.update({
                "enrollment_summary": f"""
                    SELECT 
                        SUM(total_alumnos) as matricula_total,
                        AVG(total_alumnos) as promedio_por_centro
                    FROM {table_name};
                """
            })
        
        elif 'docente' in table_name.lower() or 'personal' in table_name.lower():
            educational_queries.update({
                "by_position": f"""
                    SELECT puesto, COUNT(*) as total
                    FROM {table_name}
                    WHERE activo = 1
                    GROUP BY puesto;
                """
            })
        
        return educational_queries

# Instancia global
crud_generator = CRUDGenerator()
