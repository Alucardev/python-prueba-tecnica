"""
Tests para el módulo de documentos (análisis con AWS Textract).
"""
import pytest
from fastapi import status
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from app.modules.documents.repository import DocumentRepository, EventLogRepository
from app.modules.documents.service import DocumentService
from app.modules.documents.models import Document, EventLog


class TestDocumentRepository:
    """Tests para el repositorio de documentos."""

    def test_create_document(self, db_session, test_user):
        """Test de creación de documento."""
        document_repo = DocumentRepository(db_session)

        document = document_repo.create_document(
            original_filename="test.pdf",
            file_type="PDF",
            s3_key="uploads/2024/01/01/test-uuid.pdf",
            s3_url="https://bucket.s3.region.amazonaws.com/uploads/2024/01/01/test-uuid.pdf",
            user_id=test_user.id,
            classification="Factura",
            status="processing",
        )

        assert document.id is not None
        assert document.original_filename == "test.pdf"
        assert document.file_type == "PDF"
        assert document.user_id == test_user.id
        assert document.classification == "Factura"
        assert document.status == "processing"

    def test_get_document_by_id(self, db_session, test_user):
        """Test de obtención de documento por ID."""
        document_repo = DocumentRepository(db_session)

        # Crear documento
        document = document_repo.create_document(
            original_filename="test.pdf",
            file_type="PDF",
            s3_key="uploads/test.pdf",
            s3_url="https://bucket.s3/test.pdf",
            user_id=test_user.id,
            classification="Factura",
        )

        # Obtener documento
        found = document_repo.get_document_by_id(document.id)

        assert found is not None
        assert found.id == document.id
        assert found.original_filename == "test.pdf"

    def test_get_document_by_id_not_found(self, db_session):
        """Test de obtención de documento inexistente."""
        document_repo = DocumentRepository(db_session)

        document = document_repo.get_document_by_id(99999)

        assert document is None

    def test_update_document_analysis(self, db_session, test_user):
        """Test de actualización de análisis de documento."""
        document_repo = DocumentRepository(db_session)

        # Crear documento
        document = document_repo.create_document(
            original_filename="test.pdf",
            file_type="PDF",
            s3_key="uploads/test.pdf",
            s3_url="https://bucket.s3/test.pdf",
            user_id=test_user.id,
            classification="processing",
            status="processing",
        )

        # Actualizar análisis
        extracted_data = {"cliente": "Test Cliente", "total": "100.00"}
        updated = document_repo.update_document_analysis(
            document_id=document.id,
            classification="Factura",
            status="completed",
            extracted_data=extracted_data,
        )

        assert updated is not None
        assert updated.classification == "Factura"
        assert updated.status == "completed"
        assert updated.extracted_data == extracted_data

    def test_get_all_documents(self, db_session, test_user):
        """Test de obtención de todos los documentos."""
        document_repo = DocumentRepository(db_session)

        # Crear varios documentos
        for i in range(3):
            document_repo.create_document(
                original_filename=f"test{i}.pdf",
                file_type="PDF",
                s3_key=f"uploads/test{i}.pdf",
                s3_url=f"https://bucket.s3/test{i}.pdf",
                user_id=test_user.id,
                classification="Factura" if i % 2 == 0 else "Información",
            )

        # Obtener todos
        documents = document_repo.get_all_documents(user_id=test_user.id)

        assert len(documents) == 3

    def test_get_all_documents_with_filter(self, db_session, test_user):
        """Test de obtención de documentos con filtro."""
        document_repo = DocumentRepository(db_session)

        # Crear documentos con diferentes clasificaciones
        document_repo.create_document(
            original_filename="factura.pdf",
            file_type="PDF",
            s3_key="uploads/factura.pdf",
            s3_url="https://bucket.s3/factura.pdf",
            user_id=test_user.id,
            classification="Factura",
        )
        document_repo.create_document(
            original_filename="info.pdf",
            file_type="PDF",
            s3_key="uploads/info.pdf",
            s3_url="https://bucket.s3/info.pdf",
            user_id=test_user.id,
            classification="Información",
        )

        # Filtrar por Factura
        facturas = document_repo.get_all_documents(
            user_id=test_user.id, classification="Factura"
        )
        assert len(facturas) == 1
        assert facturas[0].classification == "Factura"

        # Filtrar por Información
        informacion = document_repo.get_all_documents(
            user_id=test_user.id, classification="Información"
        )
        assert len(informacion) == 1
        assert informacion[0].classification == "Información"


