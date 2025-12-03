"""
Servicio de Archivos.
Maneja la lógica de negocio relacionada con la carga y procesamiento de archivos.
"""
import json
from typing import List, Dict, Any, Optional
from app.repositories.file_repository import FileRepository
from app.services.s3_service import S3Service
from app.utils.validators import CSVValidator
from app.exceptions.custom_exceptions import ExternalServiceError, DatabaseError
import csv
import io


class FileService:
    """Servicio para operaciones de archivos."""
    
    def __init__(
        self,
        file_repository: FileRepository,
        s3_service: S3Service
    ):
        """
        Inicializa el servicio con repositorio y servicio S3.
        
        Args:
            file_repository: Repositorio de archivos
            s3_service: Servicio de S3
        """
        self.file_repository = file_repository
        self.s3_service = s3_service
    
    def upload_and_process_csv(
        self,
        file_content: bytes,
        filename: str,
        user_id: int,
        categoria: Optional[str] = None,
        descripcion: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sube un archivo CSV a S3, lo valida y almacena en la base de datos.
        
        Args:
            file_content: Contenido del archivo en bytes
            filename: Nombre original del archivo
            user_id: ID del usuario que sube el archivo
            categoria: Categoría del archivo
            descripcion: Descripción del archivo
            
        Returns:
            Diccionario con información del archivo procesado
        """
        # Paso 1: Subir archivo a S3 con metadata (categoria y descripcion)
        try:
            s3_key, s3_url = self.s3_service.upload_file(
                file_content,
                filename,
                categoria=categoria,
                descripcion=descripcion
            )
        except Exception as e:
            raise ExternalServiceError(str(e), service="AWS S3")
        
        # Paso 2: Validar el archivo CSV
        validations = CSVValidator.validate_csv(file_content, categoria, descripcion)
        
        # Paso 3: Procesar y almacenar registros en la base de datos
        records_count = 0
        try:
            file_text = file_content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(file_text))
            
            # Crear registro de archivo en la base de datos con categoria y descripcion
            validations_json = json.dumps(validations, ensure_ascii=False)
            file_upload = self.file_repository.create_file_upload(
                original_filename=filename,
                s3_key=s3_key,
                s3_url=s3_url,
                user_id=user_id,
                status="processing",
                validations=validations_json,
                records_count=0,
                categoria=categoria,
                descripcion=descripcion
            )
            
            # Procesar cada fila del CSV
            for row_number, row in enumerate(csv_reader, start=2):  # Empezar en 2 (fila 1 es header)
                # Convertir la fila a JSON
                record_data = json.dumps(row, ensure_ascii=False)
                
                # Determinar si la fila es válida basándose en las validaciones
                is_valid = "true"
                validation_errors = None
                
                # Verificar si esta fila tiene errores en las validaciones
                row_errors = []
                for validation in validations:
                    if row_number in validation.get("affected_rows", []):
                        if validation.get("severity") == "error":
                            is_valid = "false"
                            row_errors.append(validation.get("message", ""))
                
                if row_errors:
                    validation_errors = json.dumps(row_errors, ensure_ascii=False)
                
                # Guardar el registro en la base de datos
                self.file_repository.create_csv_record(
                    file_upload_id=file_upload.id,
                    record_data=record_data,
                    row_number=row_number,
                    is_valid=is_valid,
                    validation_errors=validation_errors
                )
                records_count += 1
            
            # Actualizar el estado del archivo
            final_status = "completed" if all(
                v.get("severity") != "error" for v in validations
            ) else "completed_with_errors"
            
            self.file_repository.update_file_upload_status(
                file_upload.id,
                final_status,
                validations_json,
                records_count
            )
            
        except Exception as e:
            # Si hay error al procesar, actualizar el estado
            if 'file_upload' in locals():
                try:
                    self.file_repository.update_file_upload_status(
                        file_upload.id,
                        "error",
                        json.dumps([{"validation_type": "processing_error", "message": str(e)}], ensure_ascii=False)
                    )
                except Exception:
                    # Si no se puede actualizar el estado, continuar con el error original
                    pass
            # Re-lanzar como DatabaseError si es un error de BD, o como BusinessLogicError
            if "database" in str(e).lower() or "sql" in str(e).lower():
                raise DatabaseError(f"Error al procesar archivo: {str(e)}")
            raise ExternalServiceError(f"Error al procesar archivo: {str(e)}", service="procesamiento")
        
        # Retornar información del archivo procesado
        return {
            "file_id": file_upload.id,
            "filename": filename,
            "s3_url": s3_url,
            "status": final_status,
            "validations": validations,
            "records_count": records_count,
            "categoria": categoria,
            "descripcion": descripcion,
            "uploaded_at": file_upload.created_at
        }

