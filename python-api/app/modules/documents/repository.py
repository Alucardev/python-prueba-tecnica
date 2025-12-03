"""
Repositorio del módulo de documentos.
"""
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session

from app.modules.documents.models import Document, EventLog


class DocumentRepository:
    """Repositorio para operaciones de documentos."""

    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db

    def create_document(
        self,
        original_filename: str,
        file_type: str,
        s3_key: str,
        s3_url: str,
        user_id: int,
        classification: str,
        status: str = "processing",
    ) -> Document:
        """
        Crea un nuevo documento en la base de datos.

        Args:
            original_filename: Nombre original del archivo
            file_type: Tipo de archivo (PDF, JPG, PNG)
            s3_key: Clave del archivo en S3
            s3_url: URL del archivo en S3
            user_id: ID del usuario que subió el documento
            classification: Clasificación del documento (Factura, Información)
            status: Estado del análisis

        Returns:
            Documento creado
        """
        document = Document(
            original_filename=original_filename,
            file_type=file_type,
            s3_key=s3_key,
            s3_url=s3_url,
            user_id=user_id,
            classification=classification,
            status=status,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """
        Obtiene un documento por su ID.

        Args:
            document_id: ID del documento

        Returns:
            Documento encontrado o None
        """
        stmt = select(Document).where(Document.id == document_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def update_document_analysis(
        self,
        document_id: int,
        classification: Optional[str] = None,
        status: Optional[str] = None,
        extracted_data: Optional[dict] = None,
    ) -> Optional[Document]:
        """
        Actualiza el análisis de un documento.

        Args:
            document_id: ID del documento
            classification: Nueva clasificación
            status: Nuevo estado
            extracted_data: Datos extraídos

        Returns:
            Documento actualizado o None
        """
        document = self.get_document_by_id(document_id)
        if document:
            if classification is not None:
                document.classification = classification
            if status is not None:
                document.status = status
            if extracted_data is not None:
                document.extracted_data = extracted_data
            self.db.commit()
            self.db.refresh(document)
        return document

    def get_all_documents(
        self,
        user_id: Optional[int] = None,
        classification: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Document]:
        """
        Obtiene todos los documentos con filtros opcionales.

        Args:
            user_id: Filtrar por usuario
            classification: Filtrar por clasificación
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Lista de documentos
        """
        stmt = select(Document)

        conditions = []
        if user_id:
            conditions.append(Document.user_id == user_id)
        if classification:
            conditions.append(Document.classification == classification)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(Document.created_at.desc()).limit(limit).offset(offset)
        result = self.db.execute(stmt)
        return list(result.scalars().all())


class EventLogRepository:
    """Repositorio para operaciones de eventos históricos."""

    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db

    def create_event(
        self,
        event_type: str,
        description: str,
        user_id: Optional[int] = None,
        document_id: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> EventLog:
        """
        Crea un nuevo evento en el log.

        Args:
            event_type: Tipo de evento (document_upload, ai_analysis, user_interaction)
            description: Descripción del evento
            user_id: ID del usuario que generó el evento
            document_id: ID del documento relacionado
            metadata: Datos adicionales del evento

        Returns:
            Evento creado
        """
        event = EventLog(
            event_type=event_type,
            description=description,
            user_id=user_id,
            document_id=document_id,
            event_metadata=metadata,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_event_by_id(self, event_id: int) -> Optional[EventLog]:
        """
        Obtiene un evento por su ID.

        Args:
            event_id: ID del evento

        Returns:
            Evento encontrado o None
        """
        stmt = select(EventLog).where(EventLog.id == event_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_events(
        self,
        event_type: Optional[str] = None,
        description_filter: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[EventLog]:
        """
        Obtiene eventos con filtros opcionales.

        Args:
            event_type: Filtrar por tipo de evento
            description_filter: Filtrar por descripción (búsqueda parcial)
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            user_id: Filtrar por usuario
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Lista de eventos
        """
        stmt = select(EventLog)

        conditions = []
        if event_type:
            conditions.append(EventLog.event_type == event_type)
        if description_filter:
            conditions.append(EventLog.description.like(f"%{description_filter}%"))
        if start_date:
            conditions.append(EventLog.created_at >= start_date)
        if end_date:
            conditions.append(EventLog.created_at <= end_date)
        if user_id:
            conditions.append(EventLog.user_id == user_id)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(EventLog.created_at.desc()).limit(limit).offset(offset)
        result = self.db.execute(stmt)
        return list(result.scalars().all())


__all__ = ["DocumentRepository", "EventLogRepository"]