class TestEventLogRepository:
    """Tests para el repositorio de eventos históricos."""

    def test_create_event(self, db_session, test_user):
        """Test de creación de evento."""
        event_repo = EventLogRepository(db_session)

        event = event_repo.create_event(
            event_type="document_upload",
            description="Documento subido",
            user_id=test_user.id,
            metadata={"filename": "test.pdf"},
        )

        assert event.id is not None
        assert event.event_type == "document_upload"
        assert event.description == "Documento subido"
        assert event.user_id == test_user.id
        assert event.event_metadata == {"filename": "test.pdf"}

    def test_get_event_by_id(self, db_session, test_user):
        """Test de obtención de evento por ID."""
        event_repo = EventLogRepository(db_session)

        # Crear evento
        event = event_repo.create_event(
            event_type="ai_analysis",
            description="Análisis completado",
            user_id=test_user.id,
        )

        # Obtener evento
        found = event_repo.get_event_by_id(event.id)

        assert found is not None
        assert found.id == event.id
        assert found.event_type == "ai_analysis"

    def test_get_events_with_filters(self, db_session, test_user):
        """Test de obtención de eventos con filtros."""
        event_repo = EventLogRepository(db_session)

        # Crear varios eventos
        event_repo.create_event(
            event_type="document_upload",
            description="Documento 1 subido",
            user_id=test_user.id,
        )
        event_repo.create_event(
            event_type="ai_analysis",
            description="Análisis completado",
            user_id=test_user.id,
        )
        event_repo.create_event(
            event_type="document_upload",
            description="Documento 2 subido",
            user_id=test_user.id,
        )

        # Filtrar por tipo
        upload_events = event_repo.get_events(event_type="document_upload")
        assert len(upload_events) == 2

        # Filtrar por descripción
        analysis_events = event_repo.get_events(description_filter="Análisis")
        assert len(analysis_events) == 1
        assert analysis_events[0].event_type == "ai_analysis"

    def test_get_events_by_user(self, db_session, test_user, test_admin_user):
        """Test de obtención de eventos por usuario."""
        event_repo = EventLogRepository(db_session)

        # Crear eventos para diferentes usuarios
        event_repo.create_event(
            event_type="document_upload",
            description="Evento usuario 1",
            user_id=test_user.id,
        )
        event_repo.create_event(
            event_type="document_upload",
            description="Evento usuario 2",
            user_id=test_admin_user.id,
        )

        # Filtrar por usuario
        user_events = event_repo.get_events(user_id=test_user.id)
        assert len(user_events) == 1
        assert user_events[0].user_id == test_user.id


