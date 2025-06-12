#!/usr/bin/env python3
"""
Tests unitarios básicos para el Sistema Educativo MCP
"""

import sys
import unittest
from pathlib import Path

# Añadir src al path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from azure_schools_mcp.utils import main_logger, validate_excel_file_basic, FileManager

class TestBasicFunctionality(unittest.TestCase):
    """Tests básicos de funcionalidad"""
    
    def setUp(self):
        """Configuración para cada test"""
        main_logger.info("🧪 Iniciando test unitario")
        self.project_root = project_root
        self.excel_dir = self.project_root / "excel_files"
    
    def test_logger_functionality(self):
        """Test del sistema de logging"""
        main_logger.info("📝 Test de logging")
        main_logger.debug("Debug message")
        main_logger.warning("Warning message")
        self.assertTrue(True)  # Si llegamos aquí, el logger funciona
    
    def test_file_manager(self):
        """Test del gestor de archivos"""
        main_logger.info("📁 Test de FileManager")
        
        # Test de ensure_directory
        test_dir = self.project_root / "test_temp"
        result = FileManager.ensure_directory(test_dir)
        self.assertTrue(result)
        self.assertTrue(test_dir.exists())
        
        # Limpiar
        test_dir.rmdir()
    
    def test_excel_directory_detection(self):
        """Test de detección de directorio Excel"""
        main_logger.info("📊 Test de directorio Excel")
        
        if self.excel_dir.exists():
            excel_files = FileManager.list_excel_files(self.excel_dir)
            main_logger.info(f"Encontrados {len(excel_files)} archivos Excel")
            self.assertIsInstance(excel_files, list)
        else:
            main_logger.warning("Directorio Excel no existe - creando para test")
            FileManager.ensure_directory(self.excel_dir)
            self.assertTrue(self.excel_dir.exists())
    
    def test_configuration_import(self):
        """Test de importación de configuración"""
        main_logger.info("⚙️ Test de configuración")
        
        try:
            from azure_schools_mcp.config.settings import settings
            self.assertIsNotNone(settings)
            main_logger.info("✅ Configuración importada correctamente")
        except ImportError as e:
            main_logger.error(f"❌ Error importando configuración: {e}")
            self.fail("No se pudo importar configuración")
    
    def test_shared_extractor_import(self):
        """Test de importación del extractor centralizado"""
        main_logger.info("🔧 Test de extractor centralizado")
        
        try:
            from azure_schools_mcp.shared.excel_extractor import get_excel_extractor
            extractor = get_excel_extractor()
            self.assertIsNotNone(extractor)
            main_logger.info("✅ Extractor centralizado importado correctamente")
        except ImportError as e:
            main_logger.error(f"❌ Error importando extractor: {e}")
            self.fail("No se pudo importar extractor centralizado")

if __name__ == "__main__":
    main_logger.info("🧪 Ejecutando tests unitarios del Sistema Educativo MCP")
    main_logger.info("=" * 50)
    
    unittest.main(verbosity=2)
