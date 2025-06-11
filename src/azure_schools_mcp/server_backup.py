#!/usr/bin/env python3
"""
Sistema Educativo MCP - Servidor para análisis de datos educativos
Automatización y análisis usando Model Context Protocol (MCP) y Azure SQL Database
"""

import json
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
import os
import sys

# Cargar variables de entorno de forma segura
from dotenv import load_dotenv
load_dotenv()  # Carga el archivo .env

# Importar FastMCP del SDK oficial
from mcp.server.fastmcp import FastMCP

# Crear el servidor MCP
mcp = FastMCP("azure-schools-mcp")

# Configuración desde variables de entorno
EXCEL_DIR = Path(__file__).parent.parent.parent / "excel_files"
AZURE_SQL_SERVER = os.getenv('AZURE_SQL_SERVER')
AZURE_SQL_DATABASE = os.getenv('AZURE_SQL_DATABASE')
AZURE_SQL_USERNAME = os.getenv('AZURE_SQL_USERNAME')
AZURE_SQL_PASSWORD = os.getenv('AZURE_SQL_PASSWORD')
MAX_ROWS_DEFAULT = int(os.getenv('MAX_ROWS_DEFAULT', '1000'))
MCP_LOG_LEVEL = os.getenv('MCP_LOG_LEVEL', 'info')

# Almacén global para DataFrames cargados
SCHOOLS_DATA: Dict[str, pd.DataFrame] = {}

# =================================
# HERRAMIENTAS DE DIAGNÓSTICO
# =================================

@mcp.tool()
def debug_info() -> str:
    """Información de diagnóstico del Sistema Educativo MCP."""
    info = [
        f"🎓 Sistema Educativo MCP - Diagnóstico Completo:",
        f"=" * 50,
        f"📂 Directorio de trabajo: {os.getcwd()}",
        f"📁 Carpeta Excel: {EXCEL_DIR}",
        f"✅ Carpeta Excel existe: {EXCEL_DIR.exists()}",
        f"📊 DataFrames en memoria: {len(SCHOOLS_DATA)}",
        f"🔧 Nivel de log: {MCP_LOG_LEVEL}",
        f"📋 Max filas por defecto: {MAX_ROWS_DEFAULT}",
        f""
    ]
    
    # Información de conexión Azure SQL (sin mostrar credenciales)
    info.extend([
        f"🗄️  CONFIGURACIÓN AZURE SQL:",
        f"   Servidor: {AZURE_SQL_SERVER or '❌ No configurado'}",
        f"   Base de datos: {AZURE_SQL_DATABASE or '❌ No configurada'}",
        f"   Usuario: {'✅ Configurado' if AZURE_SQL_USERNAME else '❌ No configurado'}",
        f"   Password: {'✅ Configurado' if AZURE_SQL_PASSWORD else '❌ No configurado'}",
        f""
    ])
    
    # Información de archivos Excel
    if EXCEL_DIR.exists():
        archivos_excel = list(EXCEL_DIR.glob("*.xlsx"))
        info.append(f"📊 ARCHIVOS EXCEL DISPONIBLES: {len(archivos_excel)}")
        for i, archivo in enumerate(archivos_excel, 1):
            size_mb = archivo.stat().st_size / (1024 * 1024)
            info.append(f"   {i}. 📄 {archivo.name} ({size_mb:.2f} MB)")
    else:
        info.append(f"❌ Directorio Excel no existe: {EXCEL_DIR}")
    
    # DataFrames cargados
    if SCHOOLS_DATA:
        info.append(f"\n💾 DATAFRAMES EN MEMORIA:")
        for key, df in SCHOOLS_DATA.items():
            info.append(f"   📊 {key}: {len(df):,} filas × {len(df.columns)} columnas")
    
    return "\n".join(info)

