"""
Modelos del módulo de análisis de documentos.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.models import Base


class Document(Base):
    """Modelo de Documento analizado en la base de datos."""

    __tablename__ = "documents"

    # ID único del documento
    id = Column(Integer, primary_key=True, index=True)

    # Nombre original del archivo
    original_filename = Column(String(255), nullable=False)

    # Tipo de archivo (PDF, JPG, PNG)
    file_type = Column(String(10), nullable=False)

    # Nombre del archivo en S3
    s3_key = Column(String(500), nullable=False, unique=True)

    # URL del archivo en S3
    s3_url = Column(String(1000), nullable=False)

    # ID del usuario que subió el documento
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Clasificación del documento (Factura, Información)
    classification = Column(String(50), nullable=False)

    # Estado del análisis (processing, completed, error)
    status = Column(String(50), default="processing")

    # Datos extraídos (JSON)
    extracted_data = Column(JSON, nullable=True)

    # Fecha de creación
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Fecha de actualización
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con el usuario
    user = relationship("User", backref="documents")

    # Relación con eventos históricos
    events = relationship("EventLog", back_populates="document")


class EventLog(Base):
    """Modelo de log de eventos históricos."""

    __tablename__ = "event_logs"

    # ID único del evento
    id = Column(Integer, primary_key=True, index=True)

    # ID del documento relacionado (opcional)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)

    # Tipo de evento (document_upload, ai_analysis, user_interaction)
    event_type = Column(String(50), nullable=False, index=True)

    # Descripción del evento
    description = Column(Text, nullable=False)

    # Datos adicionales del evento (JSON)
    event_metadata = Column(JSON, nullable=True)

    # ID del usuario que generó el evento
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Fecha y hora del evento
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relación con el documento
    document = relationship("Document", back_populates="events")

    # Relación con el usuario
    user = relationship("User", backref="event_logs")


__all__ = ["Document", "EventLog"]

