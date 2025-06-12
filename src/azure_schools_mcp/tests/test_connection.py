#!/usr/bin/env python3
"""
Script mejorado para probar conexión a Azure SQL Database
Usa el logger simplificado y configuración centralizada
"""

import os
import sys
from pathlib import Path

# Añadir src al path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from azure_schools_mcp.utils import main_logger
from azure_schools_mcp.config.settings import settings

def test_azure_sql_connection():
    """Prueba la conexión a Azure SQL con logging mejorado"""
    
    main_logger.info("🔧 Iniciando test de conexión a Azure SQL Database")
    
    # Verificar configuración
    if not settings.is_database_configured():
        main_logger.error("Base de datos no configurada")
        main_logger.info("Verificar variables en .env:")
        main_logger.info("- AZURE_SQL_SERVER")
        main_logger.info("- AZURE_SQL_DATABASE") 
        main_logger.info("- AZURE_SQL_USERNAME")
        main_logger.info("- AZURE_SQL_PASSWORD")
        return False
    
    main_logger.info(f"Configuración:")
    main_logger.info(f"Servidor: {settings.database.server}")
    main_logger.info(f"Base de datos: {settings.database.database}")
    main_logger.info(f"Usuario: {settings.database.username}")
    main_logger.info(f"Driver: {settings.database.driver}")
    
    # Probar conexión usando el gestor centralizado
    try:
        from azure_schools_mcp.config.database import db_manager
        
        main_logger.info("Probando conexión...")
        
        connection_ok = db_manager.test_connection()
        
        if connection_ok:
            main_logger.info("¡Conexión exitosa!")
            return True
        else:
            main_logger.error("Error de conexión")
            return False
            
    except ImportError as e:
        main_logger.error(f"Error importando database manager: {e}")
        return False
    except Exception as e:
        main_logger.error(f"Error de conexión: {e}")
        return False

def test_basic_query():
    """Prueba una consulta básica"""
    try:
        from azure_schools_mcp.config.database import db_manager
        
        main_logger.info("Probando consulta básica...")
        
        results = db_manager.execute_query("SELECT GETDATE() as current_time")
        
        if results:
            main_logger.info(f"Consulta exitosa: {results[0]}")
            return True
        else:
            main_logger.warning("Consulta sin resultados")
            return False
            
    except Exception as e:
        main_logger.error(f"Error en consulta: {e}")
        return False

if __name__ == "__main__":
    main_logger.info("Test de conexión Azure SQL Database")
    main_logger.info("=" * 40)
    
    # Test de conexión
    connection_success = test_azure_sql_connection()
    
    if connection_success:
        # Test de consulta básica
        query_success = test_basic_query()
        
        if query_success:
            main_logger.info("¡Todos los tests exitosos!")
        else:
            main_logger.warning("Conexión OK, pero error en consulta")
    else:
        main_logger.error("Revisar configuración de base de datos")
    
    main_logger.info("=" * 40)