# =================================
# HERRAMIENTAS DE ARCHIVOS EXCEL
# =================================

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
            return f"📁 No se encontraron archivos Excel en {EXCEL_DIR}\n💡 Coloca tus archivos .xlsx en esta carpeta para analizarlos."
        
        # Crear lista con información detallada de archivos
        file_list = []
        for file_path in excel_files:
            file_stat = file_path.stat()
            file_info = {
                "nombre": file_path.name,
                "tamaño_mb": round(file_stat.st_size / (1024 * 1024), 2),
                "modificado": pd.Timestamp.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            }
            file_list.append(file_info)
        
        # Ordenar por fecha de modificación
        file_list.sort(key=lambda x: x['modificado'], reverse=True)
        
        result = {
            "directorio": str(EXCEL_DIR),
            "total_archivos": len(file_list),
            "archivos": file_list
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"❌ Error al listar archivos Excel: {str(e)}"

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
            available_files = [f.name for f in EXCEL_DIR.glob("*.xlsx")]
            return f"❌ El archivo '{filename}' no existe en excel_files/\n📋 Archivos disponibles: {available_files}"
        
        # Leer archivo Excel
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row, nrows=max_rows)
        else:
            df = pd.read_excel(file_path, header=header_row, nrows=max_rows)
        
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        
        # Convertir a formato legible
        result = {
            "archivo": filename,
            "hoja": sheet_name or "primera_hoja",
            "header_row": header_row,
            "dimensiones": {
                "filas_mostradas": len(df),
                "columnas": len(df.columns),
                "filas_totales_estimadas": "📊 Usa get_excel_info() para ver dimensiones completas"
            },
            "columnas": list(df.columns),
            "datos": df.to_dict(orient="records"),
            "tipos_datos": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False, default=str)
        
    except Exception as e:
        return f"❌ Error al leer archivo Excel '{filename}': {str(e)}"

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
            available_files = [f.name for f in EXCEL_DIR.glob("*.xlsx")]
            return f"❌ El archivo '{filename}' no existe en excel_files/\n📋 Archivos disponibles: {available_files}"
        
        # Leer archivo con header en fila 2 (índice 2) - común en archivos de centros educativos
        df = pd.read_excel(file_path, header=2, nrows=max_rows)
        
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        
        # Guardar en memoria para uso posterior
        key = f"schools_{filename.replace('.xlsx', '')}"
        SCHOOLS_DATA[key] = df.copy()
        
        # Análisis automático de datos educativos
        estadisticas = {}
        
        # Detectar columnas importantes
        col_nivel = next((col for col in df.columns if 'nivel' in col.lower()), None)
        col_municipio = next((col for col in df.columns if 'municipio' in col.lower()), None)
        col_matricula = next((col for col in df.columns if 'matrícula' in col.lower() or 'matricula' in col.lower()), None)
        col_sostenimiento = next((col for col in df.columns if 'sostenimiento' in col.lower()), None)
        
        if col_nivel:
            estadisticas["niveles_educativos"] = df[col_nivel].value_counts().to_dict()
        if col_municipio:
            estadisticas["municipios"] = df[col_municipio].value_counts().head(10).to_dict()
        if col_matricula:
            estadisticas["matricula_total"] = int(df[col_matricula].sum()) if df[col_matricula].dtype in ['int64', 'float64'] else "No numérica"
        if col_sostenimiento:
            estadisticas["sostenimiento"] = df[col_sostenimiento].value_counts().to_dict()
        
        # Convertir a formato legible
        result = {
            "archivo": filename,
            "descripcion": "📚 Datos de centros de trabajo educativos",
            "cargado_en_memoria": key,
            "dimensiones": {
                "filas_mostradas": len(df),
                "columnas": len(df.columns),
                "mensaje": f"💾 Datos guardados como '{key}' para análisis posterior"
            },
            "columnas_detectadas": {
                "nivel": col_nivel,
                "municipio": col_municipio,
                "matricula": col_matricula,
                "sostenimiento": col_sostenimiento
            },
            "columnas_completas": list(df.columns),
            "centros_trabajo": df.to_dict(orient="records"),
            "estadisticas_automaticas": estadisticas
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False, default=str)
        
    except Exception as e:
        return f"❌ Error al leer datos de escuelas '{filename}': {str(e)}"

