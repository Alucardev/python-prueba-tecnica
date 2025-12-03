"""
Modelo de Rol para la base de datos.
Define la estructura de la tabla de roles.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base


class Role(Base):
    """Modelo de Rol en la base de datos."""
    
    __tablename__ = "roles"
    
    # ID único del rol
    id = Column(Integer, primary_key=True, index=True)
    
    # Nombre del rol (único)
    name = Column(String(50), unique=True, index=True, nullable=False)
    
    # Descripción del rol
    description = Column(String(255), nullable=True)
    
    # Fecha de creación
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Fecha de última actualización
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación con usuarios
    users = relationship("User", back_populates="role_obj")

