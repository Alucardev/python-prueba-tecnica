"""
Tests para los endpoints de archivos.
"""
import pytest
from fastapi import status
from unittest.mock import Mock, patch, MagicMock
import io


class TestFileUpload:
    """Tests para el endpoint de carga de archivos."""
    
    def test_upload_file_success(self, client, uploader_token, sample_csv_content):
        """Test de carga de archivo exitosa."""
        # Mockear S3Service para evitar llamadas reales a AWS
        with patch("app.shared.s3_service.S3Service.upload_file") as mock_s3:
            mock_s3.return_value = (
                "uploads/2024/01/01/test-uuid.csv",
                "https://bucket.s3.region.amazonaws.com/uploads/2024/01/01/test-uuid.csv"
            )
            
            files = {"file": ("test.csv", sample_csv_content, "text/csv")}
            data = {
                "categoria": "ventas",
                "descripcion": "Archivo de prueba"
            }
            
            response = client.post(
                "/files/upload",
                headers={"Authorization": f"Bearer {uploader_token}"},
                files=files,
                data=data
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data_response = response.json()
            assert "file_id" in data_response
            assert data_response["filename"] == "test.csv"
            assert data_response["categoria"] == "ventas"
            assert data_response["descripcion"] == "Archivo de prueba"
            assert "s3_url" in data_response
            assert "validations" in data_response
            assert "records_count" in data_response
    
    def test_upload_file_unauthorized(self, client, sample_csv_content):
        """Test de carga sin autenticación."""
        files = {"file": ("test.csv", sample_csv_content, "text/csv")}
        
        response = client.post(
            "/files/upload",
            files=files
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_upload_file_wrong_role(self, client, auth_token, sample_csv_content):
        """Test de carga con rol incorrecto."""
        files = {"file": ("test.csv", sample_csv_content, "text/csv")}
        
        response = client.post(
            "/files/upload",
            headers={"Authorization": f"Bearer {auth_token}"},
            files=files
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert data["error"] is True
        assert "Acceso denegado" in data["message"]
    
    def test_upload_file_invalid_extension(self, client, uploader_token):
        """Test de carga con archivo que no es CSV."""
        files = {"file": ("test.txt", b"contenido", "text/plain")}
        
        response = client.post(
            "/files/upload",
            headers={"Authorization": f"Bearer {uploader_token}"},
            files=files
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["error"] is True
        assert "CSV" in data["message"]
    
    def test_upload_file_admin_role(self, client, admin_token, sample_csv_content):
        """Test de que admin puede subir archivos."""
        with patch("app.shared.s3_service.S3Service.upload_file") as mock_s3:
            mock_s3.return_value = (
                "uploads/2024/01/01/test-uuid.csv",
                "https://bucket.s3.region.amazonaws.com/uploads/2024/01/01/test-uuid.csv"
            )
            
            files = {"file": ("test.csv", sample_csv_content, "text/csv")}
            
            response = client.post(
                "/files/upload",
                headers={"Authorization": f"Bearer {admin_token}"},
                files=files
            )
            
            assert response.status_code == status.HTTP_201_CREATED
    
    def test_upload_file_with_categoria_and_descripcion(self, client, uploader_token, sample_csv_content):
        """Test de carga con categoria y descripcion."""
        with patch("app.shared.s3_service.S3Service.upload_file") as mock_s3:
            mock_s3.return_value = (
                "uploads/2024/01/01/test-uuid.csv",
                "https://bucket.s3.region.amazonaws.com/uploads/2024/01/01/test-uuid.csv"
            )
            
            files = {"file": ("test.csv", sample_csv_content, "text/csv")}
            data = {
                "categoria": "test-categoria",
                "descripcion": "test-descripcion"
            }
            
            response = client.post(
                "/files/upload",
                headers={"Authorization": f"Bearer {uploader_token}"},
                files=files,
                data=data
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data_response = response.json()
            assert data_response["categoria"] == "test-categoria"
            assert data_response["descripcion"] == "test-descripcion"
    
    def test_upload_file_empty_csv(self, client, uploader_token):
        """Test de carga con CSV vacío."""
        with patch("app.shared.s3_service.S3Service.upload_file") as mock_s3:
            mock_s3.return_value = (
                "uploads/2024/01/01/test-uuid.csv",
                "https://bucket.s3.region.amazonaws.com/uploads/2024/01/01/test-uuid.csv"
            )
            
            # CSV solo con headers, sin datos
            empty_csv = b"id,nombre,email\n"
            files = {"file": ("empty.csv", empty_csv, "text/csv")}
            
            response = client.post(
                "/files/upload",
                headers={"Authorization": f"Bearer {uploader_token}"},
                files=files
            )
            
            # Debe procesarse pero con validación de archivo vacío
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["records_count"] == 0
    
    def test_upload_file_invalid_token(self, client, sample_csv_content):
        """Test de carga con token inválido."""
        files = {"file": ("test.csv", sample_csv_content, "text/csv")}
        
        response = client.post(
            "/files/upload",
            headers={"Authorization": "Bearer invalid_token"},
            files=files
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

