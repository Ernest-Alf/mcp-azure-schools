"""
Configuración centralizada del Sistema Educativo MCP
"""

from dataclasses import dataclass
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

@dataclass
class DatabaseConfig:
    """Configuración de Azure SQL Database"""
    server: str
    database: str
    username: str
    password: str
    connection_timeout: int = 30
    driver: str = "ODBC Driver 17 for SQL Server"

@dataclass
class ExcelConfig:
    """Configuración para procesamiento de archivos Excel"""
    max_file_size_mb: int = 100
    supported_extensions: List[str] = None
    default_sheet: str = None
    max_rows_per_query: int = 10000
    
    def __post_init__(self):
        if self.supported_extensions is None:
            self.supported_extensions = ['.xlsx', '.xls', '.xlsm']

@dataclass
class SystemConfig:
    """Configuración general del sistema"""
    log_level: str = "INFO"
    max_rows_default: int = 1000
    cache_enabled: bool = True
    cache_ttl_minutes: int = 30
    debug_mode: bool = False

@dataclass
class MCPConfig:
    """Configuración específica de MCP"""
    server_name: str = "azure-schools-mcp"
    max_tools: int = 50
    timeout_seconds: int = 30

class Settings:
    """Clase principal de configuración"""
    
    def __init__(self):
        # Configuración de base de datos
        self.database = DatabaseConfig(
            server=os.getenv('AZURE_SQL_SERVER', ''),
            database=os.getenv('AZURE_SQL_DATABASE', ''),
            username=os.getenv('AZURE_SQL_USERNAME', ''),
            password=os.getenv('AZURE_SQL_PASSWORD', '')
        )
        
        # Configuración de Excel
        self.excel = ExcelConfig()
        
        # Configuración del sistema
        self.system = SystemConfig(
            log_level=os.getenv('MCP_LOG_LEVEL', 'INFO'),
            max_rows_default=int(os.getenv('MAX_ROWS_DEFAULT', '1000')),
            debug_mode=os.getenv('DEBUG', 'false').lower() == 'true'
        )
        
        # Configuración MCP
        self.mcp = MCPConfig(
            server_name=os.getenv('MCP_SERVER_NAME', 'azure-schools-mcp')
        )
    
    def is_database_configured(self) -> bool:
        """Verifica si la base de datos está configurada"""
        return all([
            self.database.server,
            self.database.database,
            self.database.username,
            self.database.password
        ])
    
    def get_connection_string(self) -> str:
        """Genera string de conexión para Azure SQL"""
        if not self.is_database_configured():
            return ""
        
        return (
            f"Driver={{{self.database.driver}}};"
            f"Server=tcp:{self.database.server},1433;"
            f"Database={self.database.database};"
            f"Uid={self.database.username};"
            f"Pwd={self.database.password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout={self.database.connection_timeout};"
        )

# Instancia global de configuración
settings = Settings()
