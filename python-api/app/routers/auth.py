"""
Router de Autenticación.
Define los endpoints relacionados con autenticación y tokens JWT.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.exceptions.custom_exceptions import AuthenticationError
from app.modules.auth.repository import UserRepository
from app.modules.auth.schemas import (
    LoginRequest,
    TokenResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
)
from app.modules.auth.service import AuthService
from app.modules.documents.repository import EventLogRepository

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para iniciar sesión.
    Permite a usuarios anónimos autenticarse y obtener un JWT.
    
    Args:
        login_data: Datos de inicio de sesión (username y password)
        db: Sesión de base de datos
        
    Returns:
        Token JWT con información del usuario
        
    Raises:
        HTTPException: Si las credenciales son inválidas
    """
    # Crear repositorio y servicio
    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository)
    
    # Autenticar usuario
    user = auth_service.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise AuthenticationError("Credenciales inválidas")
    
    # Crear token JWT
    access_token = auth_service.create_access_token(user)
    
    # Registrar evento de login
    try:
        event_repository = EventLogRepository(db)
        event_repository.create_event(
            event_type="user_login",
            description=f"Usuario {login_data.username} inició sesión",
            user_id=user.id,
            metadata={
                "username": login_data.username,
                "login_timestamp": datetime.utcnow().isoformat(),
            }
        )
        # create_event ya hace commit internamente, no necesitamos otro commit
    except Exception as e:
        # Si falla el registro del evento, no interrumpir el login
        # En producción usar un logger para registrar el error
        import traceback
        print(f"Error al registrar evento de login: {str(e)}")
        traceback.print_exc()
        # No hacer rollback aquí porque create_event ya maneja su propia transacción
    
    # Calcular tiempo de expiración en segundos
    expires_in = settings.JWT_EXPIRATION_MINUTES * 60
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in
    )


@router.post("/refresh", response_model=TokenRefreshResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para renovar un token JWT.
    Genera un nuevo token con tiempo de expiración adicional.
    Solo funciona si el token original aún no ha expirado.
    
    Args:
        refresh_data: Token JWT original
        db: Sesión de base de datos
        
    Returns:
        Nuevo token JWT
        
    Raises:
        HTTPException: Si el token es inválido o ha expirado
    """
    # Crear repositorio y servicio
    user_repository = UserRepository(db)
    auth_service = AuthService(user_repository)
    
    # Renovar el token
    new_token = auth_service.refresh_token(refresh_data.access_token)
    
    if not new_token:
        raise AuthenticationError("Token inválido o expirado. No se puede renovar.")
    
    # Calcular tiempo de expiración en segundos
    expires_in = settings.JWT_EXPIRATION_MINUTES * 60
    
    return TokenRefreshResponse(
        access_token=new_token,
        token_type="bearer",
        expires_in=expires_in
    )

