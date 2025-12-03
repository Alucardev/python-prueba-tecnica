"""
Tests para los servicios de la aplicación.
"""
import pytest
from unittest.mock import patch, MagicMock

from app.exceptions.custom_exceptions import ExternalServiceError
from app.modules.auth.repository import UserRepository
from app.modules.auth.service import AuthService
from app.modules.csv.repository import FileRepository
from app.modules.csv.service import FileService
from app.shared.s3_service import S3Service


class TestAuthService:
    """Tests para el servicio de autenticación."""
    
    def test_authenticate_user_success(self, db_session, test_user):
        """Test de autenticación exitosa."""
        user_repository = UserRepository(db_session)
        auth_service = AuthService(user_repository)
        
        user = auth_service.authenticate_user("testuser", "testpassword123")
        
        assert user is not None
        assert user.username == "testuser"
        assert user.id == test_user.id
    
    def test_authenticate_user_invalid_password(self, db_session, test_user):
        """Test de autenticación con contraseña incorrecta."""
        user_repository = UserRepository(db_session)
        auth_service = AuthService(user_repository)
        
        user = auth_service.authenticate_user("testuser", "wrongpassword")
        
        assert user is None
    
    def test_authenticate_user_not_found(self, db_session):
        """Test de autenticación con usuario inexistente."""
        user_repository = UserRepository(db_session)
        auth_service = AuthService(user_repository)
        
        user = auth_service.authenticate_user("nonexistent", "password")
        
        assert user is None
    
    def test_create_access_token(self, db_session, test_user):
        """Test de creación de token JWT."""
        user_repository = UserRepository(db_session)
        auth_service = AuthService(user_repository)
        
        token = auth_service.create_access_token(test_user)
        
        assert token is not None
        assert len(token) > 0
        
        # Verificar que se puede decodificar
        from jose import jwt
        from app.config import settings
        
        decoded = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        assert decoded["id_usuario"] == test_user.id
        assert decoded["rol"] == test_user.role
    
    def test_verify_token_valid(self, db_session, test_user):
        """Test de verificación de token válido."""
        user_repository = UserRepository(db_session)
        auth_service = AuthService(user_repository)
        
        token = auth_service.create_access_token(test_user)
        token_data = auth_service.verify_token(token)
        
        assert token_data is not None
        assert token_data.id_usuario == test_user.id
        assert token_data.rol == test_user.role
    
    def test_verify_token_invalid(self, db_session):
        """Test de verificación de token inválido."""
        user_repository = UserRepository(db_session)
        auth_service = AuthService(user_repository)
        
        token_data = auth_service.verify_token("invalid_token")
        
        assert token_data is None
    
    def test_refresh_token_success(self, db_session, test_user):
        """Test de renovación de token exitosa."""
        user_repository = UserRepository(db_session)
        auth_service = AuthService(user_repository)
        
        original_token = auth_service.create_access_token(test_user)
        new_token = auth_service.refresh_token(original_token)
        
        assert new_token is not None
        assert new_token != original_token
        
        # Verificar que el nuevo token es válido
        token_data = auth_service.verify_token(new_token)
        assert token_data is not None
        assert token_data.id_usuario == test_user.id
    
    def test_refresh_token_invalid(self, db_session):
        """Test de renovación con token inválido."""
        user_repository = UserRepository(db_session)
        auth_service = AuthService(user_repository)
        
        new_token = auth_service.refresh_token("invalid_token")
        
        assert new_token is None


class TestFileService:
    """Tests para el servicio de archivos."""
    
    @patch("app.shared.s3_service.S3Service.upload_file")
    def test_upload_and_process_csv_success(self, mock_s3_upload, db_session, test_user):
        """Test de procesamiento de CSV exitoso."""
        mock_s3_upload.return_value = (
            "uploads/2024/01/01/test.csv",
            "https://bucket.s3.amazonaws.com/uploads/2024/01/01/test.csv"
        )
        
        csv_content = b"""id,nombre,email
1,Juan,juan@test.com
2,Maria,maria@test.com"""
        
        file_repository = FileRepository(db_session)
        s3_service = S3Service()
        file_service = FileService(file_repository, s3_service)
        
        result = file_service.upload_and_process_csv(
            file_content=csv_content,
            filename="test.csv",
            user_id=test_user.id,
            categoria="test",
            descripcion="test description"
        )
        
        assert result["file_id"] is not None
        assert result["filename"] == "test.csv"
        assert result["categoria"] == "test"
        assert result["descripcion"] == "test description"
        assert result["records_count"] == 2
        assert "validations" in result
    
    @patch("app.shared.s3_service.S3Service.upload_file")
    def test_upload_and_process_csv_s3_error(self, mock_s3_upload, db_session, test_user):
        """Test de error al subir a S3."""
        mock_s3_upload.side_effect = Exception("S3 Error")
        
        csv_content = b"""id,nombre
1,Juan"""
        
        file_repository = FileRepository(db_session)
        s3_service = S3Service()
        file_service = FileService(file_repository, s3_service)
        
        with pytest.raises(ExternalServiceError) as exc_info:
            file_service.upload_and_process_csv(
                file_content=csv_content,
                filename="test.csv",
                user_id=test_user.id
            )
        
        assert "S3" in str(exc_info.value.message)


class TestS3Service:
    """Tests para el servicio de S3."""
    
    @patch('boto3.client')
    def test_upload_file_success(self, mock_boto_client, sample_csv_content):
        """Test de subida exitosa a S3."""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        s3_service = S3Service()
        s3_key, s3_url = s3_service.upload_file(
            sample_csv_content,
            "test.csv",
            categoria="test",
            descripcion="test description"
        )
        
        assert s3_key is not None
        assert s3_url is not None
        assert "test.csv" in s3_key
        # Verificar que se llamó put_object con metadata
        mock_s3.put_object.assert_called_once()
        call_args = mock_s3.put_object.call_args
        assert "Metadata" in call_args.kwargs
        assert call_args.kwargs["Metadata"]["categoria"] == "test"
        assert call_args.kwargs["Metadata"]["descripcion"] == "test description"
    
    @patch('boto3.client')
    def test_upload_file_error(self, mock_boto_client, sample_csv_content):
        """Test de error al subir a S3."""
        from botocore.exceptions import ClientError
        
        mock_s3 = MagicMock()
        mock_s3.put_object.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "PutObject"
        )
        mock_boto_client.return_value = mock_s3
        
        s3_service = S3Service()
        
        with pytest.raises(ExternalServiceError) as exc_info:
            s3_service.upload_file(sample_csv_content, "test.csv")
        
        assert "S3" in str(exc_info.value.message)

