"""
Modelo de Usuario para la base de datos.
Define la estructura de la tabla de usuarios.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base


class User(Base):
    """Modelo de Usuario en la base de datos."""
    
    __tablename__ = "users"
    
    # ID único del usuario
    id = Column(Integer, primary_key=True, index=True)
    
    # Nombre de usuario (único)
    username = Column(String(100), unique=True, index=True, nullable=False)
    
    # Contraseña (debe estar hasheada)
    password_hash = Column(String(255), nullable=False)
    
    # ID del rol del usuario (foreign key a roles)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    
    # Fecha de creación
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Fecha de última actualización
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación con el rol
    role_obj = relationship("Role", back_populates="users")
    
    @property
    def role(self) -> str:
        """
        Propiedad para obtener el nombre del rol (compatibilidad hacia atrás).
        
        Returns:
            Nombre del rol
        """
        return self.role_obj.name if self.role_obj else None

