"""
Modelos del módulo CSV (subida y procesamiento de archivos).
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.models import Base


class FileUpload(Base):
    """Modelo de Archivo Subido en la base de datos."""

    __tablename__ = "file_uploads"

    # ID único del archivo
    id = Column(Integer, primary_key=True, index=True)

    # Nombre original del archivo
    original_filename = Column(String(255), nullable=False)

    # Nombre del archivo en S3
    s3_key = Column(String(500), nullable=False, unique=True)

    # URL del archivo en S3
    s3_url = Column(String(1000), nullable=False)

    # ID del usuario que subió el archivo
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Estado del archivo (procesado, error, etc.)
    status = Column(String(50), default="uploaded")

    # Validaciones aplicadas (JSON como texto)
    validations = Column(Text, nullable=True)

    # Número de registros procesados
    records_count = Column(Integer, default=0)

    # Categoría del archivo
    categoria = Column(String(100), nullable=True)

    # Descripción del archivo
    descripcion = Column(Text, nullable=True)

    # Fecha de creación
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación con el usuario
    user = relationship("User", backref="file_uploads")


class CSVRecord(Base):
    """Modelo para almacenar los registros del CSV en la base de datos."""

    __tablename__ = "csv_records"

    # ID único del registro
    id = Column(Integer, primary_key=True, index=True)

    # ID del archivo al que pertenece
    file_upload_id = Column(Integer, ForeignKey("file_uploads.id"), nullable=False)

    # Datos del registro (JSON como texto)
    record_data = Column(Text, nullable=False)

    # Fila del CSV original
    row_number = Column(Integer, nullable=False)

    # Indica si el registro es válido
    is_valid = Column(String(10), default="true")

    # Errores de validación (JSON como texto)
    validation_errors = Column(Text, nullable=True)

    # Fecha de creación
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación con el archivo
    file_upload = relationship(FileUpload, backref="csv_records")


__all__ = ["FileUpload", "CSVRecord"]

