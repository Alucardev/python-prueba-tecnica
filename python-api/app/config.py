"""
Configuración de la aplicación.
Maneja variables de entorno y configuraciones globales.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from urllib.parse import quote_plus


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic Settings."""
    
    # Configuración JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tu-clave-secreta-super-segura-cambiar-en-produccion")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    
    # Configuración AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "mi-bucket-csv-files")
    
    # Configuración SQL Server
    SQL_SERVER_HOST: str = os.getenv("SQL_SERVER_HOST", "localhost")
    SQL_SERVER_PORT: int = int(os.getenv("SQL_SERVER_PORT", "1433"))
    SQL_SERVER_DATABASE: str = os.getenv("SQL_SERVER_DATABASE", "prueba_tecnica")
    SQL_SERVER_USER: str = os.getenv("SQL_SERVER_USER", "sa")
    SQL_SERVER_PASSWORD: str = os.getenv("SQL_SERVER_PASSWORD", "")
    SQL_SERVER_DRIVER: str = os.getenv("SQL_SERVER_DRIVER", "ODBC Driver 17 for SQL Server")
    
    # Configuración de roles permitidos
    ALLOWED_ROLES_FOR_FILE_UPLOAD: list = ["admin", "uploader"]
    
    @property
    def DATABASE_URL(self) -> str:
        """
        Construye la URL de conexión a la base de datos SQL Server.
        
        Returns:
            URL de conexión formateada para SQLAlchemy
        """
        # Codificar la contraseña para URL (por si contiene caracteres especiales)
        encoded_password = quote_plus(self.SQL_SERVER_PASSWORD)
        encoded_driver = quote_plus(self.SQL_SERVER_DRIVER)
        
        # Construir la URL de conexión
        # Para ODBC Driver 18, agregar TrustServerCertificate=yes para certificados self-signed
        trust_cert = "TrustServerCertificate=yes" if "18" in self.SQL_SERVER_DRIVER else ""
        connection_params = f"driver={encoded_driver}"
        if trust_cert:
            connection_params += f"&{trust_cert}"
        
        return (
            f"mssql+pyodbc://{self.SQL_SERVER_USER}:{encoded_password}"
            f"@{self.SQL_SERVER_HOST}:{self.SQL_SERVER_PORT}/{self.SQL_SERVER_DATABASE}"
            f"?{connection_params}"
        )
    
    @property
    def JWT_SECRET_KEY(self) -> str:
        """
        Alias para SECRET_KEY para mantener compatibilidad con el código existente.
        
        Returns:
            Clave secreta para JWT
        """
        return self.SECRET_KEY
    
    @property
    def JWT_EXPIRATION_MINUTES(self) -> int:
        """
        Alias para ACCESS_TOKEN_EXPIRE_MINUTES para mantener compatibilidad.
        
        Returns:
            Minutos de expiración del token
        """
        return self.ACCESS_TOKEN_EXPIRE_MINUTES
    
    class Config:
        """Configuración de Pydantic."""
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()

