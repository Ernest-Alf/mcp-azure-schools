"""
Modules Package
Todos los módulos MCP del Sistema Educativo
"""

from .diagnostics import register_diagnostics_tools
from .excel_tools import register_excel_tools  
from .database_crud import register_database_crud_tools

__all__ = [
    'register_diagnostics_tools',
    'register_excel_tools', 
    'register_database_crud_tools'
]
