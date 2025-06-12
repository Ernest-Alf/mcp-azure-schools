#!/usr/bin/env python3
"""
Script para ejecutar todos los tests del sistema
"""

import sys
from pathlib import Path

# Añadir src al path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from azure_schools_mcp.utils import main_logger

def run_connection_test():
    """Ejecuta test de conexión"""
    main_logger.info("🔗 Ejecutando test de conexión...")
    try:
        from .test_connection import test_azure_sql_connection
        return test_azure_sql_connection()
    except Exception as e:
        main_logger.error(f"Error en test de conexión: {e}")
        return False

def run_unit_tests():
    """Ejecuta tests unitarios"""
    main_logger.info("🧪 Ejecutando tests unitarios...")
    try:
        import unittest
        from .unit_tests import TestBasicFunctionality
        
        suite = unittest.TestLoader().loadTestsFromTestCase(TestBasicFunctionality)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return result.wasSuccessful()
    except Exception as e:
        main_logger.error(f"Error en tests unitarios: {e}")
        return False

def run_system_diagnostics():
    """Ejecuta diagnósticos del sistema"""
    main_logger.info("🔧 Ejecutando diagnósticos del sistema...")
    try:
        from .diagnostics import system_diagnostics
        status = system_diagnostics.get_system_status()
        main_logger.info("✅ Diagnósticos completados")
        return True
    except Exception as e:
        main_logger.error(f"Error en diagnósticos: {e}")
        return False

if __name__ == "__main__":
    main_logger.info("🚀 EJECUTANDO SUITE COMPLETA DE TESTS")
    main_logger.info("=" * 50)
    
    results = {
        "unit_tests": run_unit_tests(),
        "system_diagnostics": run_system_diagnostics(),
        "connection_test": run_connection_test()
    }
    
    main_logger.info("=" * 50)
    main_logger.info("📊 RESULTADOS:")
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        main_logger.info(f"   {test_name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        main_logger.info("🎉 ¡TODOS LOS TESTS EXITOSOS!")
    else:
        main_logger.warning("⚠️ Algunos tests fallaron - revisar logs")
    
    main_logger.info("=" * 50)
