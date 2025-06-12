"""
Extractor robusto para archivos Excel (.xlsx/.xls)
"""
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

class ExcelExtractor:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.logger = logging.getLogger(__name__)
    
    def extract_all_data(self, filename: str) -> Dict[str, Any]:
        """Extrae y analiza completamente un archivo Excel"""
        file_path = self.base_dir / filename
        
        # Validaciones básicas
        if not self._validate_file(file_path):
            return {"status": "error", "error": "Archivo inválido"}
        
        try:
            # Analizar estructura del archivo
            structure = self._analyze_file_structure(file_path)
            
            # Extraer datos de cada hoja válida
            sheets_data = {}
            for sheet_name, sheet_info in structure["sheets"].items():
                if sheet_info["is_valid"]:
                    df = self._extract_sheet_data(
                        file_path, 
                        sheet_name, 
                        sheet_info["header_row"]
                    )
                    sheets_data[sheet_name] = {
                        "dataframe": df,
                        "validated": self._validate_dataframe(df),
                        "cleaned": self._clean_dataframe(df)
                    }
            
            return {
                "status": "success",
                "filename": filename,
                "structure": structure,
                "data": sheets_data
            }
            
        except Exception as e:
            self.logger.error(f"Error extrayendo {filename}: {e}")
            return {"status": "error", "error": str(e)}
    
    def _validate_file(self, file_path: Path) -> bool:
        """Valida que el archivo sea Excel válido"""
        if not file_path.exists():
            return False
        
        valid_extensions = ['.xlsx', '.xls']
        return file_path.suffix.lower() in valid_extensions
    
    def _analyze_file_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analiza estructura completa del archivo"""
        excel_file = pd.ExcelFile(file_path)
        
        structure = {
            "total_sheets": len(excel_file.sheet_names),
            "sheets": {}
        }
        
        for sheet_name in excel_file.sheet_names:
            sheet_analysis = self._analyze_sheet(file_path, sheet_name)
            structure["sheets"][sheet_name] = sheet_analysis
        
        return structure
    
    def _analyze_sheet(self, file_path: Path, sheet_name: str) -> Dict[str, Any]:
        """Analiza una hoja específica"""
        try:
            # Detectar fila de headers
            header_row, confidence = self._detect_header_row(file_path, sheet_name)
            
            # Leer muestra para análisis
            sample_df = pd.read_excel(
                file_path, 
                sheet_name=sheet_name, 
                header=header_row, 
                nrows=10
            )
            
            return {
                "is_valid": len(sample_df.columns) > 1 and len(sample_df) > 0,
                "header_row": header_row,
                "header_confidence": confidence,
                "columns": list(sample_df.columns),
                "estimated_rows": self._estimate_total_rows(file_path, sheet_name),
                "data_types": sample_df.dtypes.to_dict()
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "error": str(e)
            }
    
    def _detect_header_row(self, file_path: Path, sheet_name: str, max_check: int = 10) -> Tuple[int, float]:
        """Detecta fila de headers con confianza"""
        best_row = 0
        best_confidence = 0.0
        
        for row in range(max_check):
            try:
                df_test = pd.read_excel(
                    file_path, 
                    sheet_name=sheet_name, 
                    header=row, 
                    nrows=3
                )
                
                if len(df_test.columns) < 2:
                    continue
                
                # Calcular confianza basada en:
                confidence = 0.0
                
                # 1. Porcentaje de columnas con nombres válidos
                unnamed_ratio = sum(1 for col in df_test.columns 
                                  if str(col).startswith('Unnamed')) / len(df_test.columns)
                confidence += (1 - unnamed_ratio) * 0.4
                
                # 2. Diversidad de tipos de datos
                if len(df_test) > 0:
                    type_diversity = len(df_test.dtypes.unique()) / len(df_test.columns)
                    confidence += type_diversity * 0.3
                
                # 3. Presencia de datos no nulos
                if len(df_test) > 0:
                    non_null_ratio = df_test.notna().sum().sum() / (len(df_test) * len(df_test.columns))
                    confidence += non_null_ratio * 0.3
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_row = row
                    
            except Exception:
                continue
        
        return best_row, best_confidence
    
    def _estimate_total_rows(self, file_path: Path, sheet_name: str) -> int:
        """Estima total de filas con datos"""
        try:
            df_full = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            # Contar filas que no están completamente vacías
            return len(df_full.dropna(how='all'))
        except Exception:
            return 0
    
    def _extract_sheet_data(self, file_path: Path, sheet_name: str, header_row: int) -> pd.DataFrame:
        """Extrae datos completos de una hoja"""
        return pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
    
    def _validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Valida calidad del DataFrame"""
        return {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "empty_rows": df.isnull().all(axis=1).sum(),
            "empty_columns": df.isnull().all(axis=0).sum(),
            "duplicate_rows": df.duplicated().sum(),
            "columns_with_nulls": df.isnull().any().sum(),
            "data_quality_score": self._calculate_quality_score(df)
        }
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """Calcula score de calidad (0-1)"""
        if len(df) == 0:
            return 0.0
        
        # Factores de calidad
        null_penalty = df.isnull().sum().sum() / (len(df) * len(df.columns))
        duplicate_penalty = df.duplicated().sum() / len(df)
        empty_rows_penalty = df.isnull().all(axis=1).sum() / len(df)
        
        quality_score = 1.0 - (null_penalty * 0.4 + duplicate_penalty * 0.3 + empty_rows_penalty * 0.3)
        return max(0.0, quality_score)
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y estandariza el DataFrame para BD"""
        cleaned = df.copy()
        
        # 1. Remover filas/columnas completamente vacías
        cleaned = cleaned.dropna(how='all').dropna(axis=1, how='all')
        
        # 2. Estandarizar valores NULL/NA
        cleaned = self._standardize_null_values(cleaned)
        
        # 3. Normalizar flags
        cleaned = self._normalize_flags(cleaned)
        
        # 4. Limpiar nombres de columnas
        cleaned.columns = [str(col).strip() for col in cleaned.columns]
        
        # 5. Remover duplicados exactos
        cleaned = cleaned.drop_duplicates()
        
        return cleaned

    def _standardize_null_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Estandariza valores nulos a None"""
        # Valores a considerar como NULL
        null_values = ['', ' ', 'N/A', 'n/a', 'NA', 'null', 'NULL', 'None', '-']
        
        return df.replace(null_values, None)

    def _normalize_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza campos tipo flag a boolean estándar"""
        flag_columns = ['Multigrado', 'Unitaria', 'Bidocente']
        
        for col in flag_columns:
            if col in df.columns:
                df[col] = df[col].map({
                    'Sí': True, 'Si': True, 'X': True, '1': True, 1: True,
                    'No': False, '0': False, 0: False,
                    None: None
                })
        
        return df