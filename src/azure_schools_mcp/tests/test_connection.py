#!/usr/bin/env python3
"""
Script para probar la conexión a Azure SQL Database
"""

import os
import pyodbc
from dotenv import load_dotenv

def test_connection():
    """Prueba la conexión a Azure SQL Database"""
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener configuración
    server = os.getenv('AZURE_SQL_SERVER')
    database = os.getenv('AZURE_SQL_DATABASE') 
    username = os.getenv('AZURE_SQL_USERNAME')
    password = os.getenv('AZURE_SQL_PASSWORD')
    
    print("🔧 Configuración:")
    print(f"   Servidor: {server}")
    print(f"   Base de datos: {database}")
    print(f"   Usuario: {username}")
    print(f"   Contraseña: {'*' * len(password) if password else 'No configurada'}")
    print()
    
    # Construir cadena de conexión
    connection_string = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
    
    try:
        print("�� Intentando conectar...")
        
        # Probar conexión
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            
            print("✅ ¡Conexión exitosa!")
            print(f"   Resultado de prueba: {result[0]}")
            
        return True
        
    except Exception as e:
        print("❌ Error de conexión:")
        print(f"   {str(e)}")
        return False

if __name__ == "__main__":
    print("�� Probando conexión a Azure SQL Database...\n")
    success = test_connection()
    
    if success:
        print("\n🎉 ¡Todo listo para continuar!")
    else:
        print("\n🔧 Revisa la configuración en el archivo .env")
