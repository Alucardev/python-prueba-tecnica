"""
Repositorio de Usuario.
Maneja todas las operaciones de base de datos relacionadas con usuarios.
"""
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.models.role import Role
from passlib.context import CryptContext
import bcrypt
from typing import Optional

# Contexto para hashing de contraseñas
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception:
    # Fallback si hay problemas con passlib
    pwd_context = None


class UserRepository:
    """Repositorio para operaciones de usuario."""
    
    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesión de base de datos.
        
        Args:
            db: Sesión de SQLAlchemy
        """
        self.db = db
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Obtiene un usuario por su nombre de usuario.
        
        Args:
            username: Nombre de usuario a buscar
            
        Returns:
            Usuario encontrado o None
        """
        stmt = select(User).where(User.username == username)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Usuario encontrado o None
        """
        stmt = select(User).where(User.id == user_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña en texto plano coincide con el hash.
        
        Args:
            plain_password: Contraseña en texto plano
            hashed_password: Contraseña hasheada
            
        Returns:
            True si coinciden, False en caso contrario
        """
        if pwd_context:
            try:
                return pwd_context.verify(plain_password, hashed_password)
            except Exception:
                pass
        # Fallback a bcrypt directo
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    def hash_password(self, password: str) -> str:
        """
        Genera un hash de la contraseña.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Contraseña hasheada
        """
        if pwd_context:
            try:
                return pwd_context.hash(password)
            except Exception:
                pass
        # Fallback a bcrypt directo
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def create_user(self, username: str, password: str, role_name: str = "user") -> User:
        """
        Crea un nuevo usuario en la base de datos.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano (se hasheará)
            role_name: Nombre del rol del usuario (default: "user")
            
        Returns:
            Usuario creado
        """
        # Obtener el rol por nombre
        role = self.db.execute(select(Role).where(Role.name == role_name)).scalar_one_or_none()
        if not role:
            raise ValueError(f"Rol '{role_name}' no encontrado")
        
        hashed_password = self.hash_password(password)
        new_user = User(
            username=username,
            password_hash=hashed_password,
            role_id=role.id
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

