"""
Database Management Module
Arquitectura evolutiva para base de datos educativa
Ernest-Alf - Junio 2025
"""

from .mcp_tools import register_database_management_tools
from .schema_registry import schema_registry
from .table_inspector import table_inspector
from .crud_generator import crud_generator

__all__ = [
    'register_database_management_tools',
    'schema_registry',
    'table_inspector', 
    'crud_generator'
]
