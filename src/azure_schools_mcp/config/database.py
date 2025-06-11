"""
Configuración y utilidades para Azure SQL Database
"""

import pyodbc
from typing import Optional, List, Dict, Any
from .settings import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de conexiones a Azure SQL Database"""
    
    def __init__(self):
        self._connection_string = settings.get_connection_string()
        self._connection: Optional[pyodbc.Connection] = None
    
    def get_connection(self) -> Optional[pyodbc.Connection]:
        """Obtiene conexión a la base de datos"""
        try:
            if not self._connection_string:
                logger.error("String de conexión no configurado")
                return None
            
            self._connection = pyodbc.connect(self._connection_string)
            return self._connection
        
        except Exception as e:
            logger.error(f"Error conectando a base de datos: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos"""
        try:
            conn = self.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                conn.close()
                return result is not None
            return False
        
        except Exception as e:
            logger.error(f"Error en test de conexión: {e}")
            return False
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Ejecuta una consulta y retorna resultados"""
        try:
            conn = self.get_connection()
            if not conn:
                return []
            
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Obtener nombres de columnas
            columns = [column[0] for column in cursor.description]
            
            # Obtener datos
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            return results
        
        except Exception as e:
            logger.error(f"Error ejecutando consulta: {e}")
            return []

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()
