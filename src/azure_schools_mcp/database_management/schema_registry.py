"""
Schema Registry - Registro central de esquemas de BD
Sistema Educativo MCP - Ernest-Alf
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ColumnSchema:
    """Esquema de una columna"""
    name: str
    data_type: str
    is_nullable: bool
    max_length: Optional[int] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_table: Optional[str] = None
    default_value: Optional[str] = None
    description: Optional[str] = None

@dataclass
class TableSchema:
    """Esquema de una tabla"""
    table_name: str
    columns: List[ColumnSchema]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    indexes: List[str]
    description: Optional[str] = None
    business_purpose: Optional[str] = None

class SchemaRegistry:
    """Registro central de esquemas de base de datos"""
    
    def __init__(self):
        self.schemas_dir = Path(__file__).parent / "schemas"
        self.schemas_dir.mkdir(exist_ok=True)
        self.current_schema_file = self.schemas_dir / "current_schema.json"
        self.version_history_file = self.schemas_dir / "version_history.json"
        
        # Cache en memoria
        self._schema_cache = {}
        self._load_schema_cache()
    
    def _load_schema_cache(self):
        """Carga esquemas en cache"""
        try:
            if self.current_schema_file.exists():
                with open(self.current_schema_file, 'r', encoding='utf-8') as f:
                    self._schema_cache = json.load(f)
        except Exception as e:
            print(f"Warning: Error loading schema cache: {e}")
            self._schema_cache = {}
    
    def get_all_tables(self) -> Dict[str, Any]:
        """Obtiene todos los esquemas de tabla"""
        return self._schema_cache.get('tables', {})
    
    def get_table_schema(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene el esquema de una tabla específica"""
        tables = self.get_all_tables()
        return tables.get(table_name)
    
    def register_table_schema(self, table_schema: Dict[str, Any]) -> bool:
        """Registra o actualiza el esquema de una tabla"""
        try:
            table_name = table_schema.get('table_name')
            if not table_name:
                return False
            
            # Inicializar estructura si no existe
            if 'tables' not in self._schema_cache:
                self._schema_cache['tables'] = {}
            
            # Registrar timestamp
            table_schema['last_updated'] = datetime.now().isoformat()
            
            # Guardar en cache
            self._schema_cache['tables'][table_name] = table_schema
            
            # Persistir a archivo
            self._save_schema_cache()
            
            return True
            
        except Exception as e:
            print(f"Error registering table schema: {e}")
            return False
    
    def get_relationships(self) -> Dict[str, List[Dict[str, str]]]:
        """Obtiene todas las relaciones entre tablas"""
        relationships = {}
        tables = self.get_all_tables()
        
        for table_name, table_schema in tables.items():
            table_relationships = []
            foreign_keys = table_schema.get('foreign_keys', [])
            
            for fk in foreign_keys:
                table_relationships.append({
                    'type': 'foreign_key',
                    'local_column': fk.get('column'),
                    'foreign_table': fk.get('referenced_table'),
                    'foreign_column': fk.get('referenced_column')
                })
            
            if table_relationships:
                relationships[table_name] = table_relationships
        
        return relationships
    
    def export_schema_documentation(self) -> str:
        """Exporta documentación completa del esquema"""
        tables = self.get_all_tables()
        relationships = self.get_relationships()
        
        doc_lines = [
            "# DOCUMENTACIÓN DEL ESQUEMA DE BASE DE DATOS",
            "# Sistema Educativo MCP",
            f"# Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"## RESUMEN",
            f"- Total de tablas: {len(tables)}",
            f"- Total de relaciones: {sum(len(rels) for rels in relationships.values())}",
            ""
        ]
        
        # Documentar cada tabla
        for table_name, table_schema in tables.items():
            doc_lines.extend([
                f"## TABLA: {table_name}",
                f"**Propósito**: {table_schema.get('description', 'No especificado')}",
                "",
                "### Columnas:",
            ])
            
            columns = table_schema.get('columns', [])
            for col in columns:
                pk_marker = " (PK)" if col.get('is_primary_key') else ""
                fk_marker = f" (FK → {col.get('foreign_table')})" if col.get('is_foreign_key') else ""
                nullable = "NULL" if col.get('is_nullable') else "NOT NULL"
                
                doc_lines.append(f"- **{col.get('name')}**: {col.get('data_type')} {nullable}{pk_marker}{fk_marker}")
            
            doc_lines.append("")
        
        return "\n".join(doc_lines)
    
    def _save_schema_cache(self):
        """Guarda cache a archivo"""
        try:
            # Agregar metadata
            self._schema_cache['metadata'] = {
                'version': '1.0',
                'last_updated': datetime.now().isoformat(),
                'generator': 'Sistema Educativo MCP'
            }
            
            with open(self.current_schema_file, 'w', encoding='utf-8') as f:
                json.dump(self._schema_cache, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving schema cache: {e}")

# Instancia global
schema_registry = SchemaRegistry()
