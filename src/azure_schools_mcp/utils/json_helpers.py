"""
Utilidades para manejo de JSON
"""
import json
import pandas as pd
from typing import Any

def safe_json_response(data: Any) -> str:
    """Convierte respuesta a JSON válido para MCP"""
    def json_serializer(obj):
        if pd.isna(obj):
            return None
        elif hasattr(obj, 'item'):  # numpy types
            return obj.item()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        else:
            return str(obj)
    
    try:
        return json.dumps(data, indent=2, ensure_ascii=False, default=json_serializer)
    except Exception as e:
        return json.dumps({
            "status": "error", 
            "error": f"JSON serialization error: {str(e)}"
        })