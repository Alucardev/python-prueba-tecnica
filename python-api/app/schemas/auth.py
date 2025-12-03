"""
Esquemas Pydantic para autenticación.
Define los modelos de datos para requests y responses de autenticación.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Esquema para el request de inicio de sesión."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Esquema para la respuesta del token JWT."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # Tiempo de expiración en segundos


class TokenData(BaseModel):
    """Datos contenidos en el token JWT."""
    id_usuario: int
    rol: str
    exp: Optional[datetime] = None


class TokenRefreshRequest(BaseModel):
    """Esquema para el request de renovación de token."""
    access_token: str


class TokenRefreshResponse(BaseModel):
    """Esquema para la respuesta de renovación de token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

