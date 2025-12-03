"""
Middleware de Autenticación.
Maneja la validación de tokens JWT y control de acceso por roles.
"""
from fastapi import Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenData
from app.config import settings
from app.database import get_db
from app.exceptions.custom_exceptions import AuthenticationError, AuthorizationError
from sqlalchemy.orm import Session
from typing import List, Optional


# Esquema de seguridad HTTP Bearer
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
) -> TokenData:
    """
    Obtiene el usuario actual a partir del token JWT.
    
    Args:
        credentials: Credenciales HTTP Bearer
        db: Sesión de base de datos
        
    Returns:
        Datos del token (usuario autenticado)
        
    Raises:
        HTTPException: Si el token es inválido o ha expirado
    """
    token = credentials.credentials
    
    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository)
    
    token_data = auth_service.verify_token(token)
    if token_data is None:
        raise AuthenticationError("Token inválido o expirado")
    
    return token_data


def require_role(allowed_roles: List[str]):
    """
    Decorador/dependencia para requerir roles específicos.
    
    Args:
        allowed_roles: Lista de roles permitidos
        
    Returns:
        Función de dependencia que valida el rol
    """
    def role_checker(current_user: TokenData = Depends(get_current_user)) -> TokenData:
        """
        Verifica si el usuario tiene uno de los roles permitidos.
        
        Args:
            current_user: Usuario actual autenticado
            
        Returns:
            Datos del token si el rol es válido
            
        Raises:
            HTTPException: Si el usuario no tiene el rol requerido
        """
        if current_user.rol not in allowed_roles:
            raise AuthorizationError(
                f"Acceso denegado. Se requiere uno de los siguientes roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker

