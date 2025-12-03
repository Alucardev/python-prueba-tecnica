"""
Tests para los middlewares de la aplicación.
"""
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from app.middleware.auth import get_current_user, require_role
from app.exceptions.custom_exceptions import AuthenticationError, AuthorizationError
from app.schemas.auth import TokenData


class TestAuthMiddleware:
    """Tests para el middleware de autenticación."""
    
    def test_get_current_user_valid_token(self, db_session, test_user, auth_token):
        """Test de obtención de usuario con token válido."""
        from app.database import get_db
        from app.main import app
        
        app.dependency_overrides[get_db] = lambda: db_session
        
        # Crear un endpoint de prueba
        @app.get("/test-auth")
        async def test_endpoint(current_user: TokenData = Depends(get_current_user)):
            return {"user_id": current_user.id_usuario, "rol": current_user.rol}
        
        client = TestClient(app)
        response = client.get(
            "/test-auth",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["rol"] == test_user.role  # role es ahora un string directamente
        
        app.dependency_overrides.clear()
    
    def test_get_current_user_invalid_token(self, db_session):
        """Test de obtención de usuario con token inválido."""
        from app.database import get_db
        from app.main import app
        
        app.dependency_overrides[get_db] = lambda: db_session
        
        @app.get("/test-auth")
        async def test_endpoint(current_user: TokenData = Depends(get_current_user)):
            return {"user_id": current_user.id_usuario}
        
        client = TestClient(app)
        response = client.get(
            "/test-auth",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"] is True
        assert "Token inválido" in data["message"]
        
        app.dependency_overrides.clear()
    
    def test_get_current_user_missing_token(self, db_session):
        """Test de obtención de usuario sin token."""
        from app.database import get_db
        from app.main import app
        
        app.dependency_overrides[get_db] = lambda: db_session
        
        @app.get("/test-auth")
        async def test_endpoint(current_user: TokenData = Depends(get_current_user)):
            return {"user_id": current_user.id_usuario}
        
        client = TestClient(app)
        response = client.get("/test-auth")
        
        assert response.status_code == 403  # FastAPI security retorna 403 sin token
        
        app.dependency_overrides.clear()
    
    def test_require_role_success(self, db_session, admin_token):
        """Test de requerimiento de rol exitoso."""
        from app.database import get_db
        from app.main import app
        from app.config import settings
        
        app.dependency_overrides[get_db] = lambda: db_session
        
        @app.get("/test-role")
        async def test_endpoint(
            current_user: TokenData = Depends(require_role(settings.ALLOWED_ROLES_FOR_FILE_UPLOAD))
        ):
            return {"rol": current_user.rol}
        
        client = TestClient(app)
        response = client.get(
            "/test-role",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["rol"] == "admin"
        
        app.dependency_overrides.clear()
    
    def test_require_role_forbidden(self, db_session, auth_token):
        """Test de requerimiento de rol con rol incorrecto."""
        from app.database import get_db
        from app.main import app
        from app.config import settings
        
        app.dependency_overrides[get_db] = lambda: db_session
        
        @app.get("/test-role")
        async def test_endpoint(
            current_user: TokenData = Depends(require_role(settings.ALLOWED_ROLES_FOR_FILE_UPLOAD))
        ):
            return {"rol": current_user.rol}
        
        client = TestClient(app)
        response = client.get(
            "/test-role",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 403
        data = response.json()
        assert data["error"] is True
        assert "Acceso denegado" in data["message"]
        
        app.dependency_overrides.clear()


class TestErrorHandlerMiddleware:
    """Tests para el middleware de manejo de errores."""
    
    def test_custom_exception_handling(self, client):
        """Test de manejo de excepciones personalizadas."""
        from app.main import app
        from app.exceptions.custom_exceptions import ValidationError
        
        @app.get("/test-error")
        async def test_endpoint():
            raise ValidationError("Test error message")
        
        response = client.get("/test-error")
        
        assert response.status_code == 400
        data = response.json()
        assert data["error"] is True
        assert data["message"] == "Test error message"
        assert data["type"] == "ValidationError"
    
    def test_validation_error_handling(self, client):
        """Test de manejo de errores de validación de Pydantic."""
        response = client.post(
            "/auth/login",
            json={"username": "test"}  # Falta password
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["error"] is True
        assert "validación" in data["message"].lower()
        assert "details" in data

