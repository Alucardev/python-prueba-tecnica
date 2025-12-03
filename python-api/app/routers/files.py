"""
Router de Archivos.
Define los endpoints relacionados con la carga y validación de archivos CSV.
"""
from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.config import settings
from app.database import get_db
from app.exceptions.custom_exceptions import ValidationError
from app.middleware.auth import require_role
from app.modules.csv.repository import FileRepository
from app.modules.csv.schemas import FileUploadResponse
from app.modules.csv.service import FileService
from app.schemas.auth import TokenData
from app.shared.s3_service import S3Service

router = APIRouter(prefix="/files", tags=["Archivos"])


@router.post("/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(..., description="Archivo CSV a subir"),
    categoria: Optional[str] = Form(None, description="Categoría del archivo"),
    descripcion: Optional[str] = Form(None, description="Descripción del archivo"),
    current_user: TokenData = Depends(require_role(settings.ALLOWED_ROLES_FOR_FILE_UPLOAD)),
    db: Session = Depends(get_db)
):
    """
    Endpoint para subir y validar un archivo CSV.
    
    Requisitos:
    - El archivo se sube a AWS S3 (con metadata de categoria y descripcion)
    - El contenido se procesa y almacena en SQL Server (con categoria y descripcion)
    - Se aplican validaciones y se retorna la lista de validaciones
    
    El acceso está limitado a usuarios con roles específicos (validado por JWT).
    
    Args:
        file: Archivo CSV a subir
        categoria: Categoría del archivo (opcional, se guarda en DB y S3)
        descripcion: Descripción del archivo (opcional, se guarda en DB y S3)
        current_user: Usuario autenticado (validado por middleware)
        db: Sesión de base de datos
        
    Returns:
        Información del archivo procesado con validaciones
        
    Raises:
        HTTPException: Si hay error al procesar el archivo
    """
    # Validar que el archivo sea CSV
    if not file.filename or not file.filename.endswith('.csv'):
        raise ValidationError("El archivo debe ser un CSV (.csv)")
    
    # Leer el contenido del archivo
    file_content = await file.read()
    
    # Crear servicios
    s3_service = S3Service()
    file_repository = FileRepository(db)
    file_service = FileService(file_repository, s3_service)
    
    # Procesar el archivo con categoria y descripcion
    # Las excepciones serán capturadas por el middleware de errores
    result = file_service.upload_and_process_csv(
        file_content=file_content,
        filename=file.filename,
        user_id=current_user.id_usuario,
        categoria=categoria,
        descripcion=descripcion
    )
    
    # Asegurar que todos los cambios se persistan
    db.commit()
    
    # Retornar respuesta
    return FileUploadResponse(
        file_id=result["file_id"],
        filename=result["filename"],
        s3_url=result["s3_url"],
        status=result["status"],
        validations=result["validations"],
        records_count=result["records_count"],
        categoria=result["categoria"],
        descripcion=result["descripcion"],
        uploaded_at=result["uploaded_at"]
    )

