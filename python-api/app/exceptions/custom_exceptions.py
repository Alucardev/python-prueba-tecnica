"""
Excepciones personalizadas de la aplicación.
Define excepciones específicas para diferentes tipos de errores.
"""
from fastapi import status


class BaseAppException(Exception):
    """Excepción base para todas las excepciones de la aplicación."""
    
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        """
        Inicializa la excepción base.
        
        Args:
            message: Mensaje de error
            status_code: Código de estado HTTP
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(BaseAppException):
    """Excepción para errores de autenticación."""
    
    def __init__(self, message: str = "Credenciales inválidas"):
        """
        Inicializa la excepción de autenticación.
        
        Args:
            message: Mensaje de error
        """
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(BaseAppException):
    """Excepción para errores de autorización."""
    
    def __init__(self, message: str = "Acceso denegado"):
        """
        Inicializa la excepción de autorización.
        
        Args:
            message: Mensaje de error
        """
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ValidationError(BaseAppException):
    """Excepción para errores de validación."""
    
    def __init__(self, message: str):
        """
        Inicializa la excepción de validación.
        
        Args:
            message: Mensaje de error
        """
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class NotFoundError(BaseAppException):
    """Excepción para recursos no encontrados."""
    
    def __init__(self, message: str = "Recurso no encontrado"):
        """
        Inicializa la excepción de recurso no encontrado.
        
        Args:
            message: Mensaje de error
        """
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class BusinessLogicError(BaseAppException):
    """Excepción para errores de lógica de negocio."""
    
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        """
        Inicializa la excepción de lógica de negocio.
        
        Args:
            message: Mensaje de error
            status_code: Código de estado HTTP (default: 400)
        """
        super().__init__(message, status_code)


class ExternalServiceError(BaseAppException):
    """Excepción para errores de servicios externos (S3, etc.)."""
    
    def __init__(self, message: str, service: str = "servicio externo"):
        """
        Inicializa la excepción de servicio externo.
        
        Args:
            message: Mensaje de error
            service: Nombre del servicio externo
        """
        full_message = f"Error en {service}: {message}"
        super().__init__(full_message, status.HTTP_502_BAD_GATEWAY)


class DatabaseError(BaseAppException):
    """Excepción para errores de base de datos."""
    
    def __init__(self, message: str = "Error en la base de datos"):
        """
        Inicializa la excepción de base de datos.
        
        Args:
            message: Mensaje de error
        """
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)

