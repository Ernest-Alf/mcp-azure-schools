"""
Analizador estadístico de archivos Excel - Módulo Excel Tools
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from azure_schools_mcp.utils.logger import setup_logger

logger = setup_logger("excel_tools.analyzer")

logger = setup_logger("excel_tools.analyzer")

class ExcelAnalyzer:
    """Analizador estadístico avanzado para archivos Excel"""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def generate_comprehensive_summary(self, df: pd.DataFrame, filename: str, 
                                     sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """Genera resumen estadístico completo de un DataFrame"""
        try:
            # Información básica
            basic_info = {
                "filename": filename,
                "sheet": sheet_name or "default",
                "dimensions": {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "cells": len(df) * len(df.columns)
                },
                "memory_usage": {
                    "total_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
                    "per_column_kb": {col: round(df[col].memory_usage(deep=True) / 1024, 2) 
                                    for col in df.columns}
                }
            }
            
            # Análisis de tipos de datos
            data_types_analysis = self._analyze_data_types(df)
            
            # Análisis de valores nulos
            null_analysis = self._analyze_null_values(df)
            
            # Estadísticas numéricas
            numeric_stats = self._analyze_numeric_columns(df)
            
            # Análisis de columnas de texto
            text_stats = self._analyze_text_columns(df)
            
            # Detección automática de patrones
            patterns = self._detect_patterns(df)
            
            return {
                "status": "success",
                "timestamp": pd.Timestamp.now().isoformat(),
                "basic_info": basic_info,
                "data_types": data_types_analysis,
                "null_analysis": null_analysis,
                "numeric_statistics": numeric_stats,
                "text_statistics": text_stats,
                "detected_patterns": patterns,
                "recommendations": self._generate_recommendations(df, patterns)
            }
            
        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _analyze_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza tipos de datos de las columnas"""
        type_counts = df.dtypes.value_counts().to_dict()
        
        column_details = {}
        for col in df.columns:
            dtype = df[col].dtype
            column_details[col] = {
                "dtype": str(dtype),
                "category": self._categorize_dtype(dtype),
                "unique_values": df[col].nunique(),
                "unique_ratio": round(df[col].nunique() / len(df), 3) if len(df) > 0 else 0
            }
        
        return {
            "type_distribution": {str(k): int(v) for k, v in type_counts.items()},
            "column_details": column_details,
            "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
            "text_columns": df.select_dtypes(include=['object']).columns.tolist(),
            "datetime_columns": df.select_dtypes(include=['datetime']).columns.tolist()
        }
    
    def _analyze_null_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza valores nulos en el DataFrame"""
        null_counts = df.isnull().sum()
        null_percentages = (null_counts / len(df) * 100).round(2)
        
        # Columnas con alta proporción de nulos
        high_null_cols = null_percentages[null_percentages > 50].index.tolist()
        
        # Patrones de nulos
        total_null_rows = df.isnull().any(axis=1).sum()
        complete_rows = len(df) - total_null_rows
        
        return {
            "summary": {
                "total_null_values": int(null_counts.sum()),
                "rows_with_nulls": int(total_null_rows),
                "complete_rows": int(complete_rows),
                "completion_rate": round(complete_rows / len(df) * 100, 2) if len(df) > 0 else 0
            },
            "by_column": {
                "null_counts": null_counts.to_dict(),
                "null_percentages": null_percentages.to_dict(),
                "high_null_columns": high_null_cols
            },
            "recommendations": {
                "columns_to_review": high_null_cols,
                "data_quality_score": round((complete_rows / len(df)) * 100, 1) if len(df) > 0 else 0
            }
        }
    
    def _analyze_numeric_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza columnas numéricas"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return {"message": "No hay columnas numéricas para analizar"}
        
        stats = {}
        for col in numeric_df.columns:
            col_data = numeric_df[col].dropna()
            
            if len(col_data) > 0:
                stats[col] = {
                    "count": len(col_data),
                    "mean": round(col_data.mean(), 2),
                    "median": round(col_data.median(), 2),
                    "std": round(col_data.std(), 2),
                    "min": round(col_data.min(), 2),
                    "max": round(col_data.max(), 2),
                    "range": round(col_data.max() - col_data.min(), 2),
                    "quartiles": {
                        "q1": round(col_data.quantile(0.25), 2),
                        "q3": round(col_data.quantile(0.75), 2),
                        "iqr": round(col_data.quantile(0.75) - col_data.quantile(0.25), 2)
                    },
                    "outliers_count": self._count_outliers(col_data),
                    "distribution": {
                        "skewness": round(col_data.skew(), 3),
                        "kurtosis": round(col_data.kurtosis(), 3)
                    }
                }
        
        return {
            "column_statistics": stats,
            "summary": {
                "numeric_columns_count": len(numeric_df.columns),
                "total_numeric_values": int(numeric_df.count().sum()),
                "columns_analyzed": list(numeric_df.columns)
            }
        }
    
    def _analyze_text_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza columnas de texto"""
        text_df = df.select_dtypes(include=['object'])
        
        if text_df.empty:
            return {"message": "No hay columnas de texto para analizar"}
        
        stats = {}
        for col in text_df.columns:
            col_data = text_df[col].dropna().astype(str)
            
            if len(col_data) > 0:
                # Longitudes de texto
                lengths = col_data.str.len()
                
                # Valores más frecuentes
                value_counts = col_data.value_counts().head(5)
                
                stats[col] = {
                    "unique_values": col_data.nunique(),
                    "most_common": value_counts.to_dict(),
                    "text_lengths": {
                        "min": int(lengths.min()),
                        "max": int(lengths.max()),
                        "mean": round(lengths.mean(), 1),
                        "median": round(lengths.median(), 1)
                    },
                    "patterns": {
                        "contains_numbers": int(col_data.str.contains(r'\d').sum()),
                        "all_uppercase": int(col_data.str.isupper().sum()),
                        "all_lowercase": int(col_data.str.islower().sum()),
                        "mixed_case": int((~col_data.str.isupper() & ~col_data.str.islower()).sum())
                    }
                }
        
        return {
            "column_statistics": stats,
            "summary": {
                "text_columns_count": len(text_df.columns),
                "columns_analyzed": list(text_df.columns)
            }
        }
    
    def _detect_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detecta patrones automáticamente en los datos"""
        patterns = {
            "potential_id_columns": [],
            "potential_category_columns": [],
            "potential_date_columns": [],
            "potential_numeric_codes": [],
            "data_quality_issues": []
        }
        
        for col in df.columns:
            col_data = df[col].dropna()
            
            if len(col_data) == 0:
                continue
            
            # Detectar columnas ID
            if (col_data.nunique() == len(col_data) and 
                col.lower() in ['id', 'codigo', 'key', 'identificador']):
                patterns["potential_id_columns"].append(col)
            
            # Detectar categorías
            if (col_data.nunique() < len(col_data) * 0.1 and 
                col_data.nunique() < 20):
                patterns["potential_category_columns"].append({
                    "column": col,
                    "categories": col_data.value_counts().head(5).to_dict()
                })
            
            # Detectar fechas en texto
            if df[col].dtype == 'object':
                date_like = col_data.astype(str).str.contains(
                    r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}'
                ).sum()
                if date_like > len(col_data) * 0.5:
                    patterns["potential_date_columns"].append(col)
        
        return patterns
    
    def _generate_recommendations(self, df: pd.DataFrame, patterns: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        recommendations = []
        
        # Recomendaciones de calidad de datos
        null_percentage = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
        if null_percentage > 10:
            recommendations.append(f"⚠️  Alta proporción de valores nulos ({null_percentage:.1f}%). Considerar limpieza de datos.")
        
        # Recomendaciones de tipos de datos
        if patterns.get("potential_date_columns"):
            recommendations.append(f"📅 Convertir a fecha: {', '.join(patterns['potential_date_columns'])}")
        
        if patterns.get("potential_category_columns"):
            cat_cols = [item["column"] for item in patterns["potential_category_columns"]]
            recommendations.append(f"🏷️  Convertir a categorías: {', '.join(cat_cols)}")
        
        # Recomendaciones de memoria
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        if memory_mb > 50:
            recommendations.append(f"💾 Archivo grande ({memory_mb:.1f} MB). Considerar procesamiento por chunks.")
        
        return recommendations
    
    def _categorize_dtype(self, dtype) -> str:
        """Categoriza un tipo de dato pandas"""
        if pd.api.types.is_numeric_dtype(dtype):
            return "numeric"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            return "datetime"
        elif pd.api.types.is_bool_dtype(dtype):
            return "boolean"
        else:
            return "text"
    
    def _count_outliers(self, series: pd.Series) -> int:
        """Cuenta outliers usando el método IQR"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = (series < lower_bound) | (series > upper_bound)
        return int(outliers.sum())

# Instancia global del analizador
excel_analyzer = ExcelAnalyzer()
