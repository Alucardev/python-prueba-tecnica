"""
Tests para los endpoints de autenticación.
"""
import pytest
from fastapi import status
from app.modules.auth.repository import UserRepository
from app.modules.documents.repository import EventLogRepository


class TestLogin:
    """Tests para el endpoint de login."""
    
    def test_login_success(self, client, test_user, db_session):
        """Test de login exitoso."""
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "testpassword123"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 900  # 15 minutos en segundos
        assert len(data["access_token"]) > 0
        
        # Verificar que se creó un evento de login
        event_repo = EventLogRepository(db_session)
        events = event_repo.get_events(event_type="user_login", user_id=test_user.id)
        assert len(events) > 0
        assert events[0].event_type == "user_login"
        assert events[0].user_id == test_user.id
        assert "testuser" in events[0].description
    
    def test_login_invalid_username(self, client):
        """Test de login con usuario inexistente."""
        response = client.post(
            "/auth/login",
            json={"username": "nonexistent", "password": "password123"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["error"] is True
        assert "Credenciales inválidas" in data["message"]
        assert data["type"] == "AuthenticationError"
    
    def test_login_invalid_password(self, client, test_user):
        """Test de login con contraseña incorrecta."""
        response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["error"] is True
        assert "Credenciales inválidas" in data["message"]
    
    def test_login_missing_fields(self, client):
        """Test de login con campos faltantes."""
        response = client.post(
            "/auth/login",
            json={"username": "testuser"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["error"] is True
        assert "validación" in data["message"].lower()
    
    def test_login_empty_request(self, client):
        """Test de login con request vacío."""
        response = client.post("/auth/login", json={})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRefreshToken:
    """Tests para el endpoint de refresh token."""
    
    def test_refresh_token_success(self, client, auth_token):
        """Test de renovación de token exitosa."""
        response = client.post(
            "/auth/refresh",
            json={"access_token": auth_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 900
        # El nuevo token debe ser diferente al original
        assert data["access_token"] != auth_token
    
    def test_refresh_token_invalid(self, client):
        """Test de renovación con token inválido."""
        response = client.post(
            "/auth/refresh",
            json={"access_token": "invalid_token_here"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["error"] is True
        assert "Token inválido" in data["message"]
    
    def test_refresh_token_missing(self, client):
        """Test de renovación sin token."""
        response = client.post(
            "/auth/refresh",
            json={}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_refresh_token_empty_string(self, client):
        """Test de renovación con token vacío."""
        response = client.post(
            "/auth/refresh",
            json={"access_token": ""}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenContent:
    """Tests para verificar el contenido del token JWT."""
    
    def test_token_contains_user_info(self, client, test_user, auth_token):
        """Verifica que el token contiene información del usuario."""
        from jose import jwt
        from app.config import settings
        
        decoded = jwt.decode(
            auth_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        assert decoded["id_usuario"] == test_user.id
        assert decoded["rol"] == test_user.role  # role es ahora un string directamente
        assert "exp" in decoded
    
    def test_token_different_roles(self, client, test_admin_user, test_uploader_user):
        """Verifica que tokens de diferentes roles tienen roles diferentes."""
        admin_response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        uploader_response = client.post(
            "/auth/login",
            json={"username": "uploader", "password": "uploader123"}
        )
        
        admin_token = admin_response.json()["access_token"]
        uploader_token = uploader_response.json()["access_token"]
        
        from jose import jwt
        from app.config import settings
        
        admin_decoded = jwt.decode(
            admin_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        uploader_decoded = jwt.decode(
            uploader_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        assert admin_decoded["rol"] == "admin"
        assert uploader_decoded["rol"] == "uploader"
        assert admin_decoded["rol"] != uploader_decoded["rol"]

