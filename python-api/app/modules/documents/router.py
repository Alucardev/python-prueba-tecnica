"""
Router del módulo de documentos.
Define los endpoints relacionados con análisis de documentos y eventos históricos.
"""
from fastapi import APIRouter, Depends, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.exceptions.custom_exceptions import ValidationError
from app.middleware.auth import get_current_user
from app.modules.documents.repository import DocumentRepository, EventLogRepository
from app.modules.documents.schemas import (
    DocumentUploadResponse,
    DocumentResponse,
    EventLogListResponse,
    EventLogResponse,
    EventLogFilter,
)
from app.modules.documents.service import DocumentService
from app.schemas.auth import TokenData
from app.shared.s3_service import S3Service
from app.shared.textract_service import TextractService
from io import BytesIO
from fastapi.responses import StreamingResponse

try:
    import openpyxl
except ImportError:
    openpyxl = None

router = APIRouter(prefix="/documents", tags=["Documentos"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(..., description="Documento a analizar (PDF, JPG, PNG)"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Endpoint para subir y analizar un documento con AWS Textract.
    
    Args:
        file: Archivo a subir (PDF, JPG o PNG)
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Información del documento analizado
    """
    # Validar tipo de archivo
    allowed_extensions = [".pdf", ".jpg", ".jpeg", ".png"]
    file_extension = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_extension not in allowed_extensions:
        raise ValidationError(
            f"Tipo de archivo no permitido. Formatos aceptados: {', '.join(allowed_extensions)}"
        )
    
    # Leer el contenido del archivo
    file_content = await file.read()
    
    # Validar tamaño de archivo (máximo 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if len(file_content) > MAX_FILE_SIZE:
        raise ValidationError(
            f"El archivo es demasiado grande. Tamaño máximo permitido: 10MB"
        )
    
    if len(file_content) == 0:
        raise ValidationError("El archivo está vacío")
    
    # Crear servicios
    s3_service = S3Service()
    textract_service = TextractService()
    document_repository = DocumentRepository(db)
    event_repository = EventLogRepository(db)
    document_service = DocumentService(
        document_repository,
        event_repository,
        s3_service,
        textract_service,
    )
    
    # Procesar el documento
    # El commit se maneja automáticamente por get_db() si no hay errores
    result = document_service.upload_and_analyze_document(
        file_content=file_content,
        filename=file.filename,
        user_id=current_user.id_usuario,
    )
    
    return DocumentUploadResponse(**result)


@router.get("/", response_model=list[DocumentResponse])
async def get_documents(
    classification: Optional[str] = Query(None, description="Filtrar por clasificación"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtiene lista de documentos del usuario actual.
    
    Args:
        classification: Filtrar por clasificación (Factura, Información)
        limit: Límite de resultados
        offset: Offset para paginación
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Lista de documentos
    """
    document_repository = DocumentRepository(db)
    documents = document_repository.get_all_documents(
        user_id=current_user.id_usuario,
        classification=classification,
        limit=limit,
        offset=offset,
    )
    
    return [
        DocumentResponse(
            id=doc.id,
            original_filename=doc.original_filename,
            file_type=doc.file_type,
            s3_url=doc.s3_url,
            classification=doc.classification,
            status=doc.status,
            extracted_data=doc.extracted_data,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
        for doc in documents
    ]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtiene un documento por su ID.
    
    Args:
        document_id: ID del documento
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Documento encontrado
    """
    document_repository = DocumentRepository(db)
    document = document_repository.get_document_by_id(document_id)
    
    if not document:
        from app.exceptions.custom_exceptions import NotFoundError
        raise NotFoundError(f"Documento con ID {document_id} no encontrado")
    
    # Verificar que el documento pertenece al usuario
    if document.user_id != current_user.id_usuario:
        from app.exceptions.custom_exceptions import AuthorizationError
        raise AuthorizationError("No tienes permiso para acceder a este documento")
    
    return DocumentResponse(
        id=document.id,
        original_filename=document.original_filename,
        file_type=document.file_type,
        s3_url=document.s3_url,
        classification=document.classification,
        status=document.status,
        extracted_data=document.extracted_data,
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


@router.get("/events/history", response_model=EventLogListResponse)
async def get_event_history(
    event_type: Optional[str] = Query(None, description="Filtrar por tipo de evento"),
    description: Optional[str] = Query(None, description="Buscar en descripción"),
    start_date: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtiene el historial de eventos con filtros.
    
    Args:
        event_type: Filtrar por tipo de evento
        description: Buscar en descripción
        start_date: Fecha de inicio del rango (YYYY-MM-DD)
        end_date: Fecha de fin del rango (YYYY-MM-DD)
        limit: Límite de resultados
        offset: Offset para paginación
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Lista de eventos filtrados
    """
    # Parsear fechas desde string
    parsed_start_date = None
    parsed_end_date = None
    
    if start_date:
        try:
            parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise ValidationError(f"Formato de fecha inválido para start_date: {start_date}. Use YYYY-MM-DD")
    
    if end_date:
        try:
            parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d")
            # Agregar 23:59:59 para incluir todo el día
            parsed_end_date = parsed_end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            raise ValidationError(f"Formato de fecha inválido para end_date: {end_date}. Use YYYY-MM-DD")
    
    event_repository = EventLogRepository(db)
    events = event_repository.get_events(
        event_type=event_type,
        description_filter=description,
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        user_id=current_user.id_usuario,
        limit=limit,
        offset=offset,
    )
    
    # Obtener total (simplificado, en producción usar COUNT)
    total_events = event_repository.get_events(
        event_type=event_type,
        description_filter=description,
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        user_id=current_user.id_usuario,
        limit=10000,  # Para contar total
        offset=0,
    )
    
    return EventLogListResponse(
        events=[
            EventLogResponse(
                id=event.id,
                event_type=event.event_type,
                description=event.description,
                metadata=event.event_metadata,
                document_id=event.document_id,
                user_id=event.user_id,
                created_at=event.created_at,
            )
            for event in events
        ],
        total=len(total_events),
        limit=limit,
        offset=offset,
    )


@router.get("/events/export", response_class=StreamingResponse)
async def export_events_to_excel(
    event_type: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Exporta eventos históricos a Excel.
    
    Args:
        event_type: Filtrar por tipo de evento
        description: Buscar en descripción
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Archivo Excel con los eventos
    """
    if openpyxl is None:
        raise ValidationError("openpyxl no está instalado. Instálalo con: pip install openpyxl")
    
    # Parsear fechas desde string
    parsed_start_date = None
    parsed_end_date = None
    
    if start_date:
        try:
            parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise ValidationError(f"Formato de fecha inválido para start_date: {start_date}. Use YYYY-MM-DD")
    
    if end_date:
        try:
            parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d")
            # Agregar 23:59:59 para incluir todo el día
            parsed_end_date = parsed_end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            raise ValidationError(f"Formato de fecha inválido para end_date: {end_date}. Use YYYY-MM-DD")
    
    event_repository = EventLogRepository(db)
    events = event_repository.get_events(
        event_type=event_type,
        description_filter=description,
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        user_id=current_user.id_usuario,
        limit=10000,  # Límite alto para exportación
        offset=0,
    )
    
    # Crear archivo Excel
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Eventos Históricos"
    
    # Encabezados
    headers = ["ID", "Tipo", "Descripción", "Documento ID", "Usuario ID", "Fecha"]
    worksheet.append(headers)
    
    # Datos
    for event in events:
        worksheet.append([
            event.id,
            event.event_type,
            event.description,
            event.document_id or "",
            event.user_id or "",
            event.created_at.strftime("%Y-%m-%d %H:%M:%S") if event.created_at else "",
        ])
    
    # Guardar en memoria
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    
    # Generar nombre de archivo
    filename = f"eventos_historicos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


__all__ = ["router"]

