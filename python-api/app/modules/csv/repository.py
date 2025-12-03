"""
Repositorio del módulo CSV.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.csv.models import FileUpload, CSVRecord


class FileRepository:
    """Repositorio para operaciones de archivos."""

    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesión de base de datos.

        Args:
            db: Sesión de SQLAlchemy
        """

        self.db = db

    def create_file_upload(
        self,
        original_filename: str,
        s3_key: str,
        s3_url: str,
        user_id: int,
        status: str = "uploaded",
        validations: Optional[str] = None,
        records_count: int = 0,
        categoria: Optional[str] = None,
        descripcion: Optional[str] = None,
    ) -> FileUpload:
        """
        Crea un nuevo registro de archivo subido.

        Args:
            original_filename: Nombre original del archivo
            s3_key: Clave del archivo en S3
            s3_url: URL del archivo en S3
            user_id: ID del usuario que subió el archivo
            status: Estado del archivo
            validations: Validaciones aplicadas (JSON como string)
            records_count: Número de registros procesados
            categoria: Categoría del archivo
            descripcion: Descripción del archivo

        Returns:
            Registro de archivo creado
        """

        file_upload = FileUpload(
            original_filename=original_filename,
            s3_key=s3_key,
            s3_url=s3_url,
            user_id=user_id,
            status=status,
            validations=validations,
            records_count=records_count,
            categoria=categoria,
            descripcion=descripcion,
        )
        self.db.add(file_upload)
        self.db.commit()
        self.db.refresh(file_upload)
        return file_upload

    def get_file_upload_by_id(self, file_id: int) -> Optional[FileUpload]:
        """
        Obtiene un archivo por su ID.

        Args:
            file_id: ID del archivo

        Returns:
            Archivo encontrado o None
        """

        stmt = select(FileUpload).where(FileUpload.id == file_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def update_file_upload_status(
        self,
        file_id: int,
        status: str,
        validations: Optional[str] = None,
        records_count: Optional[int] = None,
    ) -> Optional[FileUpload]:
        """
        Actualiza el estado de un archivo subido.

        Args:
            file_id: ID del archivo
            status: Nuevo estado
            validations: Validaciones aplicadas (JSON como string)
            records_count: Número de registros procesados

        Returns:
            Archivo actualizado o None
        """

        file_upload = self.get_file_upload_by_id(file_id)
        if file_upload:
            file_upload.status = status
            if validations is not None:
                file_upload.validations = validations
            if records_count is not None:
                file_upload.records_count = records_count
            self.db.commit()
            self.db.refresh(file_upload)
        return file_upload

    def create_csv_record(
        self,
        file_upload_id: int,
        record_data: str,
        row_number: int,
        is_valid: str = "true",
        validation_errors: Optional[str] = None,
    ) -> CSVRecord:
        """
        Crea un registro CSV en la base de datos.

        Args:
            file_upload_id: ID del archivo al que pertenece
            record_data: Datos del registro (JSON como string)
            row_number: Número de fila en el CSV original
            is_valid: Indica si el registro es válido
            validation_errors: Errores de validación (JSON como string)

        Returns:
            Registro CSV creado
        """

        csv_record = CSVRecord(
            file_upload_id=file_upload_id,
            record_data=record_data,
            row_number=row_number,
            is_valid=is_valid,
            validation_errors=validation_errors,
        )
        self.db.add(csv_record)
        self.db.commit()
        self.db.refresh(csv_record)
        return csv_record

    def get_csv_records_by_file_id(self, file_upload_id: int) -> List[CSVRecord]:
        """
        Obtiene todos los registros CSV de un archivo.

        Args:
            file_upload_id: ID del archivo

        Returns:
            Lista de registros CSV
        """

        stmt = select(CSVRecord).where(CSVRecord.file_upload_id == file_upload_id)
        result = self.db.execute(stmt)
        return list(result.scalars().all())


__all__ = ["FileRepository"]

