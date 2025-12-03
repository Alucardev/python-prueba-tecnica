"""
Modelos del módulo de autenticación (usuarios y roles).
"""
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.models import Base


class RoleEnum(str, Enum):
    """Enumeración de roles soportados (para compatibilidad con tests)."""

    ADMIN = "admin"
    UPLOADER = "uploader"
    USER = "user"

class Role(Base):
    """Modelo de Rol en la base de datos."""

    __tablename__ = "roles"

    # ID único del rol
    id = Column(Integer, primary_key=True, index=True)

    # Nombre del rol (único)
    name = Column(String(50), unique=True, index=True, nullable=False)

    # Descripción del rol
    description = Column(String(255), nullable=True)

    # Relación con usuarios
    users = relationship("User", back_populates="role_obj")


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
    role_obj = relationship(Role, back_populates="users")

    # Propiedad para obtener el rol como string (compatibilidad)
    @property
    def role(self) -> str:
        """
        Propiedad para obtener el nombre del rol como string.

        Returns:
            Nombre del rol (admin/uploader/user) o "user" por defecto
        """
        if self.role_obj and self.role_obj.name:
            return self.role_obj.name.lower()
        return "user"


__all__ = ["User", "Role", "RoleEnum"]

