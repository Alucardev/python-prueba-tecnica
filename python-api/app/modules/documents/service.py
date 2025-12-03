"""
Servicio del módulo de documentos (análisis con AWS Textract).
"""
import json
from typing import Dict, Any, Optional

from app.exceptions.custom_exceptions import ExternalServiceError
from app.modules.documents.repository import DocumentRepository, EventLogRepository
from app.shared.s3_service import S3Service
from app.shared.textract_service import TextractService
from app.shared.constants import (
    DocumentClassification,
    DocumentStatus,
    EventType,
    FileType,
)


class DocumentService:
    """Servicio para operaciones de documentos."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        event_repository: EventLogRepository,
        s3_service: S3Service,
        textract_service: TextractService,
    ):
        """
        Inicializa el servicio con repositorios y servicios.

        Args:
            document_repository: Repositorio de documentos
            event_repository: Repositorio de eventos
            s3_service: Servicio de S3
            textract_service: Servicio de Textract
        """
        self.document_repository = document_repository
        self.event_repository = event_repository
        self.s3_service = s3_service
        self.textract_service = textract_service

    def upload_and_analyze_document(
        self,
        file_content: bytes,
        filename: str,
        user_id: int,
    ) -> Dict[str, Any]:
        """
        Sube un documento a S3 y lo analiza con Textract.

        Args:
            file_content: Contenido del archivo en bytes
            filename: Nombre original del archivo
            user_id: ID del usuario que sube el documento

        Returns:
            Diccionario con información del documento analizado
        """
        # Determinar tipo de archivo
        file_type = self._get_file_type(filename)

        # Subir archivo a S3
        try:
            s3_key, s3_url = self.s3_service.upload_file(
                file_content,
                filename,
                categoria="documentos",
                descripcion=f"Documento subido por usuario {user_id}",
            )
        except Exception as e:
            raise ExternalServiceError(f"Error al subir archivo a S3: {str(e)}", service="AWS S3")

        # Crear registro de documento
        document = self.document_repository.create_document(
            original_filename=filename,
            file_type=file_type,
            s3_key=s3_key,
            s3_url=s3_url,
            user_id=user_id,
            classification=DocumentClassification.PROCESSING.value,
            status=DocumentStatus.PROCESSING.value,
        )

        # Registrar evento
        self.event_repository.create_event(
            event_type=EventType.DOCUMENT_UPLOAD.value,
            description=f"Documento {filename} subido",
            user_id=user_id,
            document_id=document.id,
        )

        # Analizar documento con Textract
        try:
            # Extraer texto del documento
            textract_response = self.textract_service.detect_document_text(
                s3_bucket=self.s3_service.bucket_name,
                s3_key=s3_key,
            )

            # Extraer texto completo
            text_content = self._extract_text_from_textract_response(textract_response)

            # Clasificar documento
            classification = self.textract_service.classify_document(text_content)

            # Extraer datos según la clasificación
            extracted_data = self._extract_data_by_classification(
                classification, text_content, s3_key
            )

            # Actualizar documento con resultados
            document = self.document_repository.update_document_analysis(
                document_id=document.id,
                classification=classification,
                status=DocumentStatus.COMPLETED.value,
                extracted_data=extracted_data,
            )

            # Registrar evento de análisis
            self.event_repository.create_event(
                event_type=EventType.AI_ANALYSIS.value,
                description=f"Análisis completado: {classification}",
                user_id=user_id,
                document_id=document.id,
                metadata={"classification": classification},
            )

        except Exception as e:
            # Actualizar estado a error
            self.document_repository.update_document_analysis(
                document_id=document.id,
                status=DocumentStatus.ERROR.value,
            )
            raise ExternalServiceError(
                f"Error al analizar documento: {str(e)}", service="AWS Textract"
            )

        return {
            "document_id": document.id,
            "filename": filename,
            "file_type": file_type,
            "s3_url": s3_url,
            "classification": document.classification,
            "status": document.status,
            "extracted_data": document.extracted_data,
            "created_at": document.created_at,
        }

    def _get_file_type(self, filename: str) -> str:
        """Determina el tipo de archivo basándose en la extensión."""
        extension = filename.split(".")[-1].upper()
        
        extension_map = {
            "PDF": FileType.PDF.value,
            "JPG": FileType.JPG.value,
            "JPEG": FileType.JPG.value,
            "PNG": FileType.PNG.value,
        }
        
        return extension_map.get(extension, FileType.UNKNOWN.value)

    def _extract_text_from_textract_response(self, response: Dict[str, Any]) -> str:
        """Extrae texto completo de la respuesta de Textract."""
        blocks = response.get("Blocks", [])
        return self._extract_text_from_blocks(blocks)
    
    def _extract_text_from_blocks(self, blocks: list) -> str:
        """Extrae texto de los bloques de Textract."""
        text_blocks = [
            block.get("Text", "") 
            for block in blocks 
            if block.get("BlockType") == "LINE"
        ]
        return " ".join(text_blocks)
    
    def _extract_data_by_classification(
        self, classification: str, text_content: str, s3_key: str
    ) -> Dict[str, Any]:
        """
        Extrae datos del documento según su clasificación.
        
        Args:
            classification: Clasificación del documento
            text_content: Contenido de texto extraído
            s3_key: Clave del archivo en S3
            
        Returns:
            Diccionario con datos extraídos
        """
        if classification == DocumentClassification.FACTURA.value:
            # Usar analyze_document para obtener más detalles
            analyze_response = self.textract_service.analyze_document(
                s3_bucket=self.s3_service.bucket_name,
                s3_key=s3_key,
            )
            return self.textract_service.extract_invoice_data(analyze_response)
        else:
            return self.textract_service.extract_information_data(text_content)


__all__ = ["DocumentService"]