@mcp.tool()
def get_excel_info(filename: str) -> str:
    """Obtiene información completa sobre un archivo Excel (hojas, dimensiones, etc.).
    
    Args:
        filename: Nombre del archivo Excel
    """
    try:
        file_path = EXCEL_DIR / filename
        
        if not file_path.exists():
            available_files = [f.name for f in EXCEL_DIR.glob("*.xlsx")]
            return f"❌ El archivo '{filename}' no existe en excel_files/\n📋 Archivos disponibles: {available_files}"
        
        # Leer información del archivo
        excel_file = pd.ExcelFile(file_path)
        
        # Obtener información de cada hoja
        sheets_info = {}
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            sheets_info[sheet_name] = {
                "filas": len(df),
                "columnas": len(df.columns),
                "nombres_columnas": list(df.columns),
                "tipos_datos": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "valores_nulos": df.isnull().sum().to_dict(),
                "muestra_primera_fila": df.head(1).to_dict(orient="records") if len(df) > 0 else []
            }
        
        # Información del archivo
        file_stat = file_path.stat()
        
        result = {
            "archivo": filename,
            "ruta_completa": str(file_path),
            "tamaño_mb": round(file_stat.st_size / (1024 * 1024), 2),
            "modificado": pd.Timestamp.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
            "total_hojas": len(excel_file.sheet_names),
            "nombres_hojas": excel_file.sheet_names,
            "informacion_detallada_hojas": sheets_info,
            "recomendacion": "💡 Usa read_schools_data() para datos educativos con formato estándar"
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"❌ Error al obtener información del archivo '{filename}': {str(e)}"

@mcp.tool()
def excel_summary(filename: str, sheet_name: Optional[str] = None) -> str:
    """Obtiene un resumen estadístico completo de un archivo Excel.
    
    Args:
        filename: Nombre del archivo Excel
        sheet_name: Nombre de la hoja (opcional)
    """
    try:
        file_path = EXCEL_DIR / filename
        
        if not file_path.exists():
            available_files = [f.name for f in EXCEL_DIR.glob("*.xlsx")]
            return f"❌ El archivo '{filename}' no existe en excel_files/\n📋 Archivos disponibles: {available_files}"
        
        # Leer archivo completo
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(file_path)
        
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        
        # Análisis estadístico completo
        numeric_cols = df.select_dtypes(include='number').columns
        text_cols = df.select_dtypes(include='object').columns
        
        # Estadísticas numéricas
        numeric_stats = {}
        if len(numeric_cols) > 0:
            numeric_stats = df[numeric_cols].describe().to_dict()
        
        # Estadísticas de texto
        text_stats = {}
        for col in text_cols:
            text_stats[col] = {
                "valores_unicos": df[col].nunique(),
                "valor_mas_comun": df[col].mode().iloc[0] if len(df[col].mode()) > 0 else None,
                "frecuencia_mas_comun": df[col].value_counts().iloc[0] if len(df) > 0 else 0
            }
        
        summary = {
            "archivo": filename,
            "hoja": sheet_name or "primera_hoja",
            "fecha_analisis": pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            "dimensiones": {
                "filas_totales": len(df),
                "columnas_totales": len(df.columns),
                "columnas_numericas": len(numeric_cols),
                "columnas_texto": len(text_cols)
            },
            "estadisticas_numericas": numeric_stats,
            "estadisticas_texto": text_stats,
            "valores_nulos_por_columna": df.isnull().sum().to_dict(),
            "porcentaje_nulos": ((df.isnull().sum() / len(df)) * 100).round(2).to_dict(),
            "tipos_datos": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "muestra_datos": df.head(3).to_dict(orient="records"),
            "memoria_utilizada_kb": round(df.memory_usage(deep=True).sum() / 1024, 2)
        }
        
        return json.dumps(summary, indent=2, ensure_ascii=False, default=str)
        
    except Exception as e:
        return f"❌ Error al generar resumen de '{filename}': {str(e)}"

# =================================
# HERRAMIENTAS DE ANÁLISIS AVANZADO
# =================================

@mcp.tool()
def analyze_schools_by_municipality(data_key: str) -> str:
    """Analiza centros educativos agrupados por municipio.
    
    Args:
        data_key: Clave del DataFrame cargado (ej: 'schools_Centro_de_trabajo_1')
    """
    try:
        if data_key not in SCHOOLS_DATA:
            available_keys = list(SCHOOLS_DATA.keys())
            return f"❌ Dataset '{data_key}' no encontrado.\n📋 Datasets disponibles: {available_keys}\n💡 Usa read_schools_data() primero."
        
        df = SCHOOLS_DATA[data_key]
        
        # Detectar columna de municipio
        col_municipio = next((col for col in df.columns if 'municipio' in col.lower()), None)
        col_matricula = next((col for col in df.columns if 'matrícula' in col.lower() or 'matricula' in col.lower()), None)
        col_nivel = next((col for col in df.columns if 'nivel' in col.lower()), None)
        
        if not col_municipio:
            return f"❌ No se encontró columna de municipio en el dataset.\n📋 Columnas disponibles: {list(df.columns)}"
        
        # Análisis por municipio
        municipio_stats = df.groupby(col_municipio).agg({
            col_municipio: 'count'  # Contador de centros
        }).rename(columns={col_municipio: 'total_centros'})
        
        # Agregar matrícula si está disponible
        if col_matricula and df[col_matricula].dtype in ['int64', 'float64']:
            municipio_stats['total_matricula'] = df.groupby(col_municipio)[col_matricula].sum()
            municipio_stats['promedio_matricula'] = df.groupby(col_municipio)[col_matricula].mean().round(1)
        
        # Agregar análisis por nivel educativo si está disponible
        nivel_por_municipio = {}
        if col_nivel:
            nivel_cross = pd.crosstab(df[col_municipio], df[col_nivel])
            nivel_por_municipio = nivel_cross.to_dict()
        
        result = {
            "dataset": data_key,
            "columna_municipio": col_municipio,
            "total_municipios": len(municipio_stats),
            "estadisticas_por_municipio": municipio_stats.to_dict(),
            "distribución_niveles_por_municipio": nivel_por_municipio,
            "resumen_general": {
                "municipio_con_mas_centros": municipio_stats['total_centros'].idxmax(),
                "max_centros": int(municipio_stats['total_centros'].max()),
                "municipio_con_menos_centros": municipio_stats['total_centros'].idxmin(),
                "min_centros": int(municipio_stats['total_centros'].min())
            }
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False, default=str)
        
    except Exception as e:
        return f"❌ Error en análisis por municipio: {str(e)}"

@mcp.tool()
def list_loaded_datasets() -> str:
    """Lista todos los datasets cargados en memoria con información básica."""
    if not SCHOOLS_DATA:
        return "📭 No hay datasets cargados en memoria.\n💡 Usa read_schools_data() para cargar datos de centros educativos."
    
    datasets_info = []
    for key, df in SCHOOLS_DATA.items():
        info = {
            "dataset": key,
            "filas": len(df),
            "columnas": len(df.columns),
            "columnas_principales": list(df.columns)[:5],  # Primeras 5 columnas
            "memoria_kb": round(df.memory_usage(deep=True).sum() / 1024, 2)
        }
        datasets_info.append(info)
    
    result = {
        "total_datasets": len(SCHOOLS_DATA),
        "datasets_cargados": datasets_info,
        "herramientas_disponibles": [
            "analyze_schools_by_municipality()",
            "query_schools_data()",
            "export_school_summary()"
        ]
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)

# =================================
# FUNCIÓN DE PRUEBA
# =================================

def test_server():
    """Prueba básica del servidor MCP"""
    print("🧪 Probando Sistema Educativo MCP...")
    
    # Verificar directorio
    EXCEL_DIR.mkdir(exist_ok=True)
    print(f"📁 Directorio Excel: {EXCEL_DIR}")
    
    # Verificar variables de entorno
    print(f"🗄️  Azure SQL Server: {'✅' if AZURE_SQL_SERVER else '❌'}")
    print(f"💾 Azure SQL Database: {'✅' if AZURE_SQL_DATABASE else '❌'}")
    
    # Probar listado de archivos
    try:
        result = list_excel_files()
        print("✅ list_excel_files() funciona")
        print(f"📄 Resultado: {result[:100]}...")
    except Exception as e:
        print(f"❌ Error en list_excel_files(): {e}")
    
    # Probar debug_info
    try:
        debug_result = debug_info()
        print("✅ debug_info() funciona")
        print(f"🔍 Info: {debug_result[:200]}...")
    except Exception as e:
        print(f"❌ Error en debug_info(): {e}")
    
    print("🚀 Sistema Educativo MCP listo para ejecutar")

# =================================
# PUNTO DE ENTRADA PRINCIPAL
# =================================

if __name__ == "__main__":
    # Si se ejecuta con argumento 'test', hacer pruebas
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_server()
    else:
        # Ejecutar servidor MCP normal
        print("🚀 Iniciando Sistema Educativo MCP...")
        print(f"📊 Herramientas disponibles: 8")
        print(f"🔧 Configuración: {MCP_LOG_LEVEL}")
        mcp.run()