class TestDocumentService:
    """Tests para el servicio de documentos."""

    @patch("app.modules.documents.service.TextractService")
    @patch("app.modules.documents.service.S3Service")
    def test_upload_and_analyze_document_success(
        self, mock_s3_class, mock_textract_class, db_session, test_user
    ):
        """Test de subida y análisis exitoso de documento."""
        # Configurar mocks
        mock_s3 = MagicMock()
        mock_s3.bucket_name = "test-bucket"
        mock_s3.upload_file.return_value = (
            "uploads/test.pdf",
            "https://bucket.s3/test.pdf",
        )
        mock_s3_class.return_value = mock_s3

        mock_textract = MagicMock()
        # Mock de respuesta de Textract
        mock_textract.detect_document_text.return_value = {
            "Blocks": [
                {"BlockType": "LINE", "Text": "FACTURA"},
                {"BlockType": "LINE", "Text": "Total: 100.00"},
                {"BlockType": "LINE", "Text": "Cliente: Test"},
            ]
        }
        mock_textract.classify_document.return_value = "Factura"
        mock_textract.analyze_document.return_value = {
            "Blocks": [
                {"BlockType": "LINE", "Text": "FACTURA"},
                {"BlockType": "LINE", "Text": "Total: 100.00"},
            ]
        }
        mock_textract.extract_invoice_data.return_value = {
            "cliente": {"nombre": "Test Cliente"},
            "total": "100.00",
        }
        mock_textract_class.return_value = mock_textract

        # Crear servicio
        document_repo = DocumentRepository(db_session)
        event_repo = EventLogRepository(db_session)
        s3_service = mock_s3
        textract_service = mock_textract

        service = DocumentService(document_repo, event_repo, s3_service, textract_service)

        # Ejecutar
        file_content = b"fake pdf content"
        result = service.upload_and_analyze_document(
            file_content=file_content,
            filename="test.pdf",
            user_id=test_user.id,
        )

        # Verificar
        assert result["document_id"] is not None
        assert result["filename"] == "test.pdf"
        assert result["classification"] == "Factura"
        assert result["status"] == "completed"
        assert "extracted_data" in result

        # Verificar que se llamó a S3
        mock_s3.upload_file.assert_called_once()

        # Verificar que se llamó a Textract
        mock_textract.detect_document_text.assert_called_once()
        mock_textract.analyze_document.assert_called_once()

    @patch("app.modules.documents.service.TextractService")
    @patch("app.modules.documents.service.S3Service")
    def test_upload_and_analyze_document_s3_error(
        self, mock_s3_class, mock_textract_class, db_session, test_user
    ):
        """Test de error al subir a S3."""
        # Configurar mock de S3 para que falle
        mock_s3 = MagicMock()
        mock_s3.upload_file.side_effect = Exception("S3 Error")
        mock_s3_class.return_value = mock_s3

        mock_textract = MagicMock()
        mock_textract_class.return_value = mock_textract

        # Crear servicio
        document_repo = DocumentRepository(db_session)
        event_repo = EventLogRepository(db_session)
        service = DocumentService(
            document_repo, event_repo, mock_s3, mock_textract
        )

        # Ejecutar y verificar que lanza excepción
        with pytest.raises(Exception) as exc_info:
            service.upload_and_analyze_document(
                file_content=b"content",
                filename="test.pdf",
                user_id=test_user.id,
            )

        assert "S3" in str(exc_info.value)

    def test_get_file_type(self, db_session, test_user):
        """Test de determinación de tipo de archivo."""
        document_repo = DocumentRepository(db_session)
        event_repo = EventLogRepository(db_session)

        # Crear servicio con mocks
        with patch("app.modules.documents.service.S3Service"), patch(
            "app.modules.documents.service.TextractService"
        ):
            service = DocumentService(
                document_repo,
                event_repo,
                MagicMock(),
                MagicMock(),
            )

            # Usar el método privado a través de reflección
            file_type_pdf = service._get_file_type("test.pdf")
            assert file_type_pdf == "PDF"

            file_type_jpg = service._get_file_type("test.jpg")
            assert file_type_jpg == "JPG"

            file_type_png = service._get_file_type("test.png")
            assert file_type_png == "PNG"


