"""
Repositorio de Roles.
Maneja todas las operaciones de base de datos relacionadas con roles.
"""
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.role import Role
from typing import Optional, List


class RoleRepository:
    """Repositorio para operaciones de roles."""
    
    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesión de base de datos.
        
        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db
    
    def get_by_name(self, name: str) -> Optional[Role]:
        """
        Obtiene un rol por su nombre.
        
        Args:
            name: Nombre del rol
            
        Returns:
            Rol encontrado o None
        """
        stmt = select(Role).where(Role.name == name)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_id(self, role_id: int) -> Optional[Role]:
        """
        Obtiene un rol por su ID.
        
        Args:
            role_id: ID del rol
            
        Returns:
            Rol encontrado o None
        """
        stmt = select(Role).where(Role.id == role_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_all(self) -> List[Role]:
        """
        Obtiene todos los roles.
        
        Returns:
            Lista de todos los roles
        """
        stmt = select(Role)
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def create_role(self, name: str, description: Optional[str] = None) -> Role:
        """
        Crea un nuevo rol en la base de datos.
        
        Args:
            name: Nombre del rol
            description: Descripción del rol (opcional)
            
        Returns:
            Rol creado
        """
        new_role = Role(
            name=name,
            description=description
        )
        self.db.add(new_role)
        self.db.commit()
        self.db.refresh(new_role)
        return new_role

