"""
Esquemas Pydantic del módulo de documentos.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Esquema para la respuesta de carga de documento."""
    document_id: int
    filename: str
    file_type: str
    s3_url: str
    classification: str
    status: str
    extracted_data: Optional[Dict[str, Any]] = None
    created_at: datetime


class DocumentResponse(BaseModel):
    """Esquema para respuesta de documento."""
    id: int
    original_filename: str
    file_type: str
    s3_url: str
    classification: str
    status: str
    extracted_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class EventLogResponse(BaseModel):
    """Esquema para respuesta de evento histórico."""
    id: int
    event_type: str
    description: str
    metadata: Optional[Dict[str, Any]] = None
    document_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: datetime


class EventLogFilter(BaseModel):
    """Esquema para filtros de eventos históricos."""
    event_type: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[int] = None
    limit: int = 100
    offset: int = 0


class EventLogListResponse(BaseModel):
    """Esquema para respuesta de lista de eventos."""
    events: List[EventLogResponse]
    total: int
    limit: int
    offset: int


__all__ = [
    "DocumentUploadResponse",
    "DocumentResponse",
    "EventLogResponse",
    "EventLogFilter",
    "EventLogListResponse",
]

