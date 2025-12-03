"""
Esquemas Pydantic para manejo de archivos.
Define los modelos de datos para requests y responses de archivos.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class FileUploadResponse(BaseModel):
    """Esquema para la respuesta de carga de archivo."""
    file_id: int
    filename: str
    s3_url: str
    status: str
    validations: List[Dict[str, Any]]
    records_count: int
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    uploaded_at: datetime


class ValidationResult(BaseModel):
    """Esquema para un resultado de validación."""
    validation_type: str  # Ejemplo: "empty_values", "incorrect_types", "duplicates"
    message: str
    affected_rows: List[int]  # Números de fila afectados
    severity: str  # "error", "warning", "info"


class FileUploadRequest(BaseModel):
    """Esquema para el request de carga de archivo (parámetros adicionales)."""
    categoria: Optional[str] = None
    descripcion: Optional[str] = None

