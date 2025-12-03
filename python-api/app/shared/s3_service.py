"""
Servicio de AWS S3 compartido entre módulos.
"""
import uuid
from datetime import datetime
from typing import Optional, Tuple

import boto3
from botocore.exceptions import ClientError

from app.config import settings
from app.exceptions.custom_exceptions import ExternalServiceError


class S3Service:
    """Servicio para operaciones con AWS S3."""

    def __init__(self):
        """Inicializa el cliente de S3."""
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    def upload_file(
        self,
        file_content: bytes,
        filename: str,
        categoria: Optional[str] = None,
        descripcion: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Sube un archivo a S3 con metadata de categoría y descripción.

        Args:
            file_content: Contenido del archivo en bytes
            filename: Nombre original del archivo
            categoria: Categoría del archivo (se guarda como metadata)
            descripcion: Descripción del archivo (se guarda como metadata)

        Returns:
            Tupla con (s3_key, s3_url)
        """

        # Generar una clave única para el archivo en S3
        # Formato: uploads/YYYY/MM/DD/uuid-nombre_original.csv
        date_prefix = datetime.utcnow().strftime("%Y/%m/%d")
        unique_id = str(uuid.uuid4())
        file_extension = filename.split(".")[-1] if "." in filename else "csv"
        s3_key = f"uploads/{date_prefix}/{unique_id}-{filename}"

        try:
            # Preparar metadata para S3
            metadata = {}
            if categoria:
                metadata["categoria"] = categoria
            if descripcion:
                metadata["descripcion"] = descripcion

            # Subir el archivo a S3 con metadata
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType="text/csv",
                Metadata=metadata,
            )

            # Generar la URL del archivo
            s3_url = (
                f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
            )

            return s3_key, s3_url

        except ClientError as e:
            error_message = str(e)
            raise ExternalServiceError(
                f"Error al subir archivo: {error_message}", service="AWS S3"
            )
        except Exception as e:
            raise ExternalServiceError(
                f"Error inesperado al subir archivo: {str(e)}", service="AWS S3"
            )

    def delete_file(self, s3_key: str) -> bool:
        """
        Elimina un archivo de S3.

        Args:
            s3_key: Clave del archivo en S3

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """

        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False

    def file_exists(self, s3_key: str) -> bool:
        """
        Verifica si un archivo existe en S3.

        Args:
            s3_key: Clave del archivo en S3

        Returns:
            True si existe, False en caso contrario
        """

        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False


__all__ = ["S3Service"]


