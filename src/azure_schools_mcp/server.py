#!/usr/bin/env python3
"""
Servidor MCP para leer archivos Excel usando FastMCP
"""

import json
import pandas as pd
from pathlib import Path
from typing import Optional

# Importar FastMCP del SDK oficial
from mcp.server.fastmcp import FastMCP

# Crear el servidor MCP
mcp = FastMCP("excel-reader-mcp")

# Directorio donde están los archivos Excel
EXCEL_DIR = Path(__file__).parent.parent.parent / "excel_files"


@mcp.tool()
def list_excel_files() -> str:
    """Lista todos los archivos Excel (.xlsx, .xls) en la carpeta excel_files"""
    try:
        # Crear directorio si no existe
        EXCEL_DIR.mkdir(exist_ok=True)
        
        # Buscar archivos Excel
        excel_extensions = ['.xlsx', '.xls', '.xlsm']
        excel_files = []
        
        for ext in excel_extensions:
            excel_files.extend(EXCEL_DIR.glob(f"*{ext}"))
        
        if not excel_files:
            return "No se encontraron archivos Excel en la carpeta excel_files/"
        
        # Crear lista con información de archivos
        file_list = []
        for file_path in excel_files:
            file_stat = file_path.stat()
            file_info = {
                "nombre": file_path.name,
                "tamaño_mb": round(file_stat.st_size / (1024 * 1024), 2),
                "modificado": str(file_stat.st_mtime)
            }
            file_list.append(file_info)
        
        result = {
            "total_archivos": len(file_list),
            "archivos": file_list
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"Error al listar archivos Excel: {str(e)}"


@mcp.tool()
def read_excel_file(filename: str, sheet_name: Optional[str] = None, max_rows: int = 10, header_row: int = 0) -> str:
    """Lee un archivo Excel y devuelve su contenido.
    
    Args:
        filename: Nombre del archivo Excel a leer
        sheet_name: Nombre de la hoja a leer (opcional)
        max_rows: Número máximo de filas a devolver (por defecto 10)
        header_row: Fila donde están los headers (por defecto 0, para filtros usar 2)
    """
    try:
        file_path = EXCEL_DIR / filename
        
        if not file_path.exists():
            return f"Error: El archivo '{filename}' no existe en excel_files/"
        
        # Leer archivo Excel
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row, nrows=max_rows)
        else:
            df = pd.read_excel(file_path, header=header_row, nrows=max_rows)
        
        # Convertir a formato legible
        result = {
            "archivo": filename,
            "hoja": sheet_name or "primera_hoja",
            "header_row": header_row,
            "dimensiones": {
                "filas_mostradas": len(df),
                "columnas": len(df.columns)
            },
            "columnas": list(df.columns),
            "datos": df.to_dict(orient="records"),
            "tipos_datos": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False, default=str)
        
    except Exception as e:
        return f"Error al leer archivo Excel '{filename}': {str(e)}"


@mcp.tool()
def read_schools_data(filename: str, max_rows: int = 20) -> str:
    """Lee específicamente datos de centros de trabajo/escuelas con headers correctos.
    
    Args:
        filename: Nombre del archivo Excel de centros de trabajo
        max_rows: Número máximo de filas a devolver (por defecto 20)
    """
    try:
        file_path = EXCEL_DIR / filename
        
        if not file_path.exists():
            return f"Error: El archivo '{filename}' no existe en excel_files/"
        
        # Leer archivo con header en fila 2 (índice 2)
        df = pd.read_excel(file_path, header=2, nrows=max_rows)
        
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        
        # Convertir a formato legible
        result = {
            "archivo": filename,
            "descripcion": "Datos de centros de trabajo educativos",
            "dimensiones": {
                "filas_mostradas": len(df),
                "columnas": len(df.columns)
            },
            "columnas": list(df.columns),
            "centros_trabajo": df.to_dict(orient="records"),
            "estadisticas": {
                "niveles_unicos": df['Nivel'].unique().tolist() if 'Nivel' in df.columns else [],
                "municipios_unicos": df['Municipio'].unique().tolist()[:10] if 'Municipio' in df.columns else [],
                "total_matricula": int(df['Suma de Matrícula'].sum()) if 'Suma de Matrícula' in df.columns else 0
            }
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False, default=str)
        
    except Exception as e:
        return f"Error al leer datos de escuelas '{filename}': {str(e)}"


@mcp.tool()
def get_excel_info(filename: str) -> str:
    """Obtiene información sobre un archivo Excel (hojas, dimensiones, etc.).
    
    Args:
        filename: Nombre del archivo Excel
    """
    try:
        file_path = EXCEL_DIR / filename
        
        if not file_path.exists():
            return f"Error: El archivo '{filename}' no existe en excel_files/"
        
        # Leer información del archivo
        excel_file = pd.ExcelFile(file_path)
        
        # Obtener información de cada hoja
        sheets_info = {}
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            sheets_info[sheet_name] = {
                "filas": len(df),
                "columnas": len(df.columns),
                "nombres_columnas": list(df.columns)
            }
        
        # Información del archivo
        file_stat = file_path.stat()
        
        result = {
            "archivo": filename,
            "tamaño_mb": round(file_stat.st_size / (1024 * 1024), 2),
            "total_hojas": len(excel_file.sheet_names),
            "nombres_hojas": excel_file.sheet_names,
            "informacion_hojas": sheets_info
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"Error al obtener información del archivo '{filename}': {str(e)}"


@mcp.tool()
def excel_summary(filename: str, sheet_name: Optional[str] = None) -> str:
    """Obtiene un resumen estadístico de un archivo Excel.
    
    Args:
        filename: Nombre del archivo Excel
        sheet_name: Nombre de la hoja (opcional)
    """
    try:
        file_path = EXCEL_DIR / filename
        
        if not file_path.exists():
            return f"Error: El archivo '{filename}' no existe en excel_files/"
        
        # Leer archivo
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(file_path)
        
        # Generar resumen estadístico
        numeric_cols = df.select_dtypes(include='number').columns
        
        summary = {
            "archivo": filename,
            "hoja": sheet_name or "primera_hoja",
            "dimensiones": {
                "filas": len(df),
                "columnas": len(df.columns)
            },
            "estadisticas_numericas": df[numeric_cols].describe().to_dict() if len(numeric_cols) > 0 else "Sin columnas numéricas",
            "valores_nulos": df.isnull().sum().to_dict(),
            "tipos_datos": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "muestra_datos": df.head(3).to_dict(orient="records")
        }
        
        return json.dumps(summary, indent=2, ensure_ascii=False, default=str)
        
    except Exception as e:
        return f"Error al generar resumen de '{filename}': {str(e)}"


# Función de prueba para verificar que el servidor funciona
def test_server():
    """Prueba básica del servidor MCP"""
    print("🧪 Probando servidor MCP Excel...")
    
    # Verificar directorio
    EXCEL_DIR.mkdir(exist_ok=True)
    print(f"📁 Directorio Excel: {EXCEL_DIR}")
    
    # Probar listado de archivos
    try:
        result = list_excel_files()
        print("✅ list_excel_files() funciona")
        print(f"📄 Resultado: {result[:100]}...")
    except Exception as e:
        print(f"❌ Error en list_excel_files(): {e}")
    
    print("🚀 Servidor MCP listo para ejecutar")


if __name__ == "__main__":
    # Si se ejecuta con argumento 'test', hacer pruebas
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_server()
    else:
        # Ejecutar servidor MCP normal
        print("🚀 Iniciando servidor MCP Excel...")
        mcp.run()