class TestDocumentEndpoints:
    """Tests para los endpoints de documentos."""

    def test_upload_document_success(
        self, client, admin_token, sample_csv_content
    ):
        """Test de endpoint de subida de documento exitosa."""
        # Crear contenido de PDF simulado
        pdf_content = b"%PDF-1.4 fake pdf content"

        with patch("app.modules.documents.router.S3Service") as mock_s3_class, patch(
            "app.modules.documents.router.TextractService"
        ) as mock_textract_class:
            # Configurar mocks
            mock_s3 = MagicMock()
            mock_s3.bucket_name = "test-bucket"
            mock_s3.upload_file.return_value = (
                "uploads/test.pdf",
                "https://bucket.s3/test.pdf",
            )
            mock_s3_class.return_value = mock_s3

            mock_textract = MagicMock()
            mock_textract.detect_document_text.return_value = {
                "Blocks": [{"BlockType": "LINE", "Text": "Test document"}]
            }
            mock_textract.classify_document.return_value = "Información"
            mock_textract.extract_information_data.return_value = {
                "descripcion": "Test document",
                "resumen": "Test",
            }
            mock_textract_class.return_value = mock_textract

            files = {"file": ("test.pdf", pdf_content, "application/pdf")}

            response = client.post(
                "/documents/upload",
                headers={"Authorization": f"Bearer {admin_token}"},
                files=files,
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert "document_id" in data
            assert data["filename"] == "test.pdf"
            assert data["classification"] in ["Factura", "Información"]
            assert "s3_url" in data

    def test_upload_document_unauthorized(self, client, sample_csv_content):
        """Test de subida sin autenticación."""
        pdf_content = b"%PDF-1.4 fake pdf content"
        files = {"file": ("test.pdf", pdf_content, "application/pdf")}

        response = client.post("/documents/upload", files=files)

        # Puede ser 401 o 403 dependiendo del middleware
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_upload_document_invalid_file_type(self, client, admin_token):
        """Test de subida con tipo de archivo inválido."""
        invalid_content = b"invalid content"
        files = {"file": ("test.txt", invalid_content, "text/plain")}

        response = client.post(
            "/documents/upload",
            headers={"Authorization": f"Bearer {admin_token}"},
            files=files,
        )

        # El error handler devuelve 400 para ValidationError
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]
        assert "error" in response.json() or "Tipo de archivo no permitido" in str(response.json())

    def test_get_documents(self, client, admin_token, db_session, test_user):
        """Test de obtención de lista de documentos."""
        # Crear documentos de prueba
        document_repo = DocumentRepository(db_session)
        for i in range(2):
            document_repo.create_document(
                original_filename=f"test{i}.pdf",
                file_type="PDF",
                s3_key=f"uploads/test{i}.pdf",
                s3_url=f"https://bucket.s3/test{i}.pdf",
                user_id=test_user.id,
                classification="Factura",
            )

        response = client.get(
            "/documents/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_document_by_id(self, client, auth_token, db_session, test_user):
        """Test de obtención de documento por ID."""
        # Crear documento con el mismo usuario que tiene el token
        document_repo = DocumentRepository(db_session)
        document = document_repo.create_document(
            original_filename="test.pdf",
            file_type="PDF",
            s3_key="uploads/test.pdf",
            s3_url="https://bucket.s3/test.pdf",
            user_id=test_user.id,
            classification="Factura",
        )

        response = client.get(
            f"/documents/{document.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == document.id
        assert data["original_filename"] == "test.pdf"

    def test_get_document_not_found(self, client, admin_token):
        """Test de obtención de documento inexistente."""
        response = client.get(
            "/documents/99999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_event_history(self, client, admin_token, db_session, test_user):
        """Test de obtención de historial de eventos."""
        # Crear eventos de prueba
        event_repo = EventLogRepository(db_session)
        event_repo.create_event(
            event_type="document_upload",
            description="Test event",
            user_id=test_user.id,
        )

        response = client.get(
            "/documents/events/history",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "events" in data
        assert "total" in data
        assert isinstance(data["events"], list)

    def test_get_event_history_with_filters(
        self, client, admin_token, db_session, test_user
    ):
        """Test de historial de eventos con filtros."""
        event_repo = EventLogRepository(db_session)
        event_repo.create_event(
            event_type="document_upload",
            description="Upload event",
            user_id=test_user.id,
        )
        event_repo.create_event(
            event_type="ai_analysis",
            description="Analysis event",
            user_id=test_user.id,
        )

        # Filtrar por tipo
        response = client.get(
            "/documents/events/history?event_type=document_upload",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(event["event_type"] == "document_upload" for event in data["events"])

    @patch("app.modules.documents.router.openpyxl")
    def test_export_events_to_excel(
        self, mock_openpyxl, client, admin_token, db_session, test_user
    ):
        """Test de exportación de eventos a Excel."""
        # Mock de openpyxl
        mock_workbook = MagicMock()
        mock_worksheet = MagicMock()
        mock_workbook.active = mock_worksheet
        mock_openpyxl.Workbook.return_value = mock_workbook
        
        # Crear eventos de prueba
        event_repo = EventLogRepository(db_session)
        event_repo.create_event(
            event_type="document_upload",
            description="Test event",
            user_id=test_user.id,
        )

        response = client.get(
            "/documents/events/export",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert "attachment" in response.headers.get("content-disposition", "